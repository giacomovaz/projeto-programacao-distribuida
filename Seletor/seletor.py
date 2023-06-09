from database import Database
from sqlite3 import IntegrityError
import json
from transacao import Transacao, Cliente
import random as rnd
import requests as req
from datetime import datetime, timedelta
from time import sleep

# definir IP do Gerenciador
HOST_GERENCIADOR = "http://127.0.0.2:5000"

HTTP = "http://"

SERVICE_TRANSACAO = "/transactions"
SERVICE_CLIENTE = "/cliente"
SERVICE_HORA = "/hora"
SERVICE_VALIDADOR_VALIDA = "/transacao/validar"
SERVICE_PING = "/ping"

class Validador:
    id: int
    qtd_moeda: int
    qtd_flags: int
    ip: str
    qtd_transacao_correta: int
    chave: str
    
    chance_escolha: float

    def __init__(self, id:int=0, qtd_moeda:int=0, qtd_flags:int=0, ip:str="0.0.0.0", qtd_transacao_correta:int=0, chave=""):
        self.id = id
        self.qtd_moeda = qtd_moeda
        self.qtd_flags = qtd_flags
        self.ip = ip
        self.qtd_transacao_correta = qtd_transacao_correta
        self.chave = chave

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def cadastraDb(self):
        db = Database()
        query = "INSERT INTO VALIDADORES (id, qtd_moeda, qtd_flags, ip, qtd_transacao_correta, chave) VALUES (?, ?, ?, ?, ?, ?)"
        param = [self.id, self.qtd_moeda, self.qtd_flags, self.ip, self.qtd_transacao_correta, self.chave]
        db.execute(query, param)
        db.save()

    def excluirDb(self):
        db = Database()
        query = "DELETE FROM VALIDADORES WHERE id = ?"
        param = [self.id]
        db.execute(query, param)
        db.save()

    def editarDb(self, campo:str):
        db = Database()
        query = "UPDATE VALIDADORES SET "
        param = []

        if campo == "qtd_moeda":
            query = query + "qtd_moeda = ?"
            param = [self.qtd_moeda]
        elif campo == "qtd_flags":
            query = query + "qtd_flags = ?"
            param = [self.qtd_flags]
        elif campo == "qtd_transacao_correta":
            query = query + "qtd_transacao_correta = ?"
            param = [self.qtd_transacao_correta]
        else:
            raise Exception("Campo nao alteravel")
        
        query = query + "WHERE id = ?"
        param.append(self.id)
        
        db.execute(query, param)
        db.save()
        
    @staticmethod
    def buscarUmDb(id:int):
        db = Database()
        query = "SELECT * FROM VALIDADORES WHERE id = ?"
        param = [id]
        # pegar o unico retorno dessa busca
        ret = db.execute(query, param).fetchone()
            
        return Validador(id=ret[0], qtd_moeda=ret[1], qtd_flags=ret[2], ip=ret[3], qtd_transacao_correta=ret[4], chave=ret[5])
    
    # verificando se a instancia esta de pe
    def isAtivo(self):
        try:
            url = HTTP + self.ip + SERVICE_PING
            ret = req.get(url=url)
            if ret.status_code == 200:
                return True
            else:
                print(f'Validador {self.ip} nao inicializado')
                return False
        except Exception as e:
            print(str(e))
            return False
    
    def enviarTransacao(self, transacao:Transacao, ultima_transacao:Transacao, horario_atual:datetime):        
        transacao.ip_validacao.append(self.ip)
        data = {
            'id': transacao.id,
            'valor': transacao.valor,
            'trans_rem': transacao.remetente.qtdTransacoesUltimoSegudo(horario_atual=horario_atual),
            'horario_trans': transacao.horario,
            'horario_ult_trans': ultima_transacao.horario,
            'conta_rem': transacao.remetente.qtd_moeda,
            'id_rem' : transacao.remetente.id,
            'horario_atual' : horario_atual
        }
        url = HTTP + self.ip + SERVICE_VALIDADOR_VALIDA
        req.post(url=url, data=data)
        
    def acrescentarFlag(self):
        self.qtd_flags = self.qtd_flags + 1
        self.editarDb("qtd_flags")
        
    def decrescentarFlag(self):
        if self.qtd_flags > 0:
            self.qtd_flags = self.qtd_flags - 1
            self.editarDb("qtd_flags")
        
    def acrescentarTransacaoCorreta(self):
        self.qtd_transacao_correta = self.qtd_transacao_correta + 1
        self.editarDb("qtd_transacao_correta")
        
    def acrescentarMoeda(self, qtd_moeda):
        self.qtd_moeda = self.qtd_moeda + qtd_moeda
        self.editarDb("qtd_moeda")


class Seletor:
    total_moedas:int
    validadores:list[Validador] = []
    transacoes:list[Transacao] = []
    
    def __init__(self):
        self.buscarValidadores()
        self.buscarTotalMoedas()
    
    def buscarTransacao(self, i:int):
        for t in self.transacoes:
            if t.id == i:
                return t
        return None
    
    def removerTransacao(self, i:int=0, transacao:Transacao=None):
        if transacao == None:
            for t in self.transacoes:
                if t.id == i:
                    self.transacoes.remove(t)
                    return True
            return False
        self.transacoes.remove(transacao)
    
    def buscarValidador(self, id:int=None, ip:str=None):
        if id != None:
            for v in self.validadores:
                if v.id == id:
                    return v
            return None
        if ip != None:
            for v in self.validadores:
                if v.ip == ip:
                    return v
            return None
            
    
    def isValidadorIpCadastrado(self, ip:str):
        v = self.buscarValidador(ip=ip)
        return v != None
    
    def buscarValidadores(self):
        db = Database()
        query = "SELECT id FROM VALIDADORES"
        
        ids = db.execute(query=query).fetchall()
        if ids != []:
            for i in ids:
                validador = Validador.buscarUmDb(i[0])
                self.validadores.append(validador)
        
    
    def buscarTotalMoedas(self):
        db = Database()
        query = "SELECT total_moedas FROM SELETOR"
        ret = db.execute(query=query).fetchone()
        
        if ret == None:
            self.inicializarTotalMoedas()
        else:
            self.total_moedas = ret[0]
            
    def inicializarTotalMoedas(self):
        db = Database()
        query = "INSERT INTO SELETOR VALUES(0)"
        db.execute(query=query)
        db.save()
        self.total_moedas = 0
    
    def atualizarTotalMoedasDb(self):
        db = Database()
        query = "UPDATE SELETOR SET total_moedas = ?"
        param = [self.total_moedas]
        db.execute(query=query, param=param)
        db.save()
        
    def ultimoIdCadastrado(self):
        db = Database()
        ret = db.execute("SELECT id FROM VALIDADORES ORDER BY id DESC LIMIT 1").fetchone()
        if ret == None:
            return 0
        else:
            return ret[0]
    
    def novoValidador(self, qtdMoeda:int, ip:str):
        id = self.ultimoIdCadastrado() + 1
        chave_segura = f'chave_segura{id}'
        validador = Validador(id=id, qtd_moeda=qtdMoeda, qtd_flags=0,ip=ip, chave=chave_segura)
        try:
            validador.cadastraDb()
        except IntegrityError:
            raise Exception("IP ja cadastrado")
        self.validadores.append(validador)
        return validador
                
    def validarChave(self, ip, chave):
        if self.buscarValidador(ip=ip).chave != chave:
            raise Exception("Chave incorreta")            
    
    def buscarValidadoresAtivos(self) -> list[Validador]:
        if len(self.validadores) == 0:
            return []
        validadores_ativos = []
        for v in self.validadores:
            if v.isAtivo():
                validadores_ativos.append(v)
        return validadores_ativos

    def enviarTransacaoValidadores(self, transacao:Transacao):
        ult_trans = Transacao.buscarUltima()
        transacao.cadastraDb()
        qtd_ativos = 0
        horario_atual = self.horarioAtualGerenciador()
        tempo_tentando = horario_atual + timedelta(seconds=60)
        
        # tenta buscar pelo menos 3 validadores ativos por 1min
        while qtd_ativos < 3 and tempo_tentando > horario_atual:
            validadores_ativos = self.buscarValidadoresAtivos()
            qtd_ativos = len(validadores_ativos)
            if qtd_ativos < 3:
                sleep(5)
                horario_atual = self.horarioAtualGerenciador()
        
        if qtd_ativos < 3:
            raise Exception("Quantidade insuficiente de validadores")
        
        definindoChancesValidadores(validadores_ativos)
        remetente = self.buscarCliente(transacao.remetente.id)
        remetente.tipo = "rem"
        transacao.remetente = remetente
        horario_atual = self.horarioAtualGerenciador()
        # garantindo que essa lista estara vazia
        transacao.lista_validacao = {}
        if qtd_ativos in (3, 5):
            # definindo quanto validadores irao validar
            transacao.qtd_validando = qtd_ativos
            for v in self.validadores:
                v.enviarTransacao(transacao=transacao, ultima_transacao=ult_trans, horario_atual=horario_atual)
        elif qtd_ativos < 5:
            # definindo quanto validadores irao validar
            transacao.qtd_validando = 3
            for _ in range(3):
                v = rnd.choices(population=validadores_ativos, weights=listaChances(validadores_ativos))
                v[0].enviarTransacao(transacao=transacao, ultima_transacao=ult_trans, horario_atual=horario_atual)
                validadores_ativos.remove(v[0])
        else:
            # definindo quanto validadores irao validar
            transacao.qtd_validando = 5
            for _ in range(5):
                v = rnd.choices(population=validadores_ativos, weights=listaChances(validadores_ativos))
                v[0].enviarTransacao(transacao=transacao, ultima_transacao=ult_trans, horario_atual=horario_atual)
                validadores_ativos.remove(v[0])
        
    def distribuirGanhos(self, qtd_moeda, transacao:Transacao):
        porcentagem_seletor = 0.5
        porcentagem_validadores = 0.5
        
        self.total_moedas = self.total_moedas + round(qtd_moeda*porcentagem_seletor)
        self.atualizarTotalMoedasDb()
        
        moedas_distribuidas = round(qtd_moeda*porcentagem_validadores)
        for ip in transacao.ip_corretos:
            v = self.buscarValidador(ip=ip)
            v.acrescentarMoeda(round(moedas_distribuidas/transacao.qtd_validando))
        
    def validarTransacao(self, transacao:Transacao):
        transacao.validarTransacao()
        for ip in transacao.ip_incorretos:
            v = self.buscarValidador(ip=ip)
            v.acrescentarFlag()
            if v.qtd_flags >= 3:
                self.removerValidador(validador=v, is_excluido_por_flags=True)
        for ip in transacao.ip_corretos:
            v = self.buscarValidador(ip=ip)
            v.acrescentarTransacaoCorreta()
            # se for divisivel por 10000, alcancou a marca de mais 
            # 10000 transacoes corretas, portanto diminui em 1 as flags
            if v.qtd_transacao_correta % 10000 == 0:
                v.decrescentarFlag()
                
        self.distribuirGanhos(qtd_moeda=60, transacao=transacao)
            
    # alterando a transacao diretamente, pois nao achamos um servico
    # que pudesse receber o status para alterar la
    def alterarTransacao(self, transacao:Transacao):
        url = HOST_GERENCIADOR + SERVICE_TRANSACAO + "/" + str(transacao.id) + "/" + str(transacao.status)
        req.post(url=url)
            
    def buscarCliente(self, id:int):
        
        url = HOST_GERENCIADOR + SERVICE_CLIENTE + "/" + str(id)
        ret = req.get(url=url).json()
        
        cliente = Cliente()
        cliente.preencherCliente(ret)
        return cliente
    
    def removerValidador(self, validador:Validador, is_excluido_por_flags:bool=False):
        if is_excluido_por_flags:
            self.total_moedas = self.total_moedas + validador.qtd_moeda
            self.atualizarTotalMoedasDb()
        self.validadores.remove(validador)
        validador.excluirDb()
        
    def horarioAtualGerenciador(self):
        url = HOST_GERENCIADOR + SERVICE_HORA

        formato = "%Y-%m-%d %H:%M:%S.%f"
        ret = req.get(url=url).json()
        dt = datetime.strptime(ret, formato)
        return dt
        

# chamadas aqui em baixo por estarmos usando lista 
# que nao vem do self do Seletor
def totalMoedaEntreValidadores(validadores:list[Validador]):
    total_moeda = 0
    for v in validadores:
        total_moeda = total_moeda + v.qtd_moeda
    return total_moeda

def definindoChancesValidadores(validadores:list[Validador]):
    total_moeda = totalMoedaEntreValidadores(validadores)
    for v in validadores:
        chance = v.qtd_moeda/total_moeda
        if chance > 0.40:
            v.chance_escolha = 0.40
        elif chance < 0.05:
            v.chance_escolha = 0.05
        else:
            v.chance_escolha = chance
            
# lista das chances dos validadores
def listaChances(validadores:list[Validador]):
    chances = []
    for v in validadores:
        chances.append(v.chance_escolha)
    return chances

from database import Database
from sqlite3 import IntegrityError
import json
from transacao import Transacao, Cliente
import random as rnd
import requests as req

# definir IP do Gerenciador
HOST_GERENCIADOR = "http://127.0.0.2:5000"

SERVICE_TRANSACAO = "/transactions"
SERVICE_CLIENTE = "/cliente"

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
        param = 0

        if campo == "qtd_moedas":
            query = query + "qtd_moedas = ?"
            param = [self.qtd_moeda]
        elif campo == "qtd_flags":
            query = query + "qtd_flags = ?"
            param = [self.qtd_flags]
        elif campo == "qtd_transacao_correta":
            query = query + "qtd_transacao_correta = ?"
            param = [self.qtd_transacao_correta]
        else:
            raise Exception("Campo nao alteravel")
        
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
    
    def isAtivo(self):
        # TODO FAZER LOGICA DE VERIFICAR SE ESTA ATIVO
        return True
    
    def enviarTransacao(self, transacao:Transacao):
        # TODO ENVIAR TRANSACAO PARA OS VALIDADORES
        transacao.ip_validacao.append(self.ip)
        print(f'qtd_transacao remetente: {transacao.remetente.qtdTransacoesUltimoSegudo()}')
        # print(self.toJson())
        
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
    
    def removerTransacao(self, i:int, transacao:Transacao=None):
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
    
    def atualizarTotalMoedas(self, moedas:int):
        db = Database()
        query = "UPDATE SELETOR SET total_moedas = ?"
        param = [moedas]
        db.execute(query=query, param=param)
        db.save()
        self.total_moedas = moedas
        
    def quantidadeValidadores(self):
        return len(self.validadores)
    
    def novoValidador(self, qtdMoeda:int, ip:str):
        qtd_validadores = self.quantidadeValidadores()
        chave_segura = f'chave_segura{qtd_validadores}'
        validador = Validador(id=qtd_validadores, qtd_moeda=qtdMoeda, qtd_flags=0,ip=ip, chave=chave_segura)
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
        transacao.cadastraDb()
        validadores_ativos = self.buscarValidadoresAtivos()
        qtd_ativos = len(validadores_ativos)
        if qtd_ativos < 3:
            raise Exception("Quantidade insuficiente de validadores")
        
        definindoChancesValidadores(validadores_ativos)
        if qtd_ativos in (3, 5):
            for v in self.validadores:
                v.enviarTransacao(transacao=transacao)
            transacao.qtd_validando = qtd_ativos
        elif qtd_ativos < 5:
            for _ in range(3):
                v = rnd.choices(population=validadores_ativos, weights=listaChances(validadores_ativos))
                v[0].enviarTransacao(transacao=transacao)
                validadores_ativos.remove(v[0])
            transacao.qtd_validando = 3
        else:
            for _ in range(5):
                v = rnd.choices(population=validadores_ativos, weights=listaChances(validadores_ativos))
                v[0].enviarTransacao(transacao=transacao)
                validadores_ativos.remove(v[0])
            transacao.qtd_validando = 5
        
    def validarTransacao(self, transacao:Transacao):
        transacao.validarTransacao()
        print(transacao.status)
        
        for ip in transacao.ip_incorretos:
            v = self.buscarValidador(ip=ip)
            v.acrescentarFlag()
        for ip in transacao.ip_corretos:
            v = self.buscarValidador(ip=ip)
            v.acrescentarTransacaoCorreta()
            # se for divisivel por 10000, alcancou a marca de mais 
            # 10000 transacoes corretas, portanto diminui em 1 as flags
            if v.qtd_transacao_correta % 10000 == 0:
                v.decrescentarFlag()
            
    def alterarTransacao(self, transacao:Transacao):
        url = HOST_GERENCIADOR + SERVICE_TRANSACAO + "/" + str(transacao.id) + "/" + str(transacao.status)
        req.post(url=url)
            
    def buscarCliente(self, id:int):
        
        url = HOST_GERENCIADOR + SERVICE_CLIENTE + "/" + str(id)
        ret = req.get(url=url).json()
        
        cliente = Cliente()
        cliente.preencherCliente(ret)
        print(cliente.toJson())
        return cliente


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
            
def listaChances(validadores:list[Validador]):
    chances = []
    for v in validadores:
        chances.append(v.chance_escolha)
    return chances
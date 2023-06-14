from datetime import datetime, timedelta
import json
from database import Database

TIPO_REMETENTE = "rem"
TIPO_RECEBEDOR = "reb"

class Cliente:
    
    id: int
    nome: str
    qtd_moeda: int
    senha: str
    # define se o cliente eh remetente ou recebedor
    tipo: str
    
    
    def __init__(self, id=0, nome="", qtd_moeda=0, senha="", tipo=""):
        self.id = id
        self.nome = nome
        self.qtd_moeda = qtd_moeda
        self.senha = senha
        self.tipo = tipo
        
    def preencherCliente(self, json):
        self.id = json["id"]
        self.nome = json["nome"]
        self.qtd_moeda = json["qtdMoeda"]
        self.senha = json["senha"]
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    def qtdTransacoesUltimoSegudo(self):
        db = Database()
        sql = f"SELECT COUNT(*) FROM TRANSACOES WHERE id_{self.tipo} = ? AND horario <= ? AND horario > ?"
        horario_atual = datetime.now()
        horario_ultimo_segundo = horario_atual - timedelta(seconds=1)
        val = [1, horario_atual, horario_ultimo_segundo]
        ret = db.execute(sql, val).fetchone()[0]
        return ret

class Transacao:
    id: int
    remetente: Cliente
    recebedor: Cliente
    valor: int
    status: int
    horario: datetime
    
    qtd_validando: int = 0
    qtd_validado: int = 0
    ip_validacao: list = []
    lista_validacao: dict = {}
    ip_incorretos:list
    ip_corretos:list
    
    def __init__(self, id, rem, reb, valor, status, horario):
        self.id = id
        self.remetente = Cliente(id=rem, tipo=TIPO_REMETENTE)
        self.recebedor = Cliente(id=reb, tipo=TIPO_RECEBEDOR)
        self.valor = valor
        self.status = status
        self.horario = horario
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    # ip valido para realizar a validacao da transacao
    def isIpValido(self, ip):
        return ip in self.ip_validacao
    
    def cadastraDb(self):
        db = Database()
        query = "INSERT INTO TRANSACOES (id, id_rem, id_reb, horario) VALUES (?, ?, ?, ?)"
        param = [self.id, self.remetente.id, self.recebedor.id, self.horario]
        db.execute(query, param)
        db.save()
        
    def adicionarValidacao(self, ip, status):
        if self.isIpValido(ip=ip):
            self.qtd_validado = self.qtd_validado + 1
            self.lista_validacao.update({ip: status})
        else:
            raise Exception("IP invalido")
        
    def validarTransacao(self):
        validaram = {} 
        invalidaram = {}
        for ip, status in self.lista_validacao.items():
            if status == 1:
                validaram.update({ip: status})
            else:
                invalidaram.update({ip: status})
                
        if len(validaram) > len(invalidaram):
            self.status = 1
            self.ip_corretos = list(validaram.keys())
            self.ip_incorretos = list(invalidaram.keys())
        else:
            self.status = 2
            self.ip_corretos = list(invalidaram.keys())
            self.ip_incorretos = list(validaram.keys())
        
    def isTransacaoProntaValidar(self):
        # se todos os validadores ja tiverem enviado suas respostas
        return self.qtd_validado == self.qtd_validando
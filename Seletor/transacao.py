from datetime import datetime
import json

class Transacao:
    id: int
    remetente: int
    recebedor: int
    valor: int
    status: int
    horario: datetime
    
    qtd_validando: int = 0
    qtd_validado: int = 0
    ip_validacao: list = []
    lista_validacao: dict = {}
    
    def __init__(self, id, rem, reb, valor, status, horario):
        self.id = id
        self.remetente = rem
        self.recebedor = reb
        self.valor = valor
        self.status = status
        self.horario = horario
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    def isIpValido(self, ip):
        return ip in self.ip_validacao
        
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
            # TODO ADICIONAR FLAG NOS QUE INVALIDARAM
        else:
            self.status = 2
            # TODO ADICIONAR FLAG NOS QUE VALIDARAM
        
    def isTransacaoVerificada(self):
        # se todos os validadores ja tiverem enviado suas respostas
        if self.qtd_validado == self.qtd_validando:
            self.validarTransacao()
            return True
        else:
            return False
from datetime import datetime

class Transacao:
    id: int
    remetente: int
    recebedor: int
    valor: int
    status: int
    horario: datetime
    
    
    def __init__(self, id=0, rem=0, reb=0, valor=0, status=0, horario=None):
        self.id = id
        self.remetente = rem
        self.recebedor = reb
        self.valor = valor
        self.status = status
        self.horario = horario
        
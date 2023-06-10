from datetime import datetime
import json

class Transacao:
    id: int
    remetente: int
    recebedor: int
    valor: int
    status: int
    horario: datetime
    
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
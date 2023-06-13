from database import Database
from sqlite3 import IntegrityError
import json
from Seletor.seletor import Validador
from Seletor.transacao import Transacao
from datetime import datetime


class Validador:
    id: int
    valor_transacao: float
    valor_conta_rem: float
    horario: datetime
    horario_ultima_trans: datetime
    qtde_trans: int

    def __init__(self, id, valor_transacao, valor_conta_rem, horario, horario_ultima_trans, qtde_trans):
        self.id = id
        self.valor_transacao = valor_transacao
        self.valor_conta_rem = valor_conta_rem
        self.horario = horario
        self.horario_ultima_trans = horario_ultima_trans # do remetente
        self.qtde_trans = qtde_trans                     # do remetente

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def valida_transacao(self, transacao: Transacao):

        # Validar saldo do remetente
        if self.valor_conta_rem >= transacao.valor:
            # Validar horário da transação
            horario_atual = datetime.now()
            if self.horario_ultima_trans < transacao.horario <= horario_atual:
                # Verificar limite de transações por segundo
                if self.qtde_trans < 1000:
                    # Verificar chave única
                    if transacao.id == self.id:
                        return 1  # transacao concluida
                    else:
                        return 2  # id não corresponde
                else:
                    # adicionar o bloqueio de 1 min
                    return 0  # Mais de 1000 transacoes por segundo
            else:
                return 2  # Horario menor que da ultima transacao e maior que hora atual
        else:
            return 2  # saldo insuficiente


from database import Database
import json
from transacao import Transacao
from datetime import datetime, time

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


    # TODO
    #  - Seletor irá enviar o qtd Moedas que o cliente remetente
    #    possui em sua conta
    def valida_transacao(self, transacao: Transacao):

        # Validar saldo do remetente
        if self.valor_conta_rem >= transacao.valor:
            # Validar horário da transação
            horario_atual = datetime.now()
            if self.horario_ultima_trans < transacao.horario <= horario_atual:
                # Verificar limite de transações por segundo
                self.qtde_trans = self.qtde_trans_rem(transacao.remetente)
                if self.qtde_trans < 1000:
                    # Verificar chave única
                    if transacao.id == self.id:
                        return 1  # transacao concluida
                    else:
                        return 2  # id não corresponde
                else:
                    proximo_minuto = time.time() + 60
                    if proximo_minuto > time.time(): #blolqueio de 1 min
                        return 0  # Mais de 1000 transacoes por segundo
            else:
                return 2  # Horario menor que da ultima transacao e maior que hora atual
        else:
            return 2  # saldo insuficiente


    # TODO
    #  - Seletor vai enviar a quantidade de transacoes, validador
    #    não precisará ter acesso ao banco de dados para isso
    def qtde_trans_rem(self, id_rem):
        id = id_rem
        db = Database() # banco do gerenciador
        # pegar a quantidade de transacoes do rementente no ultimo 1seg
        query = "SELECT COUNT(*) FROM transacao WHERE remetente = {0} AND horario > datetime('now', '-1 seconds')".format(id)
        ret = db.execute(query).fetchone()
        return ret[0]




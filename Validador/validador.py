from datetime import datetime
import time


# Definição da classe Validador
class Validador:
    # Declaração das propriedades da classe
    id: int
    valor_conta_rem: float
    horario_ultima_trans: datetime
    qtde_trans: int
    limite_transacoes: bool

    # Construtor da classe
    def __init__(self, id, valor_conta_rem, horario_ultima_trans, qtde_trans):
        # Inicialização das propriedades da classe com os valores passados
        self.id = id
        self.valor_conta_rem = valor_conta_rem
        self.horario_ultima_trans = horario_ultima_trans
        self.qtde_trans = qtde_trans
        self.limite_transacoes = False

    # Método para validar a transação
    def valida_transacao(self, transacao):
        # Obter o horário atual
        horario_atual = datetime.now()

        # Verificar se o valor na conta do remetente é maior ou igual ao valor da transação
        if self.valor_conta_rem >= transacao.valor:
            # Verificar se o horário da transação é depois do horário da última transação e antes ou no mesmo horário atual
            if self.horario_ultima_trans < transacao.horario <= horario_atual:
                # Verificar se a quantidade de transações é menor que 1000 e se o limite de transações não foi atingido
                if self.qtde_trans < 1000 and not self.limite_transacoes:
                    # Verificar se a id da transação é a mesma que a id do validador
                    if transacao.id == self.id:
                        # Incrementar a quantidade de transações
                        self.qtde_trans += 1
                        # Atualizar o horário da última transação
                        self.horario_ultima_trans = horario_atual
                        # Verificar se a quantidade de transações é agora maior ou igual a 1000
                        if self.qtde_trans >= 1000:
                            # Ativar o limite de transações
                            self.limite_transacoes = True
                            # Pausa de 60 segundos
                            time.sleep(60)
                            # Desativar o limite de transações
                            self.limite_transacoes = False
                            # Zerar a quantidade de transações
                            self.qtde_trans = 0
                        # Transação concluída
                        return 1
                    else:
                        # ID da transação não corresponde à ID do validador
                        return 2
                else:
                    # Mais de 1000 transações por segundo ou dentro do minuto
                    return 2
            else:
                # Horário da transação é menor que o da última transação ou maior que o horário atual
                return 2
        else:
            # Saldo insuficiente na conta do remetente
            return 2



from datetime import datetime
import requests
import json
from transacao import Transacao
import time

HOST_SELETOR = "http://127.0.0.1:5000"

# Definição da classe Validador
class Validador: 
    # Declaração das propriedades da classe
    ip: str
    chave: str    

    valor_conta_rem: int
    horario_ultima_trans: datetime
    qtde_trans: int
    limite_transacoes: bool = False

    # Construtor da classe
    def __init__(self, ip=0, chave=""):
        # Inicialização das propriedades da classe com os valores passados
        self.ip = ip
        self.chave = chave

    # Método para validar a transação
    def valida_transacao(self, transacao: Transacao):
        # Obter o horário atual
        horario_atual = datetime.now()

        # Verificar se o valor na conta do remetente é maior ou igual ao valor da transação
        if (self.valor_conta_rem >= transacao.valor) and (
            # Verificar se o horário da transação é depois do horário da última transação e antes ou no mesmo horário atual
            self.horario_ultima_trans < transacao.horario <= horario_atual) and (
            # Verificar se a quantidade de transações é menor que 1000
            self.qtde_trans < 1000):
            transacao.status = 1
        else:
            transacao.status = 2

    # Método para enviar a validação da transação ao seletor
    def enviar_validacao(self, transacao:Transacao):
        url = HOST_SELETOR + f"/transacao/{self.ip}/{transacao.id}/{transacao.status}/{self.chave}"
        response = requests.post(url)
        if response.status_code == 200:
            print("Validação enviada com sucesso.")
        else:
            print("Erro ao enviar a validação.")

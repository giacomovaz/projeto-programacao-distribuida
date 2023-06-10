from database import Database
from seletor import Seletor
from flask import Flask

def criaTabela():
    db = Database()
    query = [
        "CREATE TABLE VALIDADORES (id INTEGER PRIMARY KEY, qtd_moeda INTEGER, qtd_flags INTEGER, ip VARCHAR(15) UNIQUE)",
        "CREATE TABLE SELETOR (total_moedas INTEGER)"
    ]
    db.criarTabelas(query=query)
    
criaTabela()
seletor = Seletor()

app = Flask(__name__)
app.run()

    
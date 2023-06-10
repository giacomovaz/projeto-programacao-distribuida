from database import Database
from seletor import Seletor
from flask import Flask, render_template, request

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

def telaErro(mensagem:str):
    return render_template('erro.html', erro=mensagem)

@app.route('/validador/<int:qtdMoedas>/<string:ip>', methods=["POST"])
def cadastrarValidador(qtdMoedas, ip):
    if request.method == "POST":
        if qtdMoedas >= 100:
            try:
                validador = seletor.novoValidador(qtdMoedas, ip)
            except Exception as e:
                return telaErro(str(e))

            return validador.toJson()
        else:
            return telaErro("Quantidade de FCoins insuficiente")
    else:
        return telaErro("Metodo invalido")

@app.errorhandler(404)
def page_not_found():
    return render_template('page_not_found.html'), 404

app.run(debug=True)
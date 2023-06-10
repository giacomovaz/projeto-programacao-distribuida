from database import Database
from seletor import Seletor
from flask import Flask, render_template

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

@app.route('/validador/<int:qtdMoedas>/<string:ip>', methods=["POST"])
def cadastrarValidador(qtdMoedas, ip):
    validador = None
    try:
        validador = seletor.novoValidador(qtdMoedas, ip)
    except Exception as e:
        return render_template('erro.html', erro=str(e))

    return validador.toJson()

@app.errorhandler(404)
def page_not_found():
    return render_template('page_not_found.html'), 404

app.run(debug=True)
from database import Database
from seletor import Seletor
from transacao import Transacao
from flask import Flask, render_template, request
import requests as req

def criaTabela():
    db = Database()
    query = [
        "CREATE TABLE VALIDADORES (id INTEGER PRIMARY KEY, qtd_moeda INTEGER, qtd_flags INTEGER, ip VARCHAR(20) UNIQUE)",
        "CREATE TABLE SELETOR (total_moedas INTEGER)"
    ]
    db.criarTabelas(query=query)
    
criaTabela()
seletor = Seletor()
# definir IP do Gerenciador
HOST_GERENCIADOR = "http://127.0.0.2:5000"

app = Flask(__name__)

def telaErro(mensagem:str):
    return render_template('erro.html', erro=mensagem)

def telaSucesso(mensagem:str):
    return render_template('sucesso.html', sucesso=mensagem)

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

@app.route('/transacao/', methods=["POST"])
def transacao():
    transacao = Transacao(id=request.form["id"], rem=request.form["remetente"], reb=request.form["recebedor"],
                        valor=request.form["valor"], status=request.form["status"], horario=request.form["horario"])
    transacao.status = seletor.validarTransacao(transacao=transacao)
    url = HOST_GERENCIADOR + "/transactions" + "/" + str(transacao.id) + "/" + str(transacao.status)
    req.post(url=url)
    if transacao.status == 1:
        telaSucesso("Transacao valida")
    elif transacao.status == 2:
        telaErro("Transacao invalida")
    else:
        telaErro("Transacao nao processada")

@app.errorhandler(404)
def page_not_found():
    return render_template('page_not_found.html'), 404

app.run(host='127.0.0.1', debug=True)
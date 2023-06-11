from database import Database
from seletor import Seletor
from transacao import Transacao
from flask import Flask, render_template, request
import requests as req
from datetime import datetime

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

def mensagemErro(mensagem:str):
    return '{ erro:%s }' % mensagem

def mensagemSucesso(mensagem:str):
    return '{ sucesso:%s }' % mensagem

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
def enviaTransacao():
    if request.method == "POST":
        transacao = Transacao(id=int(request.form["id"]), rem=int(request.form["remetente"]), reb=int(request.form["recebedor"]),
                            valor=int(request.form["valor"]), status=int(request.form["status"]), horario=request.form["horario"])
        try:
            seletor.enviarTransacaoValidadores(transacao=transacao)
            seletor.transacoes.append(transacao) 
            print(len(seletor.transacoes))
            return mensagemSucesso("Inicio Validacao")
        except Exception as e:
            return mensagemErro(str(e))

    else:
        return mensagemErro("Metodo invalido")

@app.route('/transacao/<string:ip>/<int:id>/<int:status>', methods=["POST"])
def validarTransacao(ip, id, status):
    if request.method == "POST":
        try:
            transacao = seletor.buscarTransacao(i=id)
            if transacao == None:
                return mensagemErro("Transacao invalida")
            elif status not in (0, 1, 2):
                return mensagemErro("Status invalida")
            elif not seletor.isValidadorIpCadastrado(ip):
                return mensagemErro("IP nao cadastrado")
            
            transacao.adicionarValidacao(ip=ip, status=status)
            
            if transacao.isTransacaoProntaValidar():
                seletor.validarTransacao(transacao=transacao)
                
                url = HOST_GERENCIADOR + "/transactions" + "/" + str(transacao.id) + "/" + str(transacao.status)
                req.post(url=url)
                
                seletor.removerTransacao(id)
        except Exception as e:
            return mensagemErro(str(e))
    else:
        return telaErro("Metodo invalido")

    return mensagemSucesso("Validacao executada")

@app.errorhandler(404)
def page_not_found():
    return render_template('page_not_found.html'), 404

app.run(host='127.0.0.1', debug=True)
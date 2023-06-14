from database import Database
from seletor import Seletor
from transacao import Transacao
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from time import sleep

def criaTabela():
    db = Database()
    query = [
        "CREATE TABLE VALIDADORES (id INTEGER PRIMARY KEY, qtd_moeda INTEGER, qtd_flags INTEGER, ip VARCHAR(20) UNIQUE, qtd_transacao_correta INTEGER, chave VARCHAR(100))",
        "CREATE TABLE SELETOR (total_moedas INTEGER)",
        "CREATE TABLE TRANSACOES (id INTEGER PRIMARY KEY, id_rem INTEGER, id_reb INTEGER, horario DATETIME)"
    ]
    db.criarTabelas(query=query)
    
criaTabela()
seletor = Seletor()

app = Flask(__name__)

def telaErro(mensagem:str):
    return render_template('erro.html', erro=mensagem)

def telaSucesso(mensagem:str):
    return render_template('sucesso.html', sucesso=mensagem)

def mensagemErro(mensagem:str):
    print(f'erro: {mensagem}')
    return '{ erro: %s }' % mensagem

def mensagemSucesso(mensagem:str):
    print(f'sucesso: {mensagem}')
    return '{ sucesso: %s }' % mensagem


@app.route('/validador/<int:qtdMoedas>/<string:ip>', methods=["GET", "POST"])
def cadastrarValidador(qtdMoedas, ip):
    if request.method == "POST" or request.method == "GET":
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


@app.route('/validador/remover/<string:ip>/<string:chave>', methods=["DELETE"])
def removerValidador(ip, chave):
    if request.method == "DELETE":
        try:
            v = seletor.buscarValidador(ip=ip)
            if v == None:
                return mensagemErro("IP nao encontrado")
            
            seletor.validarChave(ip=ip, chave=chave)
            seletor.removerValidador(validador=v)
        except Exception as e:
            return mensagemErro(str(e))
    else:
        return mensagemErro("Metodo invalido")
    return mensagemSucesso("Validador removido")


# chamada feita pelo Gerenciador
@app.route('/transacao/', methods=["POST"])
def enviaTransacao():
    if request.method == "POST":
        transacao = Transacao(id=int(request.form["id"]), rem=int(request.form["remetente"]), reb=int(request.form["recebedor"]),
                            valor=int(request.form["valor"]), status=int(request.form["status"]), horario=request.form["horario"])
        try:
            seletor.enviarTransacaoValidadores(transacao=transacao)
            seletor.transacoes.append(transacao) 
            return mensagemSucesso("Inicio Validacao")
        except Exception as e:
            return mensagemErro(str(e))

    else:
        return mensagemErro("Metodo invalido")


# chamada feita pelos Validadores
@app.route('/transacao/<string:ip>/<int:id>/<int:status>/<string:chave>', methods=["POST"])
def validarTransacao(ip, id, status, chave):
    if request.method == "POST":
        try:
            transacao = seletor.buscarTransacao(i=id)
            if transacao == None:
                return mensagemErro("Transacao invalida")
            elif status not in (0, 1, 2):
                return mensagemErro("Status invalida")
            elif not seletor.isValidadorIpCadastrado(ip):
                return mensagemErro("IP nao cadastrado")
            seletor.validarChave(ip=ip, chave=chave)
            
            transacao.adicionarValidacao(ip=ip, status=status)
            
            if transacao.isTransacaoProntaValidar():
                seletor.validarTransacao(transacao=transacao)
                
                seletor.alterarTransacao(transacao=transacao)
                
                seletor.removerTransacao(transacao=transacao)
        except Exception as e:
            return mensagemErro(str(e))
    else:
        return mensagemErro("Metodo invalido")

    return mensagemSucesso("Validacao executada")


@app.errorhandler(404)
def page_not_found(erro):
    return render_template('page_not_found.html'), 404

app.run(host='127.0.0.1', debug=True)
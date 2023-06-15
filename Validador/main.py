from transacao import Transacao
from datetime import datetime
from flask import Flask, request, Response
from validador import Validador

# horario das transacoes possuem miliseg
FORMAT_DATA = "%Y-%m-%d %H:%M:%S.%f"

validador = Validador()
app = Flask(__name__)

def mensagemErro(mensagem:str):
    print(f'erro: {mensagem}')
    return '{ erro: %s }' % mensagem

def mensagemSucesso(mensagem:str):
    print(f'sucesso: {mensagem}')
    return '{ sucesso: %s }' % mensagem

@app.route('/<string:ip>/<string:chave>')
def incializarValidador(ip, chave):
    validador.ip = ip
    validador.chave = chave
    validador.is_inicializado = True
    return mensagemSucesso("Validador Inicializado")

@app.route('/transacao/validar', methods=['POST'])
def validarTransacao():
    global validador
    
    print(request.form)
    ret = request.form
    transacao = Transacao(id=int(ret['id']), valor=int(ret['valor']), rem=int(ret['id_rem']),
                          horario=datetime.strptime(ret['horario_trans'], FORMAT_DATA))
    
    validador.qtde_trans = int(ret['trans_rem'])
    validador.valor_conta_rem = int(ret['conta_rem'])
    validador.horario_ultima_trans = datetime.strptime(ret['horario_ult_trans'], FORMAT_DATA)
    
    try:
        validador.valida_transacao(transacao=transacao, horario_atual=datetime.strptime(ret['horario_atual'], FORMAT_DATA))
        validador.enviar_validacao(transacao=transacao)
    except Exception as e:
        return mensagemErro(str(e))
    return mensagemSucesso("Transacao Julgada")

@app.route('/ping', methods=['GET'])
def ping():
    if validador.is_inicializado:
        return Response(status=200)
    else:
        return Response(status=500)


app.run(host="127.0.0.3", debug=True)




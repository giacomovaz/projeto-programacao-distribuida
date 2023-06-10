from database import Database
from sqlite3 import IntegrityError
import json
from transacao import Transacao

class Validador:
    id: int
    qtd_moeda: int
    qtd_flags: int
    ip: str

    def __init__(self, id:int=0, qtd_moeda:int=0, qtd_flags:int=0, ip:str="0.0.0.0"):
        self.id = id
        self.qtd_moeda = qtd_moeda
        self.qtd_flags = qtd_flags
        self.ip = ip

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def cadastraDb(self):
        db = Database()
        query = "INSERT INTO VALIDADORES (id, qtd_moeda, qtd_flags, ip) VALUES (?, ?, ?, ?)"
        param = [self.id, self.qtd_moeda, self.qtd_flags, self.ip]
        db.execute(query, param)
        db.save()

    def excluirDb(self):
        db = Database()
        query = "DELETE FROM VALIDADORES WHERE id = ?"
        param = [self.id]
        db.execute(query, param)
        db.save()

    def editarDb(self, campo:str):
        db = Database()
        query = "UPDATE VALIDADORES SET "
        param = 0

        if campo == "qtd_moedas":
            query = query + "qtd_moedas = ?"
            param = [self.qtd_moeda]
        elif campo == "qtd_flags":
            query = query + "qtd_flags = ?"
            param = [self.qtd_flags]
        else:
            raise Exception("Campo nao alteravel")
        
        db.execute(query, param)
        db.save()
        
    @staticmethod
    def buscarUmDb(id:int):
        db = Database()
        query = "SELECT * FROM VALIDADORES WHERE id = ?"
        param = [id]
        # pegar o unico retorno dessa busca
        ret = db.execute(query, param).fetchone()
            
        return Validador(id=ret[0], qtd_moeda=ret[1], qtd_flags=ret[2], ip=ret[3])


class Seletor:
    total_moedas:int
    validadores:list[Validador] = []
    
    def __init__(self):
        self.resgatarValidadores()
        self.resgatarTotalMoedas()
    
    def resgatarValidadores(self):
        db = Database()
        query = "SELECT id FROM VALIDADORES"
        
        ids = db.execute(query=query).fetchall()
        if ids != []:
            for i in ids:
                validador = Validador.buscarUmDb(i[0])
                self.validadores.append(validador)
        
    
    def resgatarTotalMoedas(self):
        db = Database()
        query = "SELECT total_moedas FROM SELETOR"
        ret = db.execute(query=query).fetchone()
        
        if ret == None:
            self.inicializarTotalMoedas()
        else:
            self.total_moedas = ret[0]
            
    def inicializarTotalMoedas(self):
        db = Database()
        query = "INSERT INTO SELETOR VALUES(0)"
        db.execute(query=query)
        db.save()
        self.total_moedas = 0
    
    def atualizarTotalMoedas(self, moedas:int):
        db = Database()
        query = "UPDATE SELETOR SET total_moedas = ?"
        param = [moedas]
        db.execute(query=query, param=param)
        db.save()
        self.total_moedas = moedas
        
    def quantidadeValidadores(self):
        return len(self.validadores)
    
    def novoValidador(self, qtdMoeda:int, ip:str):
        validador = Validador(id=self.quantidadeValidadores(), qtd_moeda=qtdMoeda, qtd_flags=0,ip=ip)
        try:
            validador.cadastraDb()
        except IntegrityError:
            raise Exception("IP ja cadastrado")
        self.validadores.append(validador)
        return validador

    def validarTransacao(self, transacao:Transacao):
        # chamada ao validador
        resultado = ""
        try:
            if resultado == "sucesso":
                return 1
            elif resultado == "erro":
                return 2
            else:
                return 0
        except Exception as e:
            print(str(e))
            return 0

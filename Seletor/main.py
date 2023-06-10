import sqlite3 as sql
import mysql.connector as conn

class Database:
    db: sql.Connection
    cursor: sql.Cursor
    
    database = "seletor_fcoin.db"
    
    def __init__(self):
        self.db = sql.connect(self.database)
        self.cursor = self.db.cursor()
        
    # explicitando que o DB sera fechado
    def __del__(self):
        self.db.close()
    
    def execute(self, query, param = []):
        self.cursor.execute(query, param)
        return self.cursor
    
    def save(self):
        self.db.commit()
    

class Validador:
    id: int
    qtd_moeda: int
    qtd_flags: int
    ip: str

    def __init__(self, id=0, qtd_moeda=0, qtd_flags=0, ip="0.0.0.0"):
        self.id = id
        self.qtd_moeda = qtd_moeda
        self.qtd_flags = qtd_flags
        self.ip = ip

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

    def editarDb(self, campo):
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
    def buscarUmDb(id):
        db = Database()
        query = "SELECT * FROM VALIDADORES WHERE id = ?"
        param = [id]
        # pegar o unico retorno dessa busca
        ret = db.execute(query, param).fetchone()
            
        return Validador(id=ret[0], qtd_moeda=ret[1], qtd_flags=ret[2], ip=ret[3])


class Seletor:
    total_moedas:int
    validadores:list[Validador]
    
    def __init__(self):
        self.resgatarValidadores()
        self.resgatarTotalMoedas()
    
    def resgatarValidadores(self):
        db = Database()
        query = "SELECT id FROM VALIDADORES"
        
        ids = db.execute(query=query).fetchall()
        for i in ids:
            validador = Validador.buscarUmDb(i)
            self.validadores.append(validador)
    
    def resgatarTotalMoedas(self):
        db = Database()
        query = "SELECT total_moedas FROM SELETOR"
        self.total_moedas = db.execute(query=query).fetchone()[0]
        
    def atualizarTotalMoedas(self, moedas):
        db = Database()
        query = "UPDATE SELETOR SET total_moedas = ?"
        param = [moedas]
        db.execute(query=query, param=param)
        db.save()


def criaTabela():
    db = Database()
    query = [
        "CREATE TABLE VALIDADORES (id INTEGER PRIMARY KEY, qtd_moeda INTEGER, qtd_flags INTEGER, ip VARCHAR(15) UNIQUE)",
        "CREATE TABLE SELETOR (total_moedas INTEGER)"
    ]
    
    for q in query:
        # caso a tabela ja exista so continua
        try:
            db.execute(q)
        except sql.OperationalError:
            pass

criaTabela()


    

    
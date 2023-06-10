import sqlite3 as sql
import mysql.connector as conn

class Database:
    db: sql.Connection
    cursor: sql.Cursor
    
    database = "seletor_fcoin.db"
    
    def __init__(self):
        self.db = sql.connect(self.database)
        self.cursor = self.db.cursor()
        
    # explicitando que o recurso sera fechado
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

    def __init__(self, id, qtd_moeda, qtd_flags, ip):
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

    def consultarDb(self):
        db = Database()
        query = "SELECT * FROM VALIDADORES WHERE id = ?"
        param = [self.id]
        ret = db.execute(query, param).fetchall()

        for x in ret:
            self.id = x[0]
            self.qtd_moeda = x[1] 
            self.qtd_flags = x[2]
            self.ip = x[3]

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


# quantidade total de moedas no seletor
total_moedas_seletor = 0

def criaTabela():
    db = Database()
    query = "CREATE TABLE VALIDADORES (id INTEGER, qtd_moeda INTEGER, qtd_flags INTEGER, ip VARCHAR(15)"
    
    # caso a tabela ja exista so continua
    try:
        db.execute(query)
    except sql.OperationalError:
        pass

criaTabela()


    

    
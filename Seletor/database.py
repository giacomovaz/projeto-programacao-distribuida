import sqlite3 as sql

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
        
    def criarTabelas(self, query=[]):
        for q in query:
            # caso a tabela ja exista so continua
            try:
                self.execute(q)
            except sql.OperationalError:
                pass

    
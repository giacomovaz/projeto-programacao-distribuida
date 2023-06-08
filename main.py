import mysql.connector as conn

def database():
    mydb = conn.connect(
        host="localhost",
        user="yourusername",
        password="yourpassword"
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE FCOIN")

    return "FCOIN"

# conectar ao DB
mydb = conn.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword",
  database=database()
)

# quantidade total de moedas no seletor
total_moedas_seletor = 0

def criaTabela():
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE VALIDADORES (id INTEGER, qtd_moeda INTEGER, qtd_flags INTEGER, ip VARCHAR(15)")

criaTabela()


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
        mycursor = mydb.cursor()
        sql = "INSERT INTO VALIDADORES (id, qtd_moeda, qtd_flags, ip) VALUES (%d, %d, %d, %s)"
        val = (self.id, self.qtd_moeda, self.qtd_flags, self.ip)
        mycursor.execute(sql, val)
        mydb.commit()

    def excluirDb(self):
        mycursor = mydb.cursor()
        sql = "DELETE FROM VALIDADORES WHERE id = %d"
        val = (self.id)
        mycursor.execute(sql, val)
        mydb.commit()

    def consultarDb(self):
        mycursor = mydb.cursor()
        sql = "SELECT * FROM VALIDADORES WHERE id = %d"
        val = (self.id)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        for x in myresult:
            self.id = x[0]
            self.qtd_moeda = x[1] 
            self.qtd_flags = x[2]
            self.ip = x[3]

    def editarDb(self, campo):
        mycursor = mydb.cursor()
        sql = "UPDATE VALIDADORES SET "
        val = 0

        if campo == "qtd_moedas":
            sql = sql + "qtd_moedas = %d"
            val = (self.qtd_moeda)
        elif campo == "qtd_flags":
            sql = sql + "qtd_flags = %d"
            val = (self.qtd_flags)
        else:
            raise Exception("Deu ruim")
        
        mycursor.execute(sql, val)
        mydb.commit()

    

    
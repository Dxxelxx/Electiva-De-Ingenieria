import psycopg2

def conectar():
    return psycopg2.connect(
        host="localhost",
        database="bebidas_pacifico",
        user="postgres",
        password="1109920832",
        port="5432"
    )
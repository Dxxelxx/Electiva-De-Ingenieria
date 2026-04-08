from conexion import conectar

conexion = conectar()
cursor = conexion.cursor()

bebidas = [
    ("Viche", 10.000),
    ("Arrechón", 12.000),
    ("Tomaseca", 9.000),
    ("Borojo con leche", 8.000),
    ("Jugo de chontaduro", 7.000),
    ("Lulada", 6.000),
    ("Agua de panela", 3.000),
    ("Jugo de maracuyá", 5.000),
    ("Jugo de mango", 5.000),
    ("Café", 2.000)
]

for bebida in bebidas:
    cursor.execute(
        "INSERT INTO bebidas (nombre, precio) VALUES (%s, %s)",
        bebida
    )

conexion.commit()
conexion.close()

print("Bebidas insertadas")
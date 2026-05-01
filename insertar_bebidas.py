from conexion import conectar

conexion = conectar()
cursor = conexion.cursor()

bebidas = [
    ("Viche", 10000),
    ("Arrechón", 12000),
    ("Tomaseca", 9000),
    ("Borojo con leche", 8000),
    ("Jugo de chontaduro", 7000),
    ("Lulada", 6000),
    ("Agua de panela", 3000),
    ("Jugo de maracuyá", 5000),
    ("Jugo de mango", 5000),
    ("Café", 2000)
]

cursor.executemany(
    "INSERT INTO bebidas (nombre, precio) VALUES (%s, %s)",
    bebidas
)

conexion.commit()
conexion.close()

print("✅ Bebidas insertadas correctamente")
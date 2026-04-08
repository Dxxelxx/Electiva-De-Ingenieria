from conexion import conectar

conexion = conectar()
cursor = conexion.cursor()

# Tabla bebidas
cursor.execute("""
CREATE TABLE bebidas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    precio DECIMAL(10,3)
);
""")

# Tabla clientes
cursor.execute("""
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20)
);
""")

# Tabla pedidos
cursor.execute("""
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INT,
    total DECIMAL(10,3),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
""")

conexion.commit()
conexion.close()

print("Tablas creadas")
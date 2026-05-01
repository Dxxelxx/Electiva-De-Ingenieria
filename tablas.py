from conexion import conectar

conexion = conectar()
cursor = conexion.cursor()

# =========================
# 🗑️ BORRAR TABLAS
# =========================
cursor.execute("DROP TABLE IF EXISTS detalle_pedidos CASCADE;")
cursor.execute("DROP TABLE IF EXISTS pedidos CASCADE;")
cursor.execute("DROP TABLE IF EXISTS clientes CASCADE;")
cursor.execute("DROP TABLE IF EXISTS bebidas CASCADE;")
cursor.execute("DROP TABLE IF EXISTS usuarios CASCADE;")

# =========================
# 🥤 TABLA BEBIDAS
# =========================
cursor.execute("""
CREATE TABLE bebidas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    precio INT
);
""")

# =========================
# 👤 TABLA CLIENTES
# =========================
cursor.execute("""
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20)
);
""")

# =========================
# 🧾 TABLA PEDIDOS
# =========================
cursor.execute("""
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(id),
    total INT,
    domicilio BOOLEAN DEFAULT FALSE,
    total_final INT
);
""")

# =========================
# 📦 DETALLE PEDIDOS
# =========================
cursor.execute("""
CREATE TABLE detalle_pedidos (
    id SERIAL PRIMARY KEY,
    pedido_id INT REFERENCES pedidos(id),
    bebida_id INT REFERENCES bebidas(id),
    cantidad INT DEFAULT 1
);
""")

# =========================
# 🔐 TABLA USUARIOS (LOGIN)
# =========================
cursor.execute("""
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    password TEXT,  -- 🔥 AQUÍ ESTÁ LA CORRECCIÓN
    rol VARCHAR(20)
);
""")

# =========================
# 👨‍💼 INSERTAR ADMINS (HASH)
# =========================
cursor.execute("""
INSERT INTO usuarios (username, password, rol) VALUES
('daniel', 'scrypt:32768:8:1$UudMF64QGx1I3Iyd$a0213ef199359b6629d90cb0289cb39f855e68d128bc947e08ba92442b5de427ba15a89104bb7ecc50222ea976845bd5e3fe2f50b237e410b9320bb26182aeac', 'admin'),
('alex', 'scrypt:32768:8:1$wchpMU86d0lcvRvj$18df419c29ba15b384048cf9cb28139b3b1cf61734c1cec309129a2f43563f0afaee3bf1340d3927e909ab8aa8368c98105e82290b4448025fbec22afade9d42', 'admin');
""")

conexion.commit()
conexion.close()

print("✅ Base de datos completa creada correctamente")
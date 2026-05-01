from flask import Flask, render_template, request, jsonify, session, redirect
from conexion import conectar
from datetime import datetime
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "clave_secreta"


# =========================
# 🔐 LOGIN SEGURO
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()

        conexion.close()

        if user and check_password_hash(user[2], password):
            session["usuario"] = user[1]
            session["rol"] = user[3]

            if user[3] == "admin":
                return redirect("/admin")
            else:
                return redirect("/")
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")


# =========================
# 🔓 LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# 🌐 INDEX (CLIENTE) 🔥 CORREGIDO
# =========================
@app.route("/")
def index():
    if "usuario" not in session:
        return redirect("/login")

    conexion = conectar()
    cursor = conexion.cursor()

    # 🔥 IMPORTANTE: traer imagen
    cursor.execute("SELECT id, nombre, precio, imagen FROM bebidas;")
    bebidas = cursor.fetchall()

    conexion.close()

    return render_template("index.html", bebidas=bebidas)


# =========================
# 🛒 COMPRAR
# =========================
@app.route("/comprar", methods=["POST"])
def comprar():
    if "usuario" not in session:
        return redirect("/login")

    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    seleccion = request.form.getlist("bebidas")
    domicilio = request.form.get("domicilio")

    if not seleccion:
        return "❌ Debes seleccionar al menos una bebida"

    conexion = conectar()
    cursor = conexion.cursor()

    # Cliente
    cursor.execute(
        "INSERT INTO clientes (nombre, telefono) VALUES (%s, %s) RETURNING id",
        (nombre, telefono)
    )
    cliente_id = cursor.fetchone()[0]

    total = 0
    productos = []

    for bebida_id in seleccion:
        cursor.execute(
            "SELECT id, nombre, precio FROM bebidas WHERE id=%s",
            (bebida_id,)
        )
        bebida = cursor.fetchone()

        if bebida:
            productos.append(bebida)
            total += bebida[2]

    costo_domicilio = 5000 if domicilio else 0
    total_final = total + costo_domicilio

    # Pedido
    cursor.execute(
        "INSERT INTO pedidos (cliente_id, total, domicilio, total_final) VALUES (%s, %s, %s, %s) RETURNING id",
        (cliente_id, total, bool(domicilio), total_final)
    )
    pedido_id = cursor.fetchone()[0]

    # Detalle
    for bebida in productos:
        cursor.execute(
            "INSERT INTO detalle_pedidos (pedido_id, bebida_id, cantidad) VALUES (%s, %s, %s)",
            (pedido_id, bebida[0], 1)
        )

    conexion.commit()
    conexion.close()

    return render_template(
        "recibo.html",
        nombre=nombre,
        telefono=telefono,
        productos=productos,
        total=total,
        domicilio=costo_domicilio,
        total_final=total_final,
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M")
    )


# =========================
# 📊 PANEL ADMIN PRO
# =========================
@app.route("/admin")
def admin():
    if "rol" not in session or session["rol"] != "admin":
        return redirect("/login")

    conexion = conectar()
    cursor = conexion.cursor()

    # Pedidos
    cursor.execute("""
    SELECT 
        p.id,
        c.nombre,
        c.telefono,
        p.total_final
    FROM pedidos p
    JOIN clientes c ON p.cliente_id = c.id
    ORDER BY p.id DESC
    """)
    pedidos = cursor.fetchall()

    # Totales
    cursor.execute("SELECT COALESCE(SUM(total_final),0) FROM pedidos;")
    total_ventas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos;")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM clientes;")
    total_clientes = cursor.fetchone()[0]

    # Gráfica clientes
    cursor.execute("""
    SELECT c.nombre, SUM(p.total_final)
    FROM pedidos p
    JOIN clientes c ON p.cliente_id = c.id
    GROUP BY c.nombre
    """)
    ventas_clientes = cursor.fetchall()

    # Gráfica productos
    cursor.execute("""
    SELECT b.nombre, SUM(dp.cantidad)
    FROM detalle_pedidos dp
    JOIN bebidas b ON dp.bebida_id = b.id
    GROUP BY b.nombre
    """)
    ventas_productos = cursor.fetchall()

    conexion.close()

    return render_template(
        "admin.html",
        pedidos=pedidos,
        total_ventas=total_ventas,
        total_pedidos=total_pedidos,
        total_clientes=total_clientes,
        ventas_clientes=ventas_clientes,
        ventas_productos=ventas_productos,
        usuario=session["usuario"]
    )


# =========================
# 👁️ VER PEDIDO
# =========================
@app.route("/pedido/<int:id>")
def ver_pedido(id):
    if "rol" not in session or session["rol"] != "admin":
        return redirect("/login")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT 
        p.id,
        c.nombre,
        c.telefono,
        p.total,
        p.domicilio,
        p.total_final
    FROM pedidos p
    JOIN clientes c ON p.cliente_id = c.id
    WHERE p.id=%s
    """, (id,))
    
    pedido = cursor.fetchone()

    cursor.execute("""
    SELECT b.nombre, b.precio
    FROM detalle_pedidos dp
    JOIN bebidas b ON dp.bebida_id = b.id
    WHERE dp.pedido_id=%s
    """, (id,))

    productos = cursor.fetchall()

    conexion.close()

    return render_template("detalle_pedido.html", pedido=pedido, productos=productos)


# =========================
# 🗑️ ELIMINAR PEDIDO
# =========================
@app.route("/eliminar_pedido/<int:id>")
def eliminar_pedido(id):
    if "rol" not in session or session["rol"] != "admin":
        return redirect("/login")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id=%s", (id,))
    cursor.execute("DELETE FROM pedidos WHERE id=%s", (id,))

    conexion.commit()
    conexion.close()

    return redirect("/admin")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
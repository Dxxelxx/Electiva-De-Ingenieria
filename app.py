from flask import Flask, render_template, request
from conexion import conectar
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM bebidas;")
    bebidas = cursor.fetchall()

    conexion.close()
    return render_template("index.html", bebidas=bebidas)


@app.route("/comprar", methods=["POST"])
def comprar():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    seleccion = request.form.getlist("bebidas")

    conexion = conectar()
    cursor = conexion.cursor()

    # Guardar cliente
    cursor.execute(
        "INSERT INTO clientes (nombre, telefono) VALUES (%s, %s) RETURNING id",
        (nombre, telefono)
    )
    cliente_id = cursor.fetchone()[0]

    total = 0
    productos = []

    # Obtener productos seleccionados
    for bebida_id in seleccion:
        cursor.execute("SELECT id, nombre, precio FROM bebidas WHERE id=%s", (bebida_id,))
        bebida = cursor.fetchone()

        if bebida:
            productos.append(bebida)
            total += bebida[2]

    # Guardar pedido
    cursor.execute(
        "INSERT INTO pedidos (cliente_id, total) VALUES (%s, %s)",
        (cliente_id, total)
    )

    conexion.commit()
    conexion.close()

    return render_template(
        "recibo.html",
        nombre=nombre,
        telefono=telefono,
        productos=productos,
        total=total,
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M")
    )


if __name__ == "__main__":
    app.run(debug=True)
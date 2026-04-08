from flask import Flask, render_template, request
from conexion import conectar

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

    for bebida_id in seleccion:
        cursor.execute("SELECT precio FROM bebidas WHERE id=%s", (bebida_id,))
        precio = cursor.fetchone()[0]
        total += precio

    # Guardar pedido
    cursor.execute(
        "INSERT INTO pedidos (cliente_id, total) VALUES (%s, %s)",
        (cliente_id, total)
    )

    conexion.commit()
    conexion.close()

    return f"<h2>Compra realizada 💰 Total: ${total}</h2><a href='/'>Volver</a>"

if __name__ == "__main__":
    app.run(debug=True)
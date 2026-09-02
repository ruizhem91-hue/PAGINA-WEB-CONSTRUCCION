from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

# ==================================================
# CONFIGURACION DEL CORREO
# ==================================================

CORREO_EMPRESA = "solucionesintegrales@gmail.com"

# IMPORTANTE:
# Aquí después colocaremos una CONTRASEÑA DE APLICACION
# de Gmail, NO tu contraseña normal.
CONTRASENA_APP = "AQUI_VA_TU_CONTRASENA_DE_APLICACION"


# ==================================================
# CREAR BASE DE DATOS
# ==================================================

def crear_base_datos():

    conexion = sqlite3.connect("clientes.db")

    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            motivo TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


# Crear la base de datos al iniciar la aplicación
crear_base_datos()


# ==================================================
# PAGINA PRINCIPAL
# ==================================================

@app.route("/")
def inicio():
    return render_template("index.html")


# ==================================================
# RECIBIR SOLICITUD DE PRESUPUESTO
# ==================================================

@app.route("/contacto", methods=["POST"])
def contacto():

    # Recibimos los datos enviados desde el formulario
    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")
    motivo = request.form.get("motivo")

    # Verificamos que los campos estén completos
    if not nombre or not telefono or not motivo:
        return "Por favor, complete todos los campos."

    # Limitar el motivo a 500 caracteres
    motivo = motivo[:500]

    # Fecha y hora de la consulta
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ==============================================
    # GUARDAR CLIENTE EN LA BASE DE DATOS
    # ==============================================

    conexion = sqlite3.connect("clientes.db")

    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO clientes (nombre, telefono, motivo, fecha)
        VALUES (?, ?, ?, ?)
    """, (
        nombre,
        telefono,
        motivo,
        fecha
    ))

    conexion.commit()
    conexion.close()


    # ==============================================
    # ENVIAR CORREO A GMAIL
    # ==============================================

    try:

        asunto = "Nueva solicitud de presupuesto"

        mensaje = f"""
NUEVA SOLICITUD DE PRESUPUESTO

Nombre:
{nombre}

Teléfono:
{telefono}

Motivo de la consulta:
{motivo}

Fecha:
{fecha}
"""

        email = MIMEMultipart()

        email["From"] = CORREO_EMPRESA
        email["To"] = CORREO_EMPRESA
        email["Subject"] = asunto

        email.attach(MIMEText(mensaje, "plain"))

        servidor = smtplib.SMTP("smtp.gmail.com", 587)

        servidor.starttls()

        servidor.login(
            CORREO_EMPRESA,
            CONTRASENA_APP
        )

        servidor.send_message(email)

        servidor.quit()

    except Exception as error:

        print("Error al enviar correo:", error)


    # ==============================================
    # VOLVER A LA PAGINA
    # ==============================================

    return redirect(url_for("inicio"))


# ==================================================
# INICIAR LA APLICACION
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)
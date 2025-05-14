from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_segura'  # Necesario para usar flash

@app.route('/')
def home():
    clubs = ['ajedrez', 'futbol', 'gimnasio']
    filtro_club = request.args.get('club')
    filtro_matricula = request.args.get('matricula')
    registros = []

    for club in clubs:
        if filtro_club and filtro_club != club:
            continue

        docs = db.collection(club).stream()
        for doc in docs:
            if filtro_matricula and filtro_matricula.lower() not in doc.id.lower():
                continue
            data = doc.to_dict()
            data['club'] = club
            data['matricula'] = doc.id
            registros.append(data)

    return render_template('home.html', registros=registros, clubs=clubs, filtro_club=filtro_club or "", filtro_matricula=filtro_matricula or "")

@app.route('/registro')
def form():
    clubs = ['ajedrez', 'futbol', 'gimnasio']
    return render_template('form.html', clubs=clubs)

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        club = request.form['club']
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        correo = request.form['correo']
        data = {'nombre': nombre, 'correo': correo}
        db.collection(club).document(matricula).set(data)
        flash('Estudiante registrado exitosamente.', 'success')
    except Exception as e:
        print("Error al guardar:", e)
        flash('Ocurrió un error al registrar al estudiante.', 'danger')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

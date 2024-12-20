from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
import os
import re
from datetime import datetime
import pandas as pd
import logging
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import ollama
import sqlite3
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the Userlog model
class Userlog(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def check_password(self, password):
        return self.password == password

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Userlog, int(user_id))


@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Userlog.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

class User(db.Model):
    matricule = db.Column(db.String(8), primary_key=True, nullable=False)
    nom_usuel = db.Column(db.String(50), nullable=True)
    prenom = db.Column(db.String(50), nullable=True)
    date_de_naissance = db.Column(db.Date, nullable=True)
    date_d_entree = db.Column(db.Date, nullable=True)
    situation_familiale = db.Column(db.String(50), nullable=True)
    echelle = db.Column(db.String(50), nullable=True)
    date_debut_grade = db.Column(db.Date, nullable=True)
    echelon = db.Column(db.String(50), nullable=True)
    date_d_effet = db.Column(db.Date, nullable=True)
    sexe = db.Column(db.String(1), nullable=True)
    etablissement = db.Column(db.String(100), nullable=True)
    numero_carte_identite = db.Column(db.String(50), unique=True, nullable=False)
    identifiant_emploi = db.Column(db.String(50), nullable=True)
    code_caisse = db.Column(db.String(50), nullable=True)
    numerau_d_inscription = db.Column(db.String(50), nullable=True)

    def __init__(self, matricule, **kwargs):
        if not re.match(r'^[A-Za-z]{2}\d{4}$|^[A-Za-z]\d{5}$', matricule):
            raise ValueError("Matricule must be two letters followed by four numbers or one letter followed by five numbers.")
        self.matricule = matricule
        for key, value in kwargs.items():
            setattr(self, key, value)

# Define the Leave model
class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(8), db.ForeignKey('user.matricule', ondelete='CASCADE'), nullable=False)
    conge_non_pris_n_1 = db.Column(db.Integer, default=0, nullable=False)
    conge_n = db.Column(db.Integer, default=54, nullable=False)
    date_debut_conge = db.Column(db.Date, nullable=True)
    date_fin_conge = db.Column(db.Date, nullable=True)
    leave_days_taken = db.Column(db.Integer, default=0, nullable=True)

    user = db.relationship('User', backref=db.backref('leaves', lazy=True, cascade='all, delete-orphan'))

# Define the Announcement model
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# Define the Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

@app.route('/home')
@login_required
def home():
    total_employees = User.query.count()
    today = datetime.today().date()
    on_leave = Leave.query.filter(Leave.date_debut_conge <= today, Leave.date_fin_conge >= today).count()
    
    leave_distribution = [0, 0, 0, 0, 0, 0]
    leaves = Leave.query.all()

    for leave in leaves:
        if 1 <= leave.leave_days_taken <= 10:
            leave_distribution[0] += 1
        elif 11 <= leave.leave_days_taken <= 20:
            leave_distribution[1] += 1
        elif 21 <= leave.leave_days_taken <= 30:
            leave_distribution[2] += 1
        elif 31 <= leave.leave_days_taken <= 40:
            leave_distribution[3] += 1
        elif 41 <= leave.leave_days_taken <= 50:
            leave_distribution[4] += 1
        elif leave.leave_days_taken >= 51:
            leave_distribution[5] += 1

    recent_employees = User.query.order_by(User.date_d_entree.desc()).limit(5).all()
    upcoming_events = Event.query.filter(Event.date >= datetime.today()).order_by(Event.date).limit(2).all()
    all_events = Event.query.all()
    return render_template('home.html', total_employees=total_employees, on_leave=on_leave, leave_distribution=leave_distribution, recent_employees=recent_employees, upcoming_events=upcoming_events, all_events=all_events)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        new_event = Event(title=title, date=date)
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_event.html')

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_event.html', event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        app.logger.debug(f"Form data: {request.form}")

        try:
            user = User(
                matricule=request.form['matricule'],
                nom_usuel=request.form['nom_usuel'],
                prenom=request.form['prenom'],
                date_de_naissance=datetime.strptime(request.form['date_de_naissance'], '%Y-%m-%d').date(),
                date_d_entree=datetime.strptime(request.form['date_d_entree'], '%Y-%m-%d').date(),
                situation_familiale=request.form['situation_familiale'],
                echelle=request.form['echelle'],
                date_debut_grade=datetime.strptime(request.form['date_debut_grade'], '%Y-%m-%d').date(),
                echelon=request.form['echelon'],
                date_d_effet=datetime.strptime(request.form['date_d_effet'], '%Y-%m-%d').date(),
                sexe=request.form['sexe'],
                etablissement=request.form['etablissement'],
                numero_carte_identite=request.form['numero_carte_identite'],
                identifiant_emploi=request.form['identifiant_emploi'],
                code_caisse=request.form['code_caisse'],
                numerau_d_inscription=request.form['numerau_d_inscription']
            )
            db.session.add(user)
            db.session.commit()
            leave = Leave(matricule=user.matricule)
            db.session.add(leave)
            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: Matricule or Identity Card Number already exists.', 'danger')
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'danger')

    return render_template('index.html')

@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_excel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and file.filename.endswith('.xlsx'):
            try:
                df = pd.read_excel(file)

                field_mapping = {
                    'matricule': ['Matricule', 'Mat.'],
                    'nom_usuel': ['Nom usuel', 'Nom'],
                    'prenom': ['Prénom', 'Prenom'],
                    'date_de_naissance': ['Date de naissance', 'Naiss.'],
                    'date_d_entree': ['Date d\'entrée', 'Entrée'],
                    'situation_familiale': ['Situation familial', 'Sit. Fam.'],
                    'echelle': ['Echelle', 'Ech.'],
                    'date_debut_grade': ['Date début grade', 'Déb. Gr.'],
                    'echelon': ['Echelon', 'Ech.'],
                    'date_d_effet': ['Date d\'effet', 'Effet'],
                    'sexe': ['Sexe'],
                    'etablissement': ['Etablissement', 'Etab.'],
                    'numero_carte_identite': ['N carte identité', 'Num. CI'],
                    'identifiant_emploi': ['Identifiant emploi', 'ID Emp.'],
                    'code_caisse': ['Code Caisse', 'Caisse'],
                    'numerau_d_inscription': ['Numéro d\'inscription', 'Inscr.']
                }

                def get_mapped_value(row, key):
                    for field in field_mapping[key]:
                        if field in row:
                            return row[field]
                    return None

                for index, row in df.iterrows():
                    try:
                        matricule = get_mapped_value(row, 'matricule')
                        numero_carte_identite = get_mapped_value(row, 'numero_carte_identite')

                        if not matricule or not numero_carte_identite:
                            flash(f"Skipping row {index} due to missing critical fields (Matricule or Identity Card Number).", 'warning')
                            continue

                        if User.query.filter_by(numero_carte_identite=numero_carte_identite).first():
                            flash(f"Duplicate found for {numero_carte_identite}. Skipping.", 'warning')
                            continue

                        user_data = {
                            'matricule': matricule,
                            'nom_usuel': get_mapped_value(row, 'nom_usuel'),
                            'prenom': get_mapped_value(row, 'prenom'),
                            'date_de_naissance': pd.to_datetime(get_mapped_value(row, 'date_de_naissance')).date() if get_mapped_value(row, 'date_de_naissance') else None,
                            'date_d_entree': pd.to_datetime(get_mapped_value(row, 'date_d_entree')).date() if get_mapped_value(row, 'date_d_entree') else None,
                            'situation_familiale': get_mapped_value(row, 'situation_familiale'),
                            'echelle': get_mapped_value(row, 'echelle'),
                            'date_debut_grade': pd.to_datetime(get_mapped_value(row, 'date_debut_grade')).date() if get_mapped_value(row, 'date_debut_grade') else None,
                            'echelon': get_mapped_value(row, 'echelon'),
                            'date_d_effet': pd.to_datetime(get_mapped_value(row, 'date_d_effet')).date() if get_mapped_value(row, 'date_d_effet') else None,
                            'sexe': get_mapped_value(row, 'sexe'),
                            'etablissement': get_mapped_value(row, 'etablissement'),
                            'numero_carte_identite': numero_carte_identite,
                            'identifiant_emploi': get_mapped_value(row, 'identifiant_emploi'),
                            'code_caisse': get_mapped_value(row, 'code_caisse'),
                            'numerau_d_inscription': get_mapped_value(row, 'numerau_d_inscription')
                        }

                        user = User(**user_data)
                        db.session.add(user)
                        db.session.commit()
                        leave = Leave(matricule=user.matricule)
                        db.session.add(leave)
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Error processing row {index}: {str(e)}', 'danger')
                db.session.commit()
                flash('Users imported successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file format. Please upload a .xlsx file.', 'danger')
            return redirect(request.url)
    return render_template('import.html')

@app.route('/users', methods=['GET'])
@login_required
def list_users():
    users = User.query.all()
    return render_template('list_users.html', users=users)

@app.route('/edit/<matricule>', methods=['GET', 'POST'])
@login_required
def edit_user(matricule):
    user = User.query.get_or_404(matricule)
    if request.method == 'POST':
        try:
            user.nom_usuel = request.form['nom_usuel']
            user.prenom = request.form['prenom']
            user.date_de_naissance = datetime.strptime(request.form['date_de_naissance'], '%Y-%m-%d').date()
            user.date_d_entree = datetime.strptime(request.form['date_d_entree'], '%Y-%m-%d').date()
            user.situation_familiale = request.form['situation_familiale']
            user.echelle = request.form['echelle']
            user.date_debut_grade = datetime.strptime(request.form['date_debut_grade'], '%Y-%m-%d').date()
            user.echelon = request.form['echelon']
            user.date_d_effet = datetime.strptime(request.form['date_d_effet'], '%Y-%m-%d').date()
            user.sexe = request.form['sexe']
            user.etablissement = request.form['etablissement']
            user.nom_conjoint = request.form.get('nom_conjoint')
            user.numero_cin = request.form.get('numero_cin')
            user.prenom_enfant = request.form.get('prenom_enfant')
            user.sexe_enfant = request.form.get('sexe_enfant')
            user.date_de_naissance_enfant = datetime.strptime(request.form['date_de_naissance_enfant'], '%Y-%m-%d').date() if request.form.get('date_de_naissance_enfant') else None
            user.identifiant_emploi = request.form['identifiant_emploi']
            user.code_caisse = request.form['code_caisse']
            user.numerau_d_inscription = request.form['numerau_d_inscription']

            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('edit_user.html', user=user)

@app.route('/delete/<matricule>', methods=['POST'])
@login_required
def delete_user(matricule):
    app.logger.debug(f'Trying to delete user with matricule: {matricule}')
    try:
        user = User.query.get_or_404(matricule)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
        app.logger.debug(f'Successfully deleted user with matricule: {matricule}')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting user with matricule: {matricule}, error: {str(e)}')
        flash(f'Error deleting user: {str(e)}', 'danger')
    return redirect(url_for('list_users'))

@app.route('/leaves', methods=['GET', 'POST'])
@login_required
def manage_leaves():
    if request.method == 'POST':
        matricule = request.form['matricule']
        date_debut_conge = datetime.strptime(request.form['date_debut_conge'], '%Y-%m-%d').date()
        date_fin_conge = datetime.strptime(request.form['date_fin_conge'], '%Y-%m-%d').date()
        leave_days_taken = (date_fin_conge - date_debut_conge).days + 1

        leave = Leave.query.filter_by(matricule=matricule).first()
        if not leave:
            flash(f'No leave data found for Matricule: {matricule}', 'danger')
            return redirect(url_for('manage_leaves'))

        if leave.conge_non_pris_n_1 >= leave_days_taken:
            leave.conge_non_pris_n_1 -= leave_days_taken
        else:
            remaining_days = leave_days_taken - leave.conge_non_pris_n_1
            leave.conge_non_pris_n_1 = 0
            if leave.conge_n >= remaining_days:
                leave.conge_n -= remaining_days
            else:
                flash('Not enough leave days available.', 'danger')
                return redirect(url_for('manage_leaves'))

        leave.date_debut_conge = date_debut_conge
        leave.date_fin_conge = date_fin_conge
        leave.leave_days_taken = leave_days_taken

        db.session.commit()
        flash('Leave days updated successfully!', 'success')
        return redirect(url_for('manage_leaves'))

    leaves = Leave.query.all()
    return render_template('manage_leaves.html', leaves=leaves)

@app.route('/get_leave_data', methods=['GET'])
@login_required
def get_leave_data():
    end_date = datetime.today()
    start_date = end_date.replace(day=1) - pd.DateOffset(months=11)
    
    leave_data = db.session.query(
        db.func.strftime('%Y-%m', Leave.date_debut_conge).label('month'),
        db.func.sum(Leave.leave_days_taken).label('leave_days')
    ).filter(
        Leave.date_debut_conge >= start_date,
        Leave.date_debut_conge <= end_date
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()

    labels = [calendar.month_name[int(month.split('-')[1])] for month, _ in leave_data]
    leave_days = [days for _, days in leave_data]

    app.logger.debug(f'Leave data: {leave_data}')

    return jsonify({'labels': labels, 'leave_days': leave_days})


@app.route('/export_table/<format>')
@login_required
def export_table(format):
    users = User.query.all()
    data = {
        "Mat.": [user.matricule for user in users],
        "Nom": [user.nom_usuel for user in users],
        "Prénom": [user.prenom for user in users],
        "Naiss.": [user.date_de_naissance.strftime('%Y-%m-%d') for user in users],
        "Entrée": [user.date_d_entree.strftime('%Y-%m-%d') for user in users],
        "Sit. Fam.": [user.situation_familiale for user in users],
        "Ech.": [user.echelle for user in users],
        "Déb. Gr.": [user.date_debut_grade.strftime('%Y-%m-%d') for user in users],
        "Echelon": [user.echelon for user in users],
        "Effet": [user.date_d_effet.strftime('%Y-%m-%d') for user in users],
        "Sexe": [user.sexe for user in users],
        "Etab.": [user.etablissement for user in users],
        "Num. CI": [user.numero_carte_identite for user in users],
        "ID Emp.": [user.identifiant_emploi for user in users],
        "Caisse": [user.code_caisse for user in users],
        "Inscr.": [user.numerau_d_inscription for user in users],
    }
    df = pd.DataFrame(data)

    if format == 'csv':
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(io.BytesIO(buffer.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='employees.csv')
    
    elif format == 'excel':
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
        buffer.seek(0)
        return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='employees.xlsx')

    elif format == 'pdf':
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []

        logo_path = os.path.join(app.root_path, 'static', 'logo_marsa.jpg')
        logo = Image(logo_path, 50, 50)
        elements.append(logo)

        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.alignment = 1
        title = Paragraph('Liste des Employés', title_style)
        elements.append(title)

        table_data = [
            [
                "Mat.", "Nom", "Prénom", "Naiss.", "Entrée",
                "Sit. Fam.", "Ech.", "Déb. Gr.", "Echelon", "Effet",
                "Sexe", "Etab.", "Num. CI", "ID Emp.",
                "Caisse", "Inscr."
            ]
        ]
        for user in users:
            table_data.append([
                user.matricule, user.nom_usuel, user.prenom, user.date_de_naissance.strftime('%Y-%m-%d'),
                user.date_d_entree.strftime('%Y-%m-%d'), user.situation_familiale, user.echelle,
                user.date_debut_grade.strftime('%Y-%m-%d'), user.echelon, user.date_d_effet.strftime('%Y-%m-%d'),
                user.sexe, user.etablissement, user.numero_carte_identite, user.identifiant_emploi,
                user.code_caisse, user.numerau_d_inscription
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        pdf.build(elements)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='employees.pdf', mimetype='application/pdf')

    else:
        return jsonify({"error": "Unsupported format"})



@app.route('/export_user/<matricule>/<format>')
@login_required
def export_user(matricule, format):
    user = User.query.get_or_404(matricule)
    data = {
        "Matricule": [user.matricule],
        "Nom Usuel": [user.nom_usuel],
        "Prénom": [user.prenom],
        "Date de Naissance": [user.date_de_naissance.strftime('%Y-%m-%d')],
        "Date d'Entrée": [user.date_d_entree.strftime('%Y-%m-%d')],
        "Situation Familiale": [user.situation_familiale],
        "Echelle": [user.echelle],
        "Date Début Grade": [user.date_debut_grade.strftime('%Y-%m-%d')],
        "Echelon": [user.echelon],
        "Date d'Effet": [user.date_d_effet.strftime('%Y-%m-%d')],
        "Sexe": [user.sexe],
        "Etablissement": [user.etablissement],
        "Numéro Carte Identité": [user.numero_carte_identite],
        "Identifiant Emploi": [user.identifiant_emploi],
        "Code Caisse": [user.code_caisse],
    }
    df = pd.DataFrame(data)

    if format == 'csv':
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(io.BytesIO(buffer.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name=f'{user.matricule}.csv')
    elif format == 'excel':
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Employee')
        buffer.seek(0)
        return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'{user.matricule}.xlsx')
    elif format == 'pdf':
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []

        logo_path = os.path.join(app.root_path, 'static', 'logo_marsa.jpg')
        logo = Image(logo_path, 50, 50)
        elements.append(logo)

        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.alignment = 1
        title = Paragraph('Liste des Employés', title_style)
        elements.append(title)

        table_data = [
            [
                "Mat.", "Nom", "Prénom", "Naiss.", "Entrée",
                "Sit. Fam.", "Ech.", "Déb. Gr.", "Echelon", "Effet",
                "Sexe", "Etab.", "Num. CI", "ID Emp.",
                "Caisse"
            ],
            [
                user.matricule, user.nom_usuel, user.prenom, user.date_de_naissance.strftime('%Y-%m-%d'),
                user.date_d_entree.strftime('%Y-%m-%d'), user.situation_familiale, user.echelle,
                user.date_debut_grade.strftime('%Y-%m-%d'), user.echelon, user.date_d_effet.strftime('%Y-%m-%d'),
                user.sexe, user.etablissement, user.numero_carte_identite, user.identifiant_emploi,
                user.code_caisse
            ]
        ]
        table = Table(table_data, colWidths=[
            0.5*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.8*inch,
            1.0*inch, 0.5*inch, 0.7*inch, 0.5*inch, 0.7*inch,
            0.4*inch, 1.0*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.8*inch
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK')
        ]))
        elements.append(table)

        pdf.build(elements)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='employees.pdf')

class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

import os
import sqlite3
import json
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

def get_relevant_data_from_db(query, limit=5):
    conn = sqlite3.connect(os.path.join(basedir, 'data.db'))
    cursor = conn.cursor()

    data_summary = {}
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(tables_query)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        column_query = f"PRAGMA table_info({table_name});"
        cursor.execute(column_query)
        columns = cursor.fetchall()
        
        table_data = []
        for column in columns:
            column_name = column[1]
            search_query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} LIKE ? LIMIT ?"
            cursor.execute(search_query, ('%' + query + '%', limit))
            rows = cursor.fetchall()
            for row in rows:
                table_data.append({column_name: row[0]})
        
        if table_data:
            data_summary[table_name] = table_data

    conn.close()
    return data_summary

def validate_and_format_data(data_summary):
    """Ensure dates are considered when generating a response."""
    today = datetime.now().strftime('%Y-%m-%d')
    formatted_data = {}

    for table, rows in data_summary.items():
        formatted_rows = []
        for row in rows:
            for col, val in row.items():
                if isinstance(val, str) and 'date' in col.lower():
                    if val < today:
                        formatted_rows.append({col: f"{val} (expiré)"})
                    else:
                        formatted_rows.append({col: val})
                else:
                    formatted_rows.append({col: val})
        formatted_data[table] = formatted_rows

    return json.dumps(formatted_data)

@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        user_query = request.json.get("query")
        
        try:
            relevant_data = get_relevant_data_from_db(user_query)
            
            if relevant_data:
                data = validate_and_format_data(relevant_data)
                prompt_template = (
                    f"Vous êtes un chatbot de RH de Marsa Maroc. Votre rôle est d'utiliser "
                    f"les données de la base de données et de répondre aux questions des utilisateurs. "
                    f"Répondez à cette question : '{user_query}' en utilisant les données suivantes : {data}. "
                    f"Votre réponse doit toujours être en français, brève et professionnelle."
                )
            else:
                all_data = get_relevant_data_from_db('')
                data = validate_and_format_data(all_data)
                prompt_template = (
                    f"Vous êtes un chatbot de RH de Marsa Maroc. Votre rôle est d'utiliser les données de la base de données et de répondre aux questions des utilisateurs."
                    f"Répondez à cette question : '{user_query}' en utilisant toutes les données disponibles : {data}. "
                    f"Soyez utile, précis, et faites attention aux dates avant de répondre en le minimum des lignes. esseyer de chercher et calculer les bon reponse etulisant les information disponible."
                    f"be short as possible"
                )

            # Generate a response using Llama 3.2
            response = ollama.generate(model="llama3-chatqa", prompt=prompt_template)
            response_text = response["response"].replace("\n", " ")  # Clean and format response

        except sqlite3.OperationalError:
            response_text = "Erreur de base de données : la table Doc n'existe pas."
        except Exception as e:
            response_text = f"Erreur inattendue : {str(e)}"

        return jsonify(response=response_text)  # Return JSON formatted response
    
    return render_template('chatbot.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Userlog.query.filter_by(username='admin').first():
            admin = Userlog(username='admin', password='admin')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
    
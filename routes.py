from flask import Blueprint, request, render_template, redirect, url_for, flash
from app import db, User

home = Blueprint('home', __name__)

@home.route('/')
def base():
    return redirect(url_for('home.home'))

@home.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        try:
            # Extract form data
            user_data = {
                'matricule': request.form['matricule'],
                'nom_usuel': request.form['nom_usuel'],
                'prenom': request.form['prenom'],
                'date_de_naissance': request.form['date_de_naissance'],
                'date_d_entree': request.form['date_d_entree'],
                'situation_familiale': request.form['situation_familiale'],
                'echelle': request.form['echelle'],
                'date_debut_grade': request.form['date_debut_grade'],
                'echelon': request.form['echelon'],
                'date_d_effet': request.form['date_d_effet'],
                'sexe': request.form['sexe'],
                'etablissement': request.form['etablissement'],
                'numero_carte_identite': request.form['numero_carte_identite'],
                'numero_identificate_de_naissance': request.form['numero_identificate_de_naissance'],
                'numero_d_ordre': request.form['numero_d_ordre'],
                'prenom_identite': request.form['prenom_identite'],
                'sexe_identite': request.form['sexe_identite'],
                'date_de_naissance_identite': request.form['date_de_naissance_identite'],
                'tem_charge_saisie': request.form['tem_charge_saisie'],
                'situation_scolaire': request.form['situation_scolaire'],
                'sexe_scolaire': request.form['sexe_scolaire'],
                'identifiant_emploi': request.form['identifiant_emploi'],
                'annee_notation': request.form['annee_notation'],
                'notation_fin': request.form['notation_fin'],
                'rubrique': request.form['rubrique'],
                'montant_initial': request.form['montant_initial'],
                'nombre_echeances': request.form['nombre_echeances'],
                'solde': request.form['solde'],
                'date_debut': request.form['date_debut'],
                'date_fin': request.form['date_fin'],
                'code': request.form['code']
            }

            # Create a new user
            new_user = User(**user_data)
            db.session.add(new_user)
            db.session.commit()

            flash('User added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'danger')
        
        return redirect(url_for('home.home'))
    
    return render_template('add_user.html')

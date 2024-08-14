from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from database import db, Zak, Termin, Autoskola, Zaznam, Komisar, Zapsany_zak
from app_logic import porovnat_hesla
from hashlib import sha256

app = Flask(__name__) # Vytvoření instance pro web
app.config['SECRET_KEY'] = 'SecreT'

# Nastavení aplikace pro spoj s databází
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/resymost' # ://uživatel:heslo@kde_db_běží:port/název_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Spojení s databází

@app.route("/", methods=['GET', 'POST'])
def home():
    """
    Stránka slouží k přihlášení uživatelů

    Parametry:
        email (str): vstupní string při POST requestu.
        heslo (str): Vstupní string při POST requestu.
    
    Vrací:
        render_template("home.html"): html stránka, vracená při GET requestu.
        redirect(...): přesměrování na jiný endpoint při správném přihlášení zkoušejícího.
        redirect(...): přesměrování na jiný endpoint při správném přihlášení autoškoly.
        flash("message.html", message=error): při špatném přihlášení vrátí pouze zprávu. 
    """  
    if request.method == 'POST':
        email = request.form['login_email']
        heslo = request.form['login_heslo']
        if email.endswith('@mesto-most.cz'):
            cil = Komisar.query.filter_by(email=email).first()
            if cil:
                if porovnat_hesla(heslo, cil.heslo):
                    flash('Účet je v databázi', category='mess_success')
                else:
                    flash('Neplatný email nebo heslo', category='mess_error')
            else:
                flash('Neplatný email nebo heslo', category='mess_error')
        else:
            flash('Néééé', category='mess_error')

    return render_template('home.html')   

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return render_template('admin.html')
    if request.method == 'POST':
        pass

@app.route('/new_org')
def new_org():
    new_org = Komisar(email='heger.adam@mesto-most.cz', heslo=sha256('heslo123'.encode()).hexdigest(), jmeno='Adam', prijmeni='Heger')
    
    db.session.add(new_org)

    db.session.commit()

    return redirect(url_for('home'))
    

if __name__ == "__main__":
    app.run(debug=True)
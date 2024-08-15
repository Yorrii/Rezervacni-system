from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, Zak, Termin, Autoskola, Zaznam, Komisar, Zapsany_zak
import app_logic
from hashlib import sha256


app = Flask(__name__) # Vytvoření instance pro web
app.config['SECRET_KEY'] = 'Secret'

# Nastavení aplikace pro spoj s databází
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/resymost' # ://uživatel:heslo@kde_db_běží:port/název_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Spojení s databází
loginManager = LoginManager(app)
loginManager.login_view = 'home'


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
                if app_logic.porovnat_hesla(heslo, cil.heslo):
                    login_user(app_logic.User(cil.id))
                    flash('Přihlášený komisař', category='mess_success')
                    return redirect(url_for('calenar'))
                else:
                    flash('Neplatný email nebo heslo', category='mess_error')
            else:
                flash('Neplatný email nebo heslo', category='mess_error')
        else:
            cil = Autoskola.query.filter_by(email=email).first()
            if cil:
                if app_logic.porovnat_hesla(heslo, cil.heslo):
                    login_user(app_logic.User(cil.id))
                    flash('Přihlášená Autoškola', category='mess_success')
                    return redirect(url_for('calenar'))
                else:
                    flash('Neplatný email nebo heslo', category='mess_error')
            else:
                flash('Neplatný email nebo heslo', category='mess_error')

    return render_template('home.html')

@app.route('/calendar', methods=['GET'])
def calenar():
    return render_template('main_page.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return render_template('admin.html')
    if request.method == 'POST':
        pass

#API metody
@app.route('/create_autoskola', methods=['POST'])
def nova_autoskola():
    nazev = request.form['nazev']
    da_schranka = request.form['datova_schranka']
    email = request.form['email']
    heslo = sha256(request.form['heslo'].encode('utf-8')).hexdigest()
    try:
        autoskola = Autoskola(nazev=nazev, da_schranka=da_schranka,email=email, heslo=heslo)
        db.session.add(autoskola)
        db.session.commit()
    except:
        raise 'Někde je chyba'
    else:
        flash('Autoškola se přidala!', category='mess_success')
        return redirect(url_for('admin'))

    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@loginManager.user_loader
def load_user(user_id):
    return app_logic.User(user_id)

if __name__ == "__main__":
    app.run(debug=True)
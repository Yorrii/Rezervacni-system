from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, Zak, Termin, Autoskola, Zaznam, Komisar, Zapsany_zak
import app_logic
from hashlib import sha256


app = Flask(__name__) # Vytvoření instance pro web
app.config['SECRET_KEY'] = 'Secret'

# Nastavení aplikace pro spoj s databází
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/resymost2' # ://uživatel:heslo@kde_db_běží:port/název_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Spojení s databází
loginManager = LoginManager(app)
loginManager.login_view = 'home'

@app.route("/login", methods=['GET', 'POST'])
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
                    return redirect(url_for('calendar'))
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
                    return redirect(url_for('calendar'))
                else:
                    flash('Neplatný email nebo heslo', category='mess_error')
            else:
                flash('Neplatný email nebo heslo', category='mess_error')

    return render_template('home.html')

@app.route('/calendar', methods=['GET'])
@login_required
def calendar():
    return render_template('main_page.html')

@app.route('/term/<id>', methods=['GET', 'POST'])
@login_required
def term(id):
    """
    Stránka slouží k zápisu žáků na termín a přehled zapsaných žáků

    Parametry:
        id (str): id místnosti, která se má načíst

    Vrací:
        #TODO
    """
    termin = Termin.query.filter_by(id=id).first()

    if not termin: # podmínka zkontroluje jestli termín existuje
        abort(404)

    if not current_user.isAdmin:
        session['term_id'] = id

        match termin.ac_flag:
            case 'N': # pokud je termín neaktivní abort
                abort(404)
            case 'Y': # pokud je aktivní
                #TODO natahat si zapsané žáky, ukázat ty z naší autoškoly a nedovolit překročit limit

                zaci = Zapsany_zak.query \
                    .join(Zak) \
                    .join(Termin) \
                    .filter(Zapsany_zak.id_terminu == id, Zak.id_autoskoly == current_user.id) \
                    .all()
                
                zaci_data = []
                for item in zaci:
                    zaci_data.append({
                        'id': item.zak.id,
                        'typ_zkousky': item.typ_zkousky,
                        'druh_zkousky': item.druh_zkousky,
                        'ev_cislo': item.zak.ev_cislo,
                        'jmeno': item.zak.jmeno,
                        'prijmeni': item.zak.prijmeni,
                        'narozeni': item.zak.narozeni
                    })

                volna_mista = termin.max_ridicu - Zapsany_zak.query.filter_by(id_terminu=termin.id, potvrzeni='Y').count()
                print(volna_mista)

                return render_template('term.html', termin=termin, volna_mista=volna_mista,zaci=zaci_data)
            case 'R':
                pass #TODO
    
    elif current_user.isAdmin:
        match termin.ac_flag:
            case 'Y':

                zaci = Zapsany_zak.query \
                    .join(Zak) \
                    .join(Termin) \
                    .filter(Zapsany_zak.id_terminu == id) \
                    .all()
                
                zaci_v_as = {} # zde se jako klíče budou dávat id autoškol a hodnota bude list žáků
                for item in zaci:
                    autoskola = Autoskola.query.filter_by(id=item.zak.id_autoskoly).first()
                    if autoskola.nazev not in zaci_v_as:
                        zaci_v_as[autoskola.nazev] = [{     
                                                            'id': item.zak.id,                 
                                                            'ev_cislo': item.zak.ev_cislo,
                                                            'jmeno': item.zak.jmeno,
                                                            'prijmeni': item.zak.prijmeni,
                                                            'narozeni': item.zak.narozeni,
                                                            'typ_zkousky': item.typ_zkousky,
                                                            'druh_zkousky': item.druh_zkousky,
                                                            'potvrzeni': item.potvrzeni
                                                        }]
                    elif autoskola.nazev in zaci_v_as:
                         zaci_v_as[autoskola.nazev].append({
                                                            'id': item.zak.id,                 
                                                            'ev_cislo': item.zak.ev_cislo,
                                                            'jmeno': item.zak.jmeno,
                                                            'prijmeni': item.zak.prijmeni,
                                                            'narozeni': item.zak.narozeni,
                                                            'typ_zkousky': item.typ_zkousky,
                                                            'druh_zkousky': item.druh_zkousky,
                                                            'potvrzeni': item.potvrzeni
                                                        })

                srovnany_dict = dict(sorted(zaci_v_as.items()))
                return render_template('term_admin.html', list_as=srovnany_dict, termin=termin)
                             
            case 'N':
                pass
            case 'R':
                pass
        
    if request.method=='POST':
        return redirect(url_for('/'))
    return render_template('term.html', termin=termin)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """
    Endpoint pouze pro testování, v plné verzi odebrat
    """
    if request.method == 'GET':
        return render_template('admin.html')
    if request.method == 'POST':
        pass

#API metody
@app.route('/create_autoskola', methods=['POST'])
def nova_autoskola():
    """
    Vytvoří novou autoškolu
    """
    nazev = request.form['nazev']
    da_schranka = request.form['datova_schranka']
    email = request.form['email']
    heslo = sha256(request.form['heslo'].encode('utf-8')).hexdigest()
    try:
        autoskola = Autoskola(nazev=nazev, da_schranka=da_schranka,email=email, heslo=heslo)
        db.session.add(autoskola)
        db.session.commit()
    except:
        raise Exception()
    else:
        flash('Autoškola se přidala!', category='mess_success')
        return redirect(url_for('admin'))

@app.route('/create_komisar', methods=['POST'])
def novy_komisar():
    """
    Vytvoří nového komisaře
    """
    email = request.form['email']
    heslo = sha256(request.form['heslo'].encode('utf-8')).hexdigest()
    jmeno = request.form['jmeno']
    prijmeni = request.form['prijmeni']
    try:
        komisar = Komisar(email=email, heslo=heslo, jmeno=jmeno, prijmeni=prijmeni)
        db.session.add(komisar)
        db.session.commit()
    except:
        raise 'Někde je chyba'
    else:
        flash('Komisař se přidal!', category='mess_success')
        return redirect(url_for('admin'))

@app.route('/create_zak', methods=['POST'])
def novy_zak():
    """
    Vytvoří nového žáka
    """
    ev_cislo = request.form['ev_cislo']
    jmeno = request.form['jmeno']
    prijmeni = request.form['prijmeni']
    narozeni = request.form['narozeni']
    adresa = request.form['adresa']
    id_autoskoly = request.form['id_autoskoly']

    try:
        zak = Zak(ev_cislo=ev_cislo, jmeno=jmeno, prijmeni=prijmeni, narozeni=narozeni, adresa=adresa, id_autoskoly=id_autoskoly)
        db.session.add(zak)
        db.session.commit()
    except:
        raise 'Někde je chyba'
    else:
        flash('Žák se přidal!', category='mess_success')
        return redirect(url_for('admin'))    

@app.route('/create_termin', methods=['POST'])
def novy_termin():
    """
    Vytvoří nový termín žáka
    """
    datum = request.form['datum']
    max_ridicu = request.form['max_ridicu']

    try:
        termin = Termin(datum=datum, max_ridicu=max_ridicu)
        db.session.add(termin)
        db.session.commit()
    except:
        raise 'Někde je chyba'
    else:
        flash('Termín se přidal!', category='mess_success')
        return redirect(url_for('admin'))

@login_required
@app.route('/calendar_api', methods=['GET'])
def get_calendar_dates():
    # Simulace termínů, které máš v databázi
    events = [
        {"date": "2024-08-20"},
        {"date": "2024-08-22"},
        {"date": "2024-08-29"}
    ]
    return jsonify(events)

@login_required
@app.route('/add_drivers', methods=['POST'])
def add_drivers():
    try:
        # Získání dat ve formátu JSON
        data = request.get_json()
    
        # Zpracování dat
        for student in data:
            evidence_number = student.get('evidence_number')
            first_name = student.get('first_name')
            last_name = student.get('last_name')
            birth_date = student.get('birth_date')
            license_category = student.get('license_category')
            exam_type = student.get('exam_type').replace('_', ' ') # value se vrací ve tvaru něco_něco tak se mění '_' v ' '
            
            zak = Zak.query.filter_by(ev_cislo=evidence_number, jmeno=first_name, prijmeni=last_name,
                                    narozeni=birth_date, id_autoskoly=current_user.id).first()
            if zak:
                zapis = Zapsany_zak(typ_zkousky=license_category, druh_zkousky=exam_type,
                                    id_terminu=session.get('term_id'), id_autoskoly=current_user.id,id_zaka=zak.id)
                print('zak se zapsal')
                db.session.add(zapis)
                db.session.commit()
                return jsonify({"message": "Data přijata úspěšně"}), 200 # Odeslání odpovědi o úspěchu 
            else:
                return jsonify({"error": str(e)}), 400   
    except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400
    

@login_required
@app.route('/api/delete_student', methods=['POST'])
def delete_student():
    print('Jsem tu')
    data = request.get_json()
    zak_id = data.get('zak_id')
    termin_id = data.get('termin_id')
    
    # Najdi záznam v tabulce Zapsany_zak a smaž ho
    zapsany = Zapsany_zak.query.filter_by(id_zaka=zak_id, id_terminu=termin_id).first()
    
    if zapsany:
        db.session.delete(zapsany)
        db.session.commit()
        return jsonify({'message': 'Student smazán'}), 200
    else:
        return jsonify({'error': 'Student nenalezen'}), 404

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@loginManager.user_loader
def load_user(user_id):
    return app_logic.User(user_id)

if __name__ == "__main__":
    app.run(debug=True)
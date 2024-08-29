from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, Zak, Termin, Autoskola, Zaznam, Komisar, Zapsany_zak, Vozidlo
from sqlalchemy import or_
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
    Stránka slouží k zobrazení a zápisu žáků, k potvrzení zápisu, přidání času pro začátek, přidání komisaře k zápisu.
    Chování je rozdělené podle toho, jestli je přistupující user nebo admin.

    Parametry:
        id (str): id místnosti, která se má načíst

    Vrací:
        user:
        -----
            abort(404): při přístupu na neexistující termín nebo termín, který není ještě aktivní
            term.html:  pokud je termín aktivní('Y'), vrací se stránka, kde user může přihlásit žáky,
                        upravit přihlášené žáky nebo zobrazit si potvrzené žáky
        admin:
        -----
            term_admin.html: pokud je termín aktivní('Y') admin uvidí všechny zapsané žáky rozdělené podle autoškol,
                        zde jim může dodat zkoušejícího a začátek zkoušky a poté změnit jejich potvrzení na aktivní('Y')

    """
    termin = Termin.query.filter_by(id=id).first()

    if not termin: # podmínka zkontroluje jestli termín existuje
        abort(404)
    else:
        session['term_id'] = id #pokud termín existuje dáme ho do sessionu protože s ním budeme ještě pracovat

    if not current_user.isAdmin:
        

        match termin.ac_flag:
            case 'N': # pokud je termín neaktivní abort 
                abort(404)
            case 'Y': # pokud je aktivní
                zaci = Zapsany_zak.query \
                    .join(Zak) \
                    .join(Termin) \
                    .filter(Zapsany_zak.id_terminu == id, Zak.id_autoskoly == current_user.id, or_(Zapsany_zak.potvrzeni == 'Y', Zapsany_zak.potvrzeni == 'W')) \
                    .all()
                
                zaci_Y = []
                zaci_W = []
                for item in zaci:
                    if item.potvrzeni == 'Y':
                        zaci_Y.append({
                            'id': item.zak.id,
                            'typ_zkousky': item.typ_zkousky,
                            'druh_zkousky': item.druh_zkousky,
                            'ev_cislo': item.zak.ev_cislo,
                            'jmeno': item.zak.jmeno,
                            'prijmeni': item.zak.prijmeni,
                            'narozeni': item.zak.narozeni,
                            'potvrzeni': item.potvrzeni
                        })
                    if item.potvrzeni == 'W':
                        zaci_W.append({
                            'id': item.zak.id,
                            'typ_zkousky': item.typ_zkousky,
                            'druh_zkousky': item.druh_zkousky,
                            'ev_cislo': item.zak.ev_cislo,
                            'jmeno': item.zak.jmeno,
                            'prijmeni': item.zak.prijmeni,
                            'narozeni': item.zak.narozeni,
                            'potvrzeni': item.potvrzeni
                        })

                volna_mista = termin.max_ridicu - Zapsany_zak.query.filter_by(id_terminu=termin.id, potvrzeni='Y').count() - len(zaci_W)

                return render_template('term.html', termin=termin, volna_mista=volna_mista,zaci_Y=zaci_Y, zaci_W=zaci_W)
            case 'R':
                #TODO read-only, vrátí seznam studentů ze zkoušky, jejich časy a závěr
                zaci = Zapsany_zak.query \
                    .join(Zak) \
                    .join(Termin) \
                    .filter(Zapsany_zak.id_terminu == id, Zak.id_autoskoly == current_user.id, Zapsany_zak.potvrzeni == 'Y') \
                    .all()
                
                zaci = []
                for item in zaci:
                        zaci.append({
                            'id': item.zak.id,
                            'typ_zkousky': item.typ_zkousky,
                            'druh_zkousky': item.druh_zkousky,
                            'ev_cislo': item.zak.ev_cislo,
                            'jmeno': item.zak.jmeno,
                            'prijmeni': item.zak.prijmeni,
                            'narozeni': item.zak.narozeni,
                            'potvrzeni': item.potvrzeni,
                            'zaver': item.zaver,
                            'cas': item.zacatek
                        })
                return render_template('term_read.html', termin=termin, zaci=zaci)
                 
    elif current_user.isAdmin:
        match termin.ac_flag:
            case 'Y':
                # Vrátí všechny zapsané studenty, schromáždí je pod jejich autoškoly a zobrazí jestli jsou už přijmutí nebo ne!
                zaci = Zapsany_zak.query \
                    .join(Zak) \
                    .join(Termin) \
                    .filter(Zapsany_zak.id_terminu == id) \
                    .all()
                
                komisari = Komisar.query.all() #vrací list objektů Komisar
                
                zaci_v_as = {} # zde se jako klíče budou dávat název autoškol a hodnota bude list žáků
                for item in zaci:
                    autoskola = Autoskola.query.filter_by(id=item.zak.id_autoskoly).first()
                    komisar = next((k for k in komisari if k.id == item.id_komisare), None) 
                    if autoskola.nazev not in zaci_v_as:
                        zaci_v_as[autoskola.nazev] = [{     
                                                            'id': item.zak.id,                 
                                                            'ev_cislo': item.zak.ev_cislo,
                                                            'jmeno': item.zak.jmeno,
                                                            'prijmeni': item.zak.prijmeni,
                                                            'narozeni': item.zak.narozeni,
                                                            'typ_zkousky': item.typ_zkousky,
                                                            'druh_zkousky': item.druh_zkousky,
                                                            'potvrzeni': item.potvrzeni,
                                                            'komisar': f'{komisar.jmeno} {komisar.prijmeni}' if komisar else None,
                                                            'cas': item.zacatek
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
                                                            'potvrzeni': item.potvrzeni,
                                                            'komisar': f'{komisar.jmeno} {komisar.prijmeni}' if komisar else None,
                                                            'cas': item.zacatek
                                                        })

                srovnany_dict = dict(sorted(zaci_v_as.items()))
                return render_template('term_admin.html', list_as=srovnany_dict, termin=termin, komisari= komisari)
                

            case 'N':
                #TODO Upravit termín nebo zapsat žáky
                pass
            case 'R':
                #TODO zapsat a zobrazit závěr zkoušky
                pass
        
    if request.method=='POST':
        return redirect(url_for('/'))
    return render_template('term.html', termin=termin)

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():

    id = current_user.id
    skola = Autoskola.query.filter_by(id=id).first()
    seznam_vozidel =  Vozidlo.query.filter_by(id_autoskoly= current_user.id).all()
    return render_template('profil.html', vozidla= seznam_vozidel, autoskola=skola)

@app.route('/teaching_training', methods=['GET', 'POST'])
def teaching_training():
    #TODO: endpoint pro zápis řidičů žádajících o výuku a výcvik
    autoskola = Autoskola.query.filter_by(id=current_user.id).first()
    vozidla = Vozidlo.query.filter_by(id_autoskoly=current_user.id).all()

    return render_template('sign_up.html', vozidla=vozidla, autoskola=autoskola)

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
    API metoda pro vytvoření autoškoly, určená pro použití pouze během testování

    Parametry:
        request: myslím si, že se jedná o objekt, který v sobě přenáší JSON z formu pro informace o autoškole

    Vrací:
        Exception: pokud při vytvoření a nebo commitu do databáze vznikne error
        flash(str): při úspěšném přidání se vytvoří zpráva, která se zobrazí při dalším render_templatu
        redirect(url_for(str)): po přijmutí a vytvoření autoškoly vrátí uživatele zpátky na /admin
    """
    nazev = request.form['nazev']
    da_schranka = request.form['datova_schranka']
    adresa_u = request.form['adresa_ucebny']
    email = request.form['email']
    heslo = sha256(request.form['heslo'].encode('utf-8')).hexdigest()
    try:
        autoskola = Autoskola(nazev=nazev, da_schranka=da_schranka, adresa_u=adresa_u, email=email, heslo=heslo)
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
    API metoda pro vytvoření komisaře, určená pro použití pouze během testování

    Parametry:
        request: myslím si, že se jedná o objekt, který v sobě přenáší JSON z formu pro informace o komisaři

    Vrací:
        raise (str): pokud při vytvoření a nebo commitu do databáze vznikne error
        flash(str): při úspěšném přidání se vytvoří zpráva, která se zobrazí při dalším render_templatu
        redirect(url_for(str)): po přijmutí a vytvoření komisaře vrátí uživatele zpátky na /admin
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
    API metoda pro vytvoření žáka, určená pro použití pouze během testování

    Parametry:
        request: myslím si, že se jedná o objekt, který v sobě přenáší JSON z formu pro informace o žákovi

    Vrací:
        str: pokud při vytvoření a nebo commitu do databáze vznikne error
        flash(str): při úspěšném přidání se vytvoří zpráva, která se zobrazí při dalším render_templatu
        redirect(url_for(str)): po přijmutí a vytvoření autoškoly vrátí uživatele zpátky na /admin
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
    API metoda pro vytvoření termínu, určená pro použití pouze během testování

    Parametry:
        request: myslím si, že se jedná o objekt, který v sobě přenáší JSON z formu pro informace o termínu

    Vrací:
        str: pokud při vytvoření a nebo commitu do databáze vznikne error
        flash(str): při úspěšném přidání se vytvoří zpráva, která se zobrazí při dalším render_templatu
        redirect(url_for(str)): po přijmutí a vytvoření autoškoly vrátí uživatele zpátky na /admin
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
def get_calendar_dates(): #TODO
    """
    API bude vracet informace o termínech aby se zobrazili v kalendáři

    """
    events = [
        {"date": "2024-08-20"},
        {"date": "2024-08-22"},
        {"date": "2024-08-29"}
    ]
    return jsonify(events)

@login_required
@app.route('/add_drivers', methods=['POST'])
def add_drivers():
    """
    API metoda pro vytvoření autoškoly, určená pro použití pouze během testování

    Parametry:
        request: myslím si, že se jedná o objekt, který v sobě přenáší JSON z formu pro informace o autoškole

    Vrací:
        Exception: pokud při vytvoření a nebo commitu do databáze vznikne error
        flash(str): při úspěšném přidání se vytvoří zpráva, která se zobrazí při dalším render_templatu
        redirect(url_for(str)): po přijmutí a vytvoření autoškoly vrátí uživatele zpátky na /admin
    """
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
@app.route('/enroll', methods=['POST'])
def enroll_drivers():
    try:
        # Získání dat ve formátu JSON
        data = request.get_json()
        
        # Zpracování dat
    
        id_studenta = data.get('id')
        time_start = data.get('time_start')
        id_commissar = data.get('commissar')
        
        zak = Zak.query.filter_by(id= id_studenta).first()
        if zak:
            zapis = Zapsany_zak.query.filter_by(id_terminu=session.get('term_id'), id_zaka=id_studenta).first()
            zapis.potvrzeni = 'Y'
            zapis.zacatek = time_start
            zapis.id_komisare = id_commissar
            print('zak se zapsal na termín')
            
            db.session.commit()
            return jsonify({"message": "Data přijata úspěšně"}), 200 # Odeslání odpovědi o úspěchu 
        else:
            return jsonify({"error": str(e)}), 400   
    except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400   

@login_required
@app.route('/api/add_vehicle', methods=['POST'])
def add_vehicle():
    znacka= request.form['znacka']
    model= request.form['model']
    spz= request.form['spz']
    #try:
    vozidlo = Vozidlo(znacka=znacka, model=model, spz=spz, id_autoskoly= current_user.id)
    db.session.add(vozidlo)
    db.session.commit()
    #except:
    #    raise Exception
    #else:
    return redirect(url_for('profil'))

@login_required
@app.route('/api/delete_student', methods=['POST'])
def delete_student():
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
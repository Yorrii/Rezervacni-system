from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, abort, session #mikrorámec na routování a celkovou správu webu
from flask_login import LoginManager, login_user, logout_user, login_required, current_user #podpůrná knihovna na správu přihlášených uživatelů
from flask_mail import Mail, Message #podúůrná knihovna na posílání emailů
from database import db, Zak, Termin, Autoskola, Zaznam, Komisar, Zapsany_zak, Vozidlo, Upozorneni #ORM modely na komunikaci s databází
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature #knihovna na generování tokenů. Kontrola, jestli není token 'prošlí' a je autentický 'neupravený'.
from sqlalchemy import or_ #metoda na možnost or v quary
from docx import Document #Objekt, který generuje word dokument z kódu
import app_logic #soubor s metodamy
from config import Config #nastavení pro posílání emailů
from hashlib import sha256  #hashovací metoda
from datetime import date, datetime


app = Flask(__name__) # Vytvoření instance pro web
app.config['SECRET_KEY'] = 'Secret' #TODO zmenit klíc!!!

# Nastavení aplikace pro spoj s databází
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/resymost2' # ://uživatel:heslo@kde_db_běží:port/název_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.from_object(Config) # Nastavení na připojení na email server
db.init_app(app) # Spojení s databází
loginManager = LoginManager(app) # Instance spravuje přihlášené uživatele
mail = Mail(app) # Instance na posílaní mailů
loginManager.login_view = 'home'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY']) # instance objektu, který vytváří token na resetování a vytváření hesla

@app.route("/login", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
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
    if request.method == 'POST': # při POST requestu
        email = request.form['login_email'] # načte si email
        heslo = request.form['login_heslo'] # načte si string z formu pro heslo
        if email.endswith('@mesto-most.cz'): # kontrolo jestli email nekončí @mesto-most.cz pro admina
            cil = Komisar.query.filter_by(email=email).first()  # podle emailu se najde komisař
            if cil:
                if app_logic.porovnat_hesla(heslo, cil.heslo): # tady se porovná heslo z databáze a hashovaná forma zadaného hesla
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

@app.route('/zapomenute_heslo', methods=['GET', 'POST'])
def forgotten_password():
    """
    Stránka slouží k resetování zapomenutého hesla. Uživatel zadá email, pokud se email najde v DB pošle se na něj odkaz s tokenem
    na jiný endpoint, kde si heslo bude moci změnit.

    Parametry:
        email (str): vstupní string při POST requestu.
    
    Vrací:
        render_template("zapomenute_heslo.html"): html stránka, vracená při GET requestu.
        redirect(calendar): přesměrování na jiný endpoint pokud je uživatel přihlášený.
        redirect(home): přesměrování na jiný endpoint, pokud se v DB najde email.
        #TODO flash("message.html", message=error): při špatném přihlášení vrátí pouze zprávu. 
    """
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))
    
    if request.method == 'GET':
        return render_template('zapomenute_heslo.html')
    
    if request.method == 'POST':
        email = request.form['email']
        if email.endswith('@mesto-most.cz'): # kontrolo jestli email nekončí @mesto-most.cz pro admina
            cil = Komisar.query.filter_by(email=email).first() # pokud jo, tak se ho pokusí najít
        else:
            cil = Autoskola.query.filter_by(email=email).first() # pokud ne, tak ho hledá v autoškolách
        
        if cil: # pokud to najde komisaře nebo i autoškolu
            token = serializer.dumps(email, salt='8na5YMzlD1A32xS1m') # vytvoří token z emailu a solí
            reset_url = url_for('reset_password', token=token, _external=True) # vytvoří odkaz na resetování hesla

            msg = Message(
                subject="Resetování hesla",
                sender='Rezervační systém Most',
                recipients=[str(email)],
                body=f'Klikněte na tento odkaz pro resetování hesla: {reset_url}',
                html=f'<p>Klikněte na tento odkaz pro resetování hesla:</p><a href="{reset_url}">Resetovat heslo</a>'
            )    
            try:
                mail.send(msg)
                flash('Email s odkazem na resetování hesla byl poslán.', category='success')
                return redirect(url_for('home'))
            except Exception as e:
                flash(f'Email se nepodařilo odeslat. Prosím, kontaktujte Magistrát města Most.', category='error')
                return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route('/resetovat/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='8na5YMzlD1A32xS1m', max_age=7200) # token se rozbalí, pokud bude "prošlí" vyhodí SignatureExpired, pokud bude token změněn vyhodí BadSignature
        if request.method == 'GET': # Pokud je token v pořádku a request je GET
            return render_template('reset_hesla.html')
        
        if request.method == 'POST': 
            nove_heslo= request.form['password'] # heslo z formuláře při POST          
            if email.endswith('@mesto-most.cz'): # kontrola jak končí email aby se hledalo ve správné tabulce
                komisar = Komisar.query.filter_by(email=email).first()
                komisar.heslo = sha256(nove_heslo.encode('utf-8')).hexdigest()
                db.session.commit()
                return redirect(url_for('home'))
            else:
                autoskola = Autoskola.query.filter_by(email=email).first()
                autoskola.heslo = sha256(nove_heslo.encode('utf-8')).hexdigest()
                db.session.commit()
                return redirect(url_for('home'))
            
    except SignatureExpired: # Pokud vyprší platnost tokenu
        return 'Nestihnul jsi to'
    except BadSignature: # Token je neplatný nebo byl změněn (např. útok nebo modifikace)
        abort(404)

@app.route('/nove_heslo/<token>', methods=['GET', 'POST'])
def create_password(token):
    try:
        email = serializer.loads(token, salt='8na5YMzlD1A32xS1m', max_age=172800) # token je platný dva dny



    except SignatureExpired: # Pokud vyprší platnost tokenu
        return 'Nestihnul jsi to'
    except BadSignature: # Token je neplatný nebo byl změněn (např. útok nebo modifikace)
        abort(404)    

@app.route('/calendar', methods=['GET'])
@login_required
def calendar():
    if current_user.isAdmin:
        return render_template('main_page.html')
    else:
        return render_template('main_page_user.html')

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
                            'potvrzeni': item.potvrzeni,
                            'cas': item.zacatek
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
                
                zaci_s = []
                for item in zaci:
                        zaci_s.append({
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
                return render_template('term_read.html', termin=termin, zaci=zaci_s)
                 
    elif current_user.isAdmin:
        volna_mista = termin.max_ridicu - Zapsany_zak.query.filter_by(id_terminu=termin.id, potvrzeni='Y').count()
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
                return render_template('term_admin.html', list_as=srovnany_dict, termin=termin, komisari= komisari, volna_mista= volna_mista)
                

            case 'N':
                #TODO Upravit termín nebo zapsat žáky
                """
                V případě, že je termín stále neaktivní, admin by měl mít možnost od něj zapsat studenty sám bez
                zásahu autoškoly. Tudíž v tomto případě je potřeba dostat žáky, kteří jsou již zapsaní, čekají na zápis
                a formuláře pro zapsaní žáků.
                """
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
                volna_mista = termin.max_ridicu - len([zak for zak in zaci if zak.potvrzeni == 'Y'])
                return render_template('zapis_studenta_adminem.html', termin=termin, list_as=srovnany_dict, komisari=komisari, volna_mista=volna_mista)
            case 'R':
                #TODO zapsat a zobrazit závěr zkoušky
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
                                                            'cas': item.zacatek,
                                                            'zaver': item.zaver
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
                                                            'cas': item.zacatek,
                                                            'zaver': item.zaver
                                                        })                   
                srovnany_dict = dict(sorted(zaci_v_as.items()))
                return render_template('term_conclusion.html', list_as=srovnany_dict, termin=termin, komisari= komisari)
            
    if request.method=='POST':
        return redirect(url_for('/'))
    return render_template('term.html', termin=termin)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    id = current_user.id
    skola = Autoskola.query.filter_by(id=id).first()
    seznam_vozidel =  Vozidlo.query.filter_by(id_autoskoly= current_user.id).all()
    return render_template('profile.html', vozidla= seznam_vozidel, autoskola=skola)

@app.route('/new_driving_school', methods=['GET', 'POST'])
@login_required
def new_driving_school():
    if not current_user.isAdmin:
        abort(404)
    if request.method == 'POST':
        #TODO tady by se měla vytvořit autoškola, měl by se jí poslat email s vytvořením hesla a manuálem
        nazev = request.form.get('nazev')
        dat_schranka = request.form.get('email')
        email =  request.form.get('email')
        
        autoskola = Autoskola.query.filter_by(email=email).first()

        if not autoskola:
            nova_autoskola = Autoskola(nazev=nazev, da_schranka=dat_schranka, email=email)
            db.session.add(nova_autoskola)
            db.session.commit()

            flash('Nová autoškola přidána', category='success')

            token = serializer.dumps(email, salt='8QLlZzV5TtW1Rfb') # vytvoří token z emailu a solí
            newPassword_url = url_for('create_password', token=token, _external=True) # vytvoří odkaz na resetování hesla

            msg = Message(
                subject="Odkaz na vytvoření hesla",
                sender='Rezervační systém Most',
                recipients=[str(email)],
                body=f'Klikněte na tento odkaz bude přesměrováni na stránku pro vytvoření hesla: {newPassword_url}',
                html=f'<p>Klikněte na tento odkaz pro vytvoření hesla:</p><a href="{newPassword_url}">Vytvořit heslo</a>'
            )    
            try:
                mail.send(msg)
                flash('Email s odkazem na resetování hesla byl poslán.', category='success')
                return redirect(url_for('home'))
            except Exception as e:
                flash(f'Email se nepodařilo odeslat. Prosím, kontaktujte Magistrát města Most.', category='error')
                return redirect(url_for('home'))

        flash('Nová autoškola přidána', category='success')
        return render_template('new_driving_school.html')
    
    if request.method == 'GET':
        return render_template('new_driving_school.html')

@app.route('/teaching_training', methods=['GET', 'POST'])
@login_required
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

@app.route('/logs', methods= ['GET', 'POST'])
@login_required
def logs():
    """
    Stránka slouží k zobrazení logů autoškoly. Bude přístupná pouze komisařům. Po prvním načtení si komisař vybere, které logy chce
    vidět, od jaké autoškoly. Pošle POST request, endpoint vyhledá logy v db a vrátí je.

    Vrací:
        Abort(404): Pokud user není admin
        html
    """
    if not current_user.isAdmin:
        abort(404)

    autoskoly = Autoskola.query.all()
        # Pokud přibudou typy záznamu tak je můžeme zjistit takhle: druhy_zaznamu = [choice for choice in Zaznam.druh.type.enums]
    lst_as = []
    for autoskola in autoskoly:
        lst_as.append({'id':autoskola.id,
                        'nazev':autoskola.nazev})

    if request.method == 'GET':
        return render_template('logs.html', autoskoly=lst_as)
    
    if request.method == 'POST':
        id_as = request.form.get('autoskola') or None
        druh = request.form.get('druh') or None
        datum = request.form.get('datum') or None

        quary = Zaznam.query # Tady se přípravý quary, které potom budu doplňovat podle parametrů

        if id_as:
            quary = quary.filter(Zaznam.id_autoskoly == id_as)
        if druh:
            quary = quary.filter(Zaznam.druh == druh)
        if datum:
            quary = quary.filter(Zaznam.kdy >= datum)

        quary.limit(100) # limit na počet záznamů
        zaznamy = quary.all()

        lst_zaznamy= []
        for zaznam in zaznamy:
            lst_zaznamy.append({
                'kdy': zaznam.kdy,
                'druh': zaznam.druh,
                'zprava': zaznam.zprava,
                'autoskola': zaznam.autoskola.nazev
            })
            
        return render_template('logs.html', logs=lst_zaznamy, autoskoly=lst_as)

#TODO API metody
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
    heslo = sha256(request.form['heslo'].encode('utf-8')).hexdigest() # heslo se zahashuje
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
@app.route('/api/create_term', methods=['POST'])
def vytvor_termin():
    data = request.get_json()

    try:
        print(data.get('dayId'), data.get('pocetMist'))
        termin = Termin(datum=data.get('dayId'), max_ridicu=data.get('pocetMist'))
        db.session.add(termin)
        db.session.commit()
        return redirect(url_for('calendar'))
    except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400
    
@login_required
@app.route('/calendar_api', methods=['GET'])
def get_calendar_dates():
    """
    API bude vracet informace o termínech aby se zobrazili v kalendáři

    """
    if current_user.isAdmin:
        terminy = Termin.query.all()
        
        # Serializace dat
        terminy_list = []
        for termin in terminy:
            termin_data = {
                'id': termin.id,
                'date': termin.datum.isoformat(),  # datum převedeme na string ve formátu ISO
                'ac_flag': termin.ac_flag,
                'max_ridicu': termin.max_ridicu,
                'zapsani_zaci': len(termin.zapsani_zaci)  # Příklad jak zahrnout počet zapsaných žáků
            }
            terminy_list.append(termin_data)
        return jsonify(terminy_list)
    if not current_user.isAdmin:
        # Dotaz pro aktivní termíny (ac_flag = 'Y')
        aktivni_terminy = db.session.query(Termin).filter(Termin.ac_flag == 'Y').all()
        
        # Dotaz pro ukončené termíny (ac_flag = 'R') s žáky z konkrétní autoškoly
        ukoncene_terminy = db.session.query(Termin)\
            .join(Zapsany_zak)\
            .filter(Termin.ac_flag == 'R', Zapsany_zak.id_autoskoly == current_user.id)\
            .all()

        # Spojíme aktivní i ukončené termíny dohromady
        terminy = aktivni_terminy + ukoncene_terminy

        # Příprava dat pro frontend ve formátu JSON
        terminy_data = []
        for termin in terminy:
            terminy_data.append({
                "id": termin.id,
                "date": termin.datum.isoformat(),
                "ac_flag": termin.ac_flag,
                "max_ridicu": termin.max_ridicu,
            })
        
        return jsonify(terminy_data)

@login_required
@app.route('/add_drivers', methods=['POST'])
def add_drivers():
    """
    API metoda pro zápis řidičů na termín AUTOŠKOLOU. Přijme data, ty projde a podle nich vytvoří záznam v DB.

    Parametry:
        request: JSON objekt, který v sobě nese informace o žácích

    Vrací:
        Exception: pokud při vytvoření a nebo commitu do databáze vznikne error
        jsonify(dic): při úspěšném přidání se vrací zpráva s kódem 200(successful request)
        redirect(url_for(str)): po přijmutí a vytvoření autoškoly vrátí uživatele zpátky na /admin
    """
    try:
        # Získání dat ve formátu JSON
        data = request.get_json()
        print(data)
        # Zpracování dat
        for student in data:
            print(student)
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
                zaznam = Zaznam(druh='zápis', kdy=datetime.now(),
                                zprava=f'Autoškola přidala studentku/studenta {first_name} {last_name} {evidence_number} na termín s id: {session.get('term_id')}',
                                id_autoskoly=current_user.id)
                print('zak se zapsal')
                db.session.add(zapis)
                db.session.add(zaznam)
                db.session.commit() 
        return jsonify({"message": "Data přijata úspěšně"}), 200 # Odeslání odpovědi o úspěchu
    except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400

@login_required
@app.route('/api/enroll_by_admin', methods=['POST'])
def enroll_by_admin():
    """
    API metoda pro zapsání žáka od ADMINA na termín, který je zatím neaktivní! 

    Parametry:
        request: myslím si, že se jedná o objekt, který v sobě přenáší JSON z formu pro informace o termínu

    Vrací:
        str: pokud při vytvoření a nebo commitu do databáze vznikne error
        flash(str): při úspěšném přidání se vytvoří zpráva, která se zobrazí při dalším render_templatu
        redirect(url_for(str)): po přijmutí a vytvoření autoškoly vrátí uživatele zpátky na /admin
    """
    #TODO udělat záznamy pro autoškolu i komisaře
    try:
        data = request.get_json()

        for student in data:
            evidence_number = student.get('evidence_number')
            first_name = student.get('first_name')
            last_name = student.get('last_name')
            birth_date = student.get('birth_date')
            license_category = student.get('license_category')
            exam_type = student.get('exam_type').replace('_', ' ') # value se vrací ve tvaru něco_něco tak se mění '_' v ' '
            
            zak = Zak.query.filter_by(ev_cislo=evidence_number, jmeno=first_name, prijmeni=last_name,
                                    narozeni=birth_date).first()
            if zak:
                zapis = Zapsany_zak(typ_zkousky=license_category, druh_zkousky=exam_type,
                                    id_terminu=session.get('term_id'), id_autoskoly=zak.id_autoskoly,id_zaka=zak.id)
                db.session.add(zapis)
                db.session.commit()
            else:
                print('Něco se nevyšlo')
                return jsonify({"error": str(e)}), 400
        return jsonify({"message": "Data přijata úspěšně"}), 200 # Odeslání odpovědi o úspěchu
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
        termin = Termin.query.filter_by(id=session.get('term_id')).first()
        if zak:
            zapis = Zapsany_zak.query.filter_by(id_terminu=session.get('term_id'), id_zaka=id_studenta).first()
            zapis.potvrzeni = 'Y'
            zapis.zacatek = time_start
            zapis.id_komisare = id_commissar
            print('zak se zapsal na termín')
            upozorneni= Upozorneni(zprava= f'Studentka/Student {zak.jmeno} {zak.prijmeni} {zak.ev_cislo} byl/a zapsán/a na termín {termin.datum} v {time_start}',
                                   id_autoskoly= zak.id_autoskoly, datum_vytvoreni=datetime.now())
            db.session.add(upozorneni)
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
    return redirect(url_for('profile'))

@login_required
@app.route('/api/delete_student', methods=['POST'])
def delete_student():
    data = request.get_json()
    zak_id = data.get('zak_id')
    termin_id = data.get('termin_id')
    
    # Najdi záznam v tabulce Zapsany_zak a smaž ho
    zapsany = Zapsany_zak.query.filter_by(id_zaka=zak_id, id_terminu=termin_id).filter(Zapsany_zak.potvrzeni.in_(['W', 'N'])).first()
    zak = Zak.query.filter_by(id=zak_id).first()
    zaznam = Zaznam(druh='odpis', kdy=datetime.now(),
                    zprava=f'Autoškola odebrala studentku/studenta {zak.jmeno} {zak.prijmeni} {zak.ev_cislo} z termínu s id: {session.get('term_id')}',
                    id_autoskoly=current_user.id)
    db.session.add(zaznam)

    if zapsany:
        db.session.delete(zapsany)
        db.session.commit()
        return jsonify({'message': 'Student smazán'}), 200
    else:
        print(f'Nebylo nalezeno zapsání {zak_id} {termin_id}')
        return jsonify({'error': 'Student nenalezen'}), 404

@login_required
@app.route('/api/sign_up', methods=['POST'])
def docx_for_signup():
    """
    API metoda, která vytvoří dokument o zápisu studentů. Zapsané studenty přidá do databáze. 

    Parametry:
        request: JSON soubor s novými studenty, adresou učebny, typem výuky, vozidli pro výuku

    Vrací:
        str: pokud při vytvoření a nebo commitu do databáze vznikne error
        str: pokud vše proběhne v pořádku
        docx: dokument o žádost zápisu studentů do výuky a výcviku
    """
    if True:
        data = request.get_json() #data z POST requestu

        autoskola = Autoskola.query.filter_by(id=current_user.id).first() # data o autoškole, potřebuju jméno pro ukládání

        adresa = data['main_form']['adress'] # adresa účebny
        datum = data['main_form']['start_of_training'] # datum začátku výcviku
        seznam_vozidel = data['main_form']['vehicle_list'] # seznam vozidel k výcviku
        seznam_studentu = data['students'] # seznam studentů do výcviku
        print(adresa, datum, seznam_vozidel, seznam_studentu)
        document = Document() # docx dokument

        document.add_heading('Seznam řidičů žádajících o zařazení do výuky a výcviku', 0) # nadpis

        p = document.add_paragraph('A plain paragraph having some ')
        p.add_run('bold').bold = True
        p.add_run(' and some ')
        p.add_run('italic.').italic = True

        document.add_heading('Heading, level 1', level=1)
        document.add_paragraph('Intense quote', style='Intense Quote')

        # vytvoření tabulky a sloupců s názvem
        table = document.add_table(rows=1, cols=7)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Evidenčí číslo'
        hdr_cells[1].text = 'Jméno'
        hdr_cells[2].text = 'Přijmení'
        hdr_cells[3].text = 'Datum narození'
        hdr_cells[4].text = 'Adresa'
        hdr_cells[5].text = 'Číslo řidičského průkazu'
        hdr_cells[6].text = 'Druh výcviku'
        for student in seznam_studentu: # cykl pro studenty, aby se zapsali do tabulky a zároveň jejich tvorba do db
            row_cells = table.add_row().cells
            row_cells[0].text = student['evidence_number']
            row_cells[1].text = student['first_name']
            row_cells[2].text = student['last_name']
            row_cells[3].text = student['birth_date']
            row_cells[4].text = student['adress']
            row_cells[5].text = student['drivers_license'] if student['drivers_license'] else ' '
            row_cells[6].text = student['type_of_teaching'].replace('-', ' ')

            # Tady se vytvoří žák a uloží se do db
            zak = Zak(ev_cislo=student['evidence_number'],jmeno=student['first_name'],prijmeni=student['last_name'],
                      narozeni=student['birth_date'],adresa=student['adress'],id_autoskoly= current_user.id)
            zaznam = Zaznam(druh='přidání', kdy=datetime.now(),
                            zprava=f'Autoškola zapsala studentku/studenta {student['first_name']} {student['last_name']} {student['evidence_number']} do výuky a výcviku.',
                            id_autoskoly=current_user.id)
            db.session.add(zaznam)
            db.session.add(zak)
            
        db.session.commit()
        document.add_page_break()

        document.save(f'Zapis_studentu/{autoskola.nazev}_{date.today().strftime("%d-%m-%Y")}.docx') # ukládání dokumentu
        return jsonify({"message": "Data přijata úspěšně"}), 200   
    """except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400"""

@login_required
@app.route('/api/success', methods=['POST'])
def student_success():
    """
    API metoda, která slouží pro zápis úspěchu studenta na zkoušce. 

    Parametry:
        request: JSON soubor s id studenta, který uspěl.

    Vrací:
        str: error, když dojede k chybě nebo když neexistuje termín nebo žák
        str: pokud vše proběhne v pořádku
    """
    if not current_user.isAdmin:
        abort(404)
    try:
        # Získání dat ve formátu JSON
        data = request.get_json()
        
        # Zpracování dat
        id_studenta = data.get('id')
        
        zak = Zak.query.filter_by(id = id_studenta).first()
        termin = Termin.query.filter_by(id = session.get('term_id')).first()
        if zak and termin:
            zapis = Zapsany_zak.query.filter_by(id_terminu=session.get('term_id'), id_zaka=id_studenta).first()
            print(f'{zak.jmeno} {zak.prijmeni} uspěl na zkoušce {termin.datum} :)')
            zapis.zaver = 'Y'
            upozorneni= Upozorneni(zprava= f'Studentka/Student {zak.jmeno} {zak.prijmeni} {zak.ev_cislo} úspěšně splnil termín.',
                                   id_autoskoly= zak.id_autoskoly)
            db.session.add(zapis)
            db.session.add(upozorneni)
            db.session.commit()
            
            return jsonify({"message": "Data přijata úspěšně"}), 200 # Odeslání odpovědi o úspěchu 
        else:
            return jsonify({"error": str(e)}), 400   
    except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400    

@login_required
@app.route('/api/reject', methods=['POST'])
def student_reject():
    """
    API metoda, která slouží k zápisu neúspěchu při zkoušce. 

    Parametry:
        request: JSON soubor s id žáka

    Vrací:
        str: error, pokud se nenajde žák nebo termín nebo pokud dojde k nějaké chybě
        str: 200, pokud vše proběhne v pořádku
        abort: 404 pokud user není admin, jelikož k metodě by měl mít přístup pouze admin
    """
    if not current_user.isAdmin:
        abort(404)
    try:
        # Získání dat ve formátu JSON
        data = request.get_json()
        
        # Zpracování dat
        id_studenta = data.get('id')
        
        zak = Zak.query.filter_by(id= id_studenta).first()
        termin = Termin.query.filter_by(id = session.get('term_id')).first()
        if zak and termin:
            zapis = Zapsany_zak.query.filter_by(id_terminu=session.get('term_id'), id_zaka=id_studenta).first()
            print(f'{zak.jmeno} {zak.prijmeni} neuspěl na zkoušce {termin.datum} :(')
            zapis.zaver = 'N'
            upozorneni= Upozorneni(zprava= f'Studentka/Student {zak.jmeno} {zak.prijmeni} {zak.ev_cislo} neuspěl u termínu.',
                                   id_autoskoly= zak.id_autoskoly)
            db.session.add(upozorneni)
            db.session.add(zapis)
            db.session.commit()
            
            return jsonify({"message": "Data přijata úspěšně"}), 200 # Odeslání odpovědi o úspěchu 
        else:
            return jsonify({"error": str(e)}), 400   
    except Exception as e:
        # Pokud nastane chyba, odeslat chybovou zprávu
        return jsonify({"error": str(e)}), 400    

@login_required
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        upozorneni_list = Upozorneni.query.filter_by(id_autoskoly=current_user.id)\
                                      .order_by(Upozorneni.datum_vytvoreni.desc())\
                                      .limit(10)\
                                      .all()
        lst = []
        for upozorneni in upozorneni_list:
            lst.append({
            'zprava': upozorneni.zprava,
            'stav': upozorneni.stav
            })
        
        return jsonify(lst), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@loginManager.user_loader
def load_user(user_id):
    return app_logic.User(user_id)

if __name__ == "__main__":
    app.run(debug=True)
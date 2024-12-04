from flask_sqlalchemy import SQLAlchemy

# Vytvoření instance pro spojení s databází
db=SQLAlchemy()

class Zak(db.Model):
    """
    Třída Zak je model reprezentující tabulku žáci v DB
    """
    __tablename__ = 'zaci'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor žáka."""
    ev_cislo = db.Column('evidencni_cislo', db.String(30), nullable=False)
    """ev_cislo (str): Evidenční číslo žáka."""
    jmeno = db.Column('jmeno', db.String(30), nullable=False)
    """jmeno (str): Jméno žáka."""
    prijmeni = db.Column('prijmeni', db.String(30), nullable=True)
    """prijmeni (str): Přijmení žáka."""
    narozeni = db.Column('datum_narozeni', db.Date, nullable=True)
    """narozeni (str): Datum narození žáka."""
    adresa = db.Column('adresa', db.String(255), nullable=True)
    """adresa (str): Adresa bydliště."""
    splnil = db.Column('splnil', db.Boolean, default=False, nullable=False)
    """splnil (bool): Určuje, zda žák splnil požadavky. Výchozí hodnota je False."""
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)
    """id_autoskoly (int): Cizý klíč odkazující na autoškolu do které žák patří."""


class Termin(db.Model):
    """
    Třida Termin je model reprezentující tabulku terminy v DB
    """
    __tablename__ = 'terminy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor termínu."""
    datum = db.Column('datum', db.Date, nullable=False)
    """datum (str): Datum konání termínu."""
    ac_flag = db.Column('active_flag', db.Enum('Y', 'N', 'R'), default='N', nullable=True)
    """ac_flag (str): Reprezentuje, jestli je termín aktivní, neaktivní nebo již proběhl."""
    max_ridicu = db.Column('max_ridicu', db.SmallInteger, nullable=True)
    """max_ridicu (int): Kolik je maximální počet míst na termínu."""
    zapsani_zaci = db.relationship('Zapsany_zak', backref='termin', lazy=True)
    """zapsani_zaci (list): Seznam žáků spojených s tímto termínem."""

class Autoskola(db.Model):
    """
    Třída Autoskola je model reprezentující tabulku autoskoly v DB
    """
    __tablename__ = 'autoskoly'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor autoškoly."""
    nazev = db.Column('nazev', db.String(50), nullable=True)
    """nazev (str): Název autoškoly."""
    da_schranka = db.Column('datova_schranka', db.String(100), nullable=True)
    """da_schranka (str): Datová schránka autoškoly."""
    email = db.Column('email', db.String(70), nullable=True)
    """email (str): E-mailová adresa autoškoly."""
    heslo = db.Column('heslo', db.String(70), nullable=True)
    """heslo (str): Heslo autoškoly, šifrované."""
    adresa_u = db.Column('adresa_ucebny', db.String(100), nullable=True)
    """adresa_u (str): Adresa učebny autoškoly."""
    zaci = db.relationship('Zak', backref='autoskola', lazy=True)
    """zaci (list): Seznam žáků spojených s touto autoškolou."""
    zaznamy = db.relationship('Zaznam', backref='autoskola', lazy=True)
    """zaznamy (list): Seznam záznamů spojených s touto autoškolou."""


class Komisar(db.Model):
    """
    Třída Komisar je model reprezentující tabulku Komisari v DB 
    """
    __tablename__ = 'komisari'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor komisaře."""
    email = db.Column('email', db.String(70), nullable=True)
    """email (str): Email komisaře."""
    heslo = db.Column('heslo', db.String(70), nullable=True)
    """heslo (str): Zašifrované heslo komisaře."""
    jmeno = db.Column('jmeno', db.String(70), nullable=True)
    """jmeno (str): Jméno komisaře."""
    prijmeni = db.Column('prijmeni', db.String(70), nullable=True)
    """prijmeni (str): Přijmení komisaře."""
    isAdmin = db.Column('isAdmin', db.DateTime, nullable=True)
    """isAdmin (str): Datum, do kdy má komisař adminská práva."""


class Superadmin(db.Model):
    """
    Třída Superadmin je model reprezentující tabulku Superadmini v DB
    """
    __tablename__ = 'Superadmini'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor superadmina."""
    email = db.Column('email', db.String(70), nullable=True)
    """email (str): Email superadmina."""
    heslo = db.Column('heslo', db.String(70), nullable=False)
    """heslo (str): Zašifrované heslo superadmina."""
    jmeno = db.Column('jmeno', db.String(70), nullable=True)
    """jmeno (str): Jméno superadmina."""
    prijmeni = db.Column('prijmeni', db.String(70), nullable=True)
    """prijmeni (str): Přijmení superadmina."""


class Zapsany_zak(db.Model):
    """
    Třída Zapsany_zak je model reprezentující tabulku zapsani_zaci v DB
    """
    __tablename__ = 'zapsani_zaci'

    potvrzeni = db.Column('potvrzeni', db.Enum('Y', 'N', 'W'), default='W', nullable=True)
    """potvrzeni (str): Stav, jestli je žák přihlášený na termín, čeká nebo je zamítnut."""
    typ_zkousky = db.Column('typ_zkousky', db.Enum('A', 'B', 'C', 'C+E', 'D', 'D+E', 'T'), nullable=True)
    """typ_zkousky (str): Třída řidičského oprávnění, kterou bude žák podstupovat."""
    druh_zkousky = db.Column('druh_zkousky', db.Enum('Řádná zkouška', 'Opravná zkouška-test+jízda', 'Opravná zkouška-jízda', 'Opravná zkouška-technika', 'Opravná zkouška-technika+jízda', 'Profesní způsobilost-test'), nullable=True)
    """druh_zkousky (str): O jaký druh zkoušky se jedná."""
    zaver = db.Column('zaver', db.Enum('Y', 'N', 'W'), default='W',nullable=True)
    """zaver (str): Jak se žákovy na zkoušce dařilo."""
    id_terminu = db.Column('id_terminu', db.Integer, db.ForeignKey('terminy.id'), nullable=True)
    """id_terminu (int): Cizý klíč odkazující na termín."""
    id_komisare = db.Column('id_komisare', db.Integer, db.ForeignKey('komisari.id'), nullable=True)
    """id_komisare (int): Cizý klíč odkazující na komisaře, který žáka zkoušel."""
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=True)
    """id_autoskoly (int): Cizý klíč odkazující na autoškolu, do které žák patří."""
    id_zaka = db.Column('id_zaka', db.Integer, db.ForeignKey('zaci.id'), nullable=True)
    """id_zaka (int): Cizý klíc odkazujíci na žáka."""
    zacatek = db.Column('zacatek', db.Time, nullable=True)
    """zacatek (str): Čas, kdy se má žák dostavit."""
    __table_args__ = (
        db.PrimaryKeyConstraint('id_terminu', 'id_zaka'),
    )
    zak = db.relationship('Zak', backref='zapsani', lazy=True)
    """zak (obj): Objekt žáka."""
    komisar = db.relationship('Komisar', backref='zapsani', lazy=True)
    """komisar (obj): Objekt komisaře."""
    autoskola = db.relationship('Autoskola', backref='zapsani', lazy=True)
    """autoskola (obj): Objekt autoškoly."""

class Zaznam(db.Model):
    """
    Třída Zaznam je model reprezentující tabulku zaznamy v DB        
    """
    __tablename__ = 'zaznamy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor záznamu."""
    druh = db.Column('druh', db.Enum('zápis', 'odpis', 'přidání', 'odebrání', 'přihlásil se', 'odhlásil se'), nullable=True)
    """druh (str): O jaký druh(zápis, přidání, atd...) záznamu se jedná."""
    kdy = db.Column('kdy', db.DateTime, nullable=True)
    """kdy (str): Čas, kdy záznam vznikl."""
    zprava = db.Column('zprava', db.Text, nullable=True)
    """zprava (str): Obsah záznamu pro výstup."""
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=True)
    """id_autoškoly (int): Cizý klíč odkazující na autoškoly, která záznam vytvořila."""

class Vozidlo(db.Model):
    """
    Třída Vozidlo je model reprezentující tabulku Vozidla v DB
    """
    __tablename__ = 'vozidla'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor vozidla."""
    znacka = db.Column('znacka', db.String(100), nullable=False)
    """znacka (str): Značka vozidla."""
    model = db.Column('model', db.String(100), nullable=False)
    """model (str): Model vozidla."""
    spz = db.Column('spz', db.String(10))
    """spz (str): RZ vozidla."""
    id_autoskoly = db.Column('id_autoskoly',db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)
    """id_autoškoly (int): Cizý klíč odkazující na autoškolu."""

class Upozorneni(db.Model):
    """
    Třída Upozorneni je model reprezentující tabulku Upozorneni v DB
    """
    __tablename__ = 'Upozorneni'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """id (int): Primární klíč tabulky, unikátní identifikátor upozornění."""
    zprava = db.Column(db.String(200), nullable=False)
    """zprava (str): Text, který upozornění nese."""
    datum_vytvoreni = db.Column(db.DateTime)
    """datum_vytvoreni (str): Datum, kdy upozornění vzniklo."""
    stav = db.Column(db.Enum('Y', 'N'), default='N')
    """stav (str): Stav, jestli bylo upozornění přečtené nebo ne."""
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)
    """id_autoskoly (str): Cizý klíč odkazující na autoškolu, pro kterou toto upozornění platí."""
from flask_sqlalchemy import SQLAlchemy

# Vytvoření instance pro spojení s databází
db=SQLAlchemy()

class Zak(db.Model):
    """
    Třída Zak je model reprezentující tabulku žáci v DB
    """
    __tablename__ = 'zaci'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ev_cislo = db.Column('evidencni_cislo', db.String(30), nullable=False)
    jmeno = db.Column('jmeno', db.String(30), nullable=False)
    prijmeni = db.Column('prijmeni', db.String(30), nullable=True)
    narozeni = db.Column('datum_narozeni', db.Date, nullable=True)
    adresa = db.Column('adresa', db.String(255), nullable=True)
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)

    #autoskola = db.relationship('Autoskola', backref='zaci', lazy=True)


class Termin(db.Model):
    """
    Třida Termin je model reprezentující tabulku terminy v DB
    """
    __tablename__ = 'terminy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datum = db.Column('datum', db.Date, nullable=False)
    ac_flag = db.Column('active_flag', db.Enum('Y', 'N', 'R'), default='N', nullable=True)
    max_ridicu = db.Column('max_ridicu', db.SmallInteger, nullable=True)

    zapsani_zaci = db.relationship('Zapsany_zak', backref='termin', lazy=True)


class Autoskola(db.Model):
    """
    Třída Autoskola je model reprezentující tabulku autoskoly v DB
    """
    __tablename__ = 'autoskoly'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nazev = db.Column('nazev', db.String(50), nullable=True)
    da_schranka = db.Column('datova_schranka', db.String(100), nullable=True)
    email = db.Column('email', db.String(70), nullable=True)
    heslo = db.Column('heslo', db.String(70), nullable=True)
    adresa_u = db.Column('adresa_ucebny', db.String(100), nullable=True)

    zaci = db.relationship('Zak', backref='autoskola', lazy=True)
    zaznamy = db.relationship('Zaznam', backref='autoskola', lazy=True)


class Komisar(db.Model):
    """
    Třída Komisar je model reprezentující tabulku Komisari v DB
    """
    __tablename__ = 'komisari'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column('email', db.String(70), nullable=True)
    heslo = db.Column('heslo', db.String(70), nullable=True)
    jmeno = db.Column('jmeno', db.String(70), nullable=True)
    prijmeni = db.Column('prijmeni', db.String(70), nullable=True)
    isAdmin = db.Column('isAdmin', db.DateTime, nullable=True)


class Superadmin(db.Model):
    """
    Třída Komisar je model reprezentující tabulku Komisari v DB
    """
    __tablename__ = 'Superadmini'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column('email', db.String(70), nullable=True)
    heslo = db.Column('heslo', db.String(70), nullable=False)


class Zapsany_zak(db.Model):
    """
    Třída Zapsany_zak je model reprezentující tabulku zapsani_zaci v DB
    """
    __tablename__ = 'zapsani_zaci'

    potvrzeni = db.Column('potvrzeni', db.Enum('Y', 'N', 'W'), default='W', nullable=True)
    typ_zkousky = db.Column('typ_zkousky', db.Enum('A', 'B', 'C', 'C+E', 'D', 'D+E', 'T'), nullable=True)
    druh_zkousky = db.Column('druh_zkousky', db.Enum('Řádná zkouška', 'Opravná zkouška-test+jízda', 'Opravná zkouška-jízda',
                                                     'Opravná zkouška-technika', 'Opravná zkouška-technika+jízda', 'Profesní způsobilost-test'),
                                                     nullable=True)
    zaver = db.Column('zaver', db.Enum('Y', 'N', 'W'), default='W',nullable=True)
    id_terminu = db.Column('id_terminu', db.Integer, db.ForeignKey('terminy.id'), nullable=True)
    id_komisare = db.Column('id_komisare', db.Integer, db.ForeignKey('komisari.id'), nullable=True)
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=True)
    id_zaka = db.Column('id_zaka', db.Integer, db.ForeignKey('zaci.id'), nullable=True)
    zacatek = db.Column('zacatek', db.Time, nullable=True)

    __table_args__ = (
        db.PrimaryKeyConstraint('id_terminu', 'id_zaka'),
    )

    zak = db.relationship('Zak', backref='zapsani', lazy=True)
    komisar = db.relationship('Komisar', backref='zapsani', lazy=True)
    autoskola = db.relationship('Autoskola', backref='zapsani', lazy=True)

class Zaznam(db.Model):
    """
    Třída Zaznam je model reprezentující tabulku zaznamy v DB
    """
    __tablename__ = 'zaznamy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    druh = db.Column('druh', db.Enum('zápis', 'odpis', 'přidání', 'odebrání', 'přihlásil se', 'odhlásil se'), nullable=True)
    kdy = db.Column('kdy', db.DateTime, nullable=True)
    zprava = db.Column('zprava', db.Text, nullable=True)
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=True)


class Vozidlo(db.Model):
    __tablename__ = 'vozidla'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    znacka = db.Column('znacka', db.String(100), nullable=False)
    model = db.Column('model', db.String(100), nullable=False)
    spz = db.Column('spz', db.String(10))
    id_autoskoly = db.Column('id_autoskoly',db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)


class Upozorneni(db.Model):
    __tablename__ = 'Upozorneni'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zprava = db.Column(db.String(200), nullable=False)
    datum_vytvoreni = db.Column(db.DateTime)
    stav = db.Column(db.Enum('Y', 'N'), default='N')
    
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)
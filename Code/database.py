from flask_sqlalchemy import SQLAlchemy

# Vytvoření instance pro spojení s databází
db=SQLAlchemy()

class Zak(db.Model):
    """
    Třída Zak je model reprezentující tabulku žáci v DB
    """
    __tablename__ = 'zaci'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ev_cislo = db.Column('evidencni_cislo', db.String(255), nullable=False)
    jmeno = db.Column('jmeno', db.String(255), nullable=False)
    prijmeni = db.Column('prijmeni', db.String(255), nullable=False)
    narozeni = db.Column('datum_narozeni', db.Date, nullable=False)
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=False)

    def __repr__(self):
        return f'<Zaci {self.jmeno} {self.prijmeni}>'


class Termin(db.Model):
    """
    Třida Termin je model reprezentující tabulku terminy v DB
    """
    __tablename__ = 'terminy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datum = db.Column('datum', db.Date, nullable=False)
    ac_flag = db.Column('active_flag', db.Enum('Y', 'N'), default='N', nullable=True)
    max_ridici = db.Column('max_ridici', db.SmallInteger, nullable=True)


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


class Zapsany_zak(db.Model):
    """
    Třída Zapsany_zak je model reprezentující tabulku zapsani_zaci v DB
    """
    __tablename__ = 'zapsani_zaci'

    potvrzeni = db.Column('potvrzeni', db.Enum('Y', 'N', 'W'), default='W', nullable=True)
    typ_zkousky = db.Column('typ_zkousky', db.Enum('A', 'B', 'C', 'C+E', 'D', 'D+E', 'T'), nullable=True)
    stav_zkousky = db.Column('stav_zkousky', db.Enum('Řádná zkouška', 'Opravná zkouška-test+jízda', 'Opravná zkouška-jízda',
                                                     'Opravná zkouška-technika', 'Opravná zkouška-technika+jízda', 'Profesní způsobilost-test'),
                                                     nullable=True)
    zaver = db.Column('zaver', db.Enum('Y', 'N', 'W'), default='W',nullable=True)
    id_terminu = db.Column('id_terminu', db.Integer, db.ForeignKey('terminy.id'), nullable=True)
    id_komisare = db.Column('id_komisare', db.Integer, db.ForeignKey('komisari.id'), nullable=True)
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=True)
    id_zaka = db.Column('id_zaka', db.Integer, db.ForeignKey('zaci.id'), nullable=True)

    __table_args__ = (
        db.PrimaryKeyConstraint('id_terminu', 'id_zaka'),
    )


class Zaznam(db.Model):
    """
    Třída Zaznam je model reprezentující tabulku zaznamy v DB
    """
    __tablename__ = 'zaznamy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    druh = db.Column('druh', db.Enum('zápis', 'odpis', 'přidání', 'odebrání'), nullable=True)
    kdy = db.Column('kdy', db.DateTime, nullable=True)
    zprava = db.Column('zprava', db.Text, nullable=True)
    id_autoskoly = db.Column('id_autoskoly', db.Integer, db.ForeignKey('autoskoly.id'), nullable=True)
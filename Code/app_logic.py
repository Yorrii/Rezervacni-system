import hashlib
from flask_login import UserMixin


def porovnat_hesla(heslo, db_heslo):
    """
    Metoda slouží k porovnání hesel

    Parametry:
        heslo (str): heslo, které uživatel zadá při přihlašování na webové stránce
        db_heslo (str): heslo, které se vezme z databáze podle zadaného emailu.

    Vrací:
        True (boolean): pokud jsou oba stringy stejné
        False (boolean): pokud jsou stringy odlišné
    """
    return True if hashlib.sha256(heslo.encode('utf-8')).hexdigest() == db_heslo else False

class User(UserMixin):
    def __init__(self, id, isAdmin=False):
        self.id = id
        if int(self.id) > 1000000: # pokud je superadmin
            self.isSuperAdmin = True
            self.isCommissar = True
            self.isAdmin = True
        elif int(self.id) > 100000: # pokud je komisař
            self.isSuperAdmin = False 
            self.isCommissar = True
            self.isAdmin = isAdmin # pokud má admin práva
        else: # pro autoškolu
            self.isSuperAdmin = False
            self.isCommissar = False
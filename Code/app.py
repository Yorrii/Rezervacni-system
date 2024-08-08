from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # Vytvoření instance pro web
db = SQLAlchemy() # Vytvoření instance pro spojení s databází
# Nastavení aplikace pro spoj s databází
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/test1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Spojení s databází

class Zaci(db.Model):
    __tablename__ = 'žáci'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jmeno = db.Column('jméno', db.String(255), nullable=False)
    prijmeni = db.Column('přijmení', db.String(255), nullable=False)
    narozeni = db.Column('narození', db.Date, nullable=False)
    rodne = db.Column('rodné', db.String(255), nullable=False)
    id_autoskoly = db.Column('id_autoškoly', db.Integer, db.ForeignKey('autoškoly.id'), nullable=False)

    def __repr__(self):
        return f'<Zaci {self.jmeno} {self.prijmeni}>'



@app.route("/")
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
    zak = Zaci.query.get(3)
    return jsonify({
        'id': zak.id,
        'jmeno': zak.jmeno,
        'prijmeni': zak.prijmeni,
        'narozeni': str(zak.narozeni),
        'rodne': zak.rodne,
        'id_autoskoly': zak.id_autoskoly
    })

if __name__ == "__main__":
    app.run(debug=True)
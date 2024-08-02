from flask import Flask, render_template

app = Flask(__name__)

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
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
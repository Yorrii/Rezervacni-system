# TODO

## App

### FIXME
    - odebrat endpoint /admin před nasazením
    - Dokumentace
    - Udělat requirements
    - zajistit licence

### BUGI

### Uživatel
    - logování
    - v záznamech pro malé rozlišení text přetéká
    
### Admin 
    - (api metodu, která vytvoří novou školu), udělá pro ní dočasné heslo, pošle ho na vybraný email spolu s manuálem
    - css
### Dodělat
    - py -m pdoc --output-dir Code/templates/dokumentace Code/app Code/app_logic Code/database
    - pokud zadám termín bez místa, tak se i tak propíše do db
    
### 11.03.2025
    - přenastavit dobu aktivace termínů na tři týdny |DONE| 
    - do 'R' termínu přidat možnost zapsat žáka |DONE|
    - Možnost smazat žáka v den termínu(vedle úspěch/neúspech přidat tlačítko, které ho smaže) |DONE|
    - přidat možnost do VaV (opakovaný výcvik, opakovaná výuka) a u těhle možností nevytvářet nového žáka |DONE|
    - Při vytváření nové autoškoly pohrát si s adresou. Myslím si, že by bylo dobré, kdybych udělal nějaký oddělovač(', '). |DONE| 
    - Sloupeček s prvním nesplněným termínem |DONE|

### 21.03.2025
    - udělat konec výuky |D|
    - změnit skupinu na na input místo selectu |D|
    - do VaV přidat první pokus |D|
    - opravit nadpisy sloupců |D|


### Dodělat
    - v term_admin.html chybí kontrolo vstupu pro třídu řidič. oprávnění   
    - udělám normálně kontrolu jestli první pokus > 1 rok, pokud ano tak vytvořím záznam a žáka smažu
    - přesunout nějaké důležité styly do ostatních zobrazení
    - autoškola - při konci výcviku jde vynechat typ oprávnění
    - superadmin - v 'R' termínu je pořád select místo inputu pro třídu ř. opr.

### Poslední den
    - mazaní studentů po roce
    - styly pro telefony
    - vymazat data, upravit db
    - nahrát poslední změny
    
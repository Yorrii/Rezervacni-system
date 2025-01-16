# TODO

## App

### FIXME
    - odebrat endpoint /admin před nasazením
    - Dokumentace
    - Udělat requirements
    - zajistit licence

### BUGI
    SD - Autoškola může zapsat na termín více, než je volný počet míst(i když je termín plný, může přidat žáky po jednom)
    - Komisař může na termín povolit více, než je počet volných míst.
    - Pokud se při VaV nebo přihlášení na zkoušku nechá jeden řádek prázdný, tak je problém.
    - V DB může vzniknout duplikát jenom s jiným id. Kontrolovat jestli už žák s takovým E.č. je v autoškole pokud ano, nenechat zapsat.
    - pokud komisař odepíše studenta z termínu, vytvoří se upozornění se špatným formátem data 

### Uživatel
    - upravit profil(vozidla, učebny), správa vozidel
    - logování
    - v záznamech pro malé rozlišení text přetéká
    
### Admin 
    - (api metodu, která vytvoří novou školu), udělá pro ní dočasné heslo, pošle ho na vybraný email spolu s manuálem
    - css
    D - upravit navbar u 'R' termínů
### Dodělat
    D ale neotestováno - udělat výuku a výcvik i pro komisaře
    - udělat ukládání souborů pro výuku a výcvik tak aby se nepřepisovali soubory
    - py -m pdoc --output-dir Code/templates/dokumentace Code/app Code/app_logic Code/database
    - pokud zadám termín bez místa, tak se i tak propíše do db

### 04.12.2024
    D? - předělat zapisovací formulář na zkoušku (chtějí vybrat autoškolu, napsat e.č. a zbytek se doplní sám, pak si jen dopíšou komisaře, druh zkoušky a čas)
    - ve VaV přepsat kolonku, kde se píše adresa účebny tak, aby se zobrazovala účebna z DB.

### Next server update
    - přidat do templatu odkaz na styly pro malé a střední displaye
    - přidat soubor stylů pro menší displaye
    - upravit JS script_calendar, přidal jsem omezení na počet žáků při vytváření termínu
    - pro nějaké html stránky byla přidána classa, primárně pro grid 8
    
    
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
    D - SUPERADMIN - bude moct dávat práva komisařům na nějakou dobu, koukat na logy komisařů, zápis komisaře a času k termínu
    D ale neotestováno - udělat výuku a výcvik i pro komisaře
    D - jenom zelené a červené termíny | Stejně jsem zůstal u 3 barev (zelená aktivní a neaktivní termíny, červená plné, modrá proběhlé)
    D - Pokud komisař někoho zapíše na termín udělat dokument | udělat tlačítko na okno pro autoškolu, které tento dokument udělá
    D - SPZ - RZ
    D - skupina ve VaV
    D - dopsat do mailu info
    D - přidat form na zápis žáků adminem pro termíny v term_admin a term_komisar
    - udělat ukládání souborů pro výuku a výcvik tak aby se nepřepisovali soubory
    D - přidat superadminovi možnost upravovat profili autoškol
    - py -m pdoc --output-dir Code/templates/dokumentace Code/app Code/app_logic Code/database

### 04.12.2024
    D - dodělat tlačítko na odevrání studenta když už je zapsaný (třeba z důvodu nemoci)
    D - dodělat profil
    D - sepsat requirementy(D) a licence
    D - přidat vlaječku jestli student už uspěl u zkoušky
    - předělat zapisovací formulář na zkoušku (chtějí vybrat autoškolu, napsat e.č. a zbytek se doplní sám, pak si jen dopíšou komisaře, druh zkoušky a čas)
    - ve VaV přepsat kolonku, kde se píše adresa účebny tak, aby se zobrazovala účebna z DB.

    
    
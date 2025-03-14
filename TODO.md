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

### 04.12.2024
    - ve VaV přepsat kolonku, kde se píše adresa účebny tak, aby se zobrazovala účebna z DB.

### Next server update
    - přidat soubor stylů pro menší displaye
    - upravit JS script_calendar, přidal jsem omezení na počet žáků při vytváření termínu
    - pro nějaké html stránky byla přidána classa, primárně pro grid 8
    
### 11.03.2025
    - přenastavit dobu aktivace termínů na tři týdny |DONE| 
    - do 'R' termínu přidat možnost zapsat žáka
    - Možnost smazat žáka v den termínu(vedle úspěch/neúspech přidat tlačítko, které ho smaže)
    - přidat možnost do VaV (opakovaný výcvik, opakovaná výuka) a u těhle možností nevytvářet nového žáka
    - Při vytváření nové autoškoly pohrát si s adresou. Myslím si, že by bylo dobré, kdybych udělal nějaký oddělovač(', ').
    - Při zapisování žáka na termín, udělat kolonku pro první termín(nepovinná).
    - Sloupeček s prvním nesplněným termínem
    
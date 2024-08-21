# TODO

## App

### FIXME
    - odebrat endpoint /admin před nasazením
    - předělat Api /add_drivers do /term/<id> protože v api chybí id termínu, nebo termín uložit do sessionu

### Uživatel
    - endpointy pro zápis na termíny, profil(vozidla, učebny), správa vozidel, stránka se žádostí o zápis, úprava termínů, na které se přihlásí
    - logování
    - dokončit databázi
    - udělat zvoneček

### Admin
    - endpoint pro změnu termínů, přehled zapsaných a přidání komisaře a času, zapsat autoškolu a studenty na termín, přehled logů
    - dodělat kalendář + js
    - css
    - udělat aborter


## Databáze
    - udělat rutiny
    - udělat eventy(změna active_flagů pro termíny v následujících 14 dnech)
    - u některých flagů přidat další možnost (read only)
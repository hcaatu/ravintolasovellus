# Ravintolasovellus

Tämän repositorion sovellus toimii Helsingin Yliopiston Tietokannat ja Web-ohjelmointi -kurssin harjoitustyönä.

Sovellus on yksinkertainen tietokantasovellus PostgreSQL:n avulla, jossa voi arvostella ja lukea lähialeen kuppiloiden tuotteita ja palvelua. 

Tarkoituksena on luoda ominaisuuksia, kuten
- sisäänkirjautuminen ja omien tietojen tarkastelu
- ravintolan tietojen tarkastelu
- arvion antaminen tietylle ravintolalle
- lista- tai karttanäkymä kuppiloista

## Välipalautus 2:
- sovellukseen voi lisätä uusia ravintoloita
- sovellukseen voi luoda uusia käyttäjiä
- käyttäjät voivat jättää arvioita ravintoloihin
- käyttäjät voivat poistaa arvionsa
- arvioita voi etsiä hakusanalla

Sovellus on tällä hetkellä fly.io:n palvelimella, mutta en ole saanut vielä kaikkia ongelmia ratkaistua siihen liittyen. En siis saanut palvelua toimimaan vielä tähän palautukseen saakka. Kurssin ohjeet liittyen siihen olivat ilmeisesti vanhentuneet. 

Sovelluksen saa kuitenkin käynnistettyä paikallisesti.

### Asennusohje

1. Kloonaa repositorio paikalliselle koneelle:
```bash
git clone
```

2. Hakemistoon voi siirtyä komennolla:
```bash
cd ravintolasovellus
```

3. Luo kansioon .env tiedosto
```bash
touch .env
```
Tiedostoon tulee kirjoittaa seuraaat rivit:


DATABASE_URL=*tietokannan-paikallinen-osoite*

SECRET_KEY=*salainen-avain*


johon vaihdetaan oikeat muuttujat paikalle. Salaisen avaimen saa luotua esimerkiksi juurihakemistossa komennolla:
```bash
python3 secret.py
```

4. Aktivoidaan virtuaaliympäristö ja asennetaan sovelluksen riippuvuudet seuraavilla komennoilla:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Määritetään vielä sovelluksen tietokannan skeema komennolla:
```bash
psql < schema.sql
```

6. Nyt sovelluksen voi käynnistää komennolla
```bash
flask run
```

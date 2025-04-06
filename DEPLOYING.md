
Tvá webová aplikace **ArteModerno** je e-shop postavený na **Flasku** a **SQLAlchemy**, kde prodáváš umělecké produkty. Máš v ní mimo jiné:

- systém **košíku** (přidávání, mazání, rekapitulace),
    
- **objednávky** s PDF fakturami,
    
- **slevové kódy**,
    
- **uživatelské profily** a přehled objednávek,
    
- **admin dashboard** pro správu produktů, uživatelů i objednávek,
    
- **email notifikace**,
    
- **AI agenta**, kterého propojuješ přes API,
    
- a aktuálně řešíš **multijazyčnost** a **překlady**.
    

Takže klidně pokračuj – co budeme dneska v ArteModerno upravovat? 💻✨

4o

##### Řekl/a jsi:

ok jak moc složité jí bude deploy live a jaké problémy můžu očekávat

###### ChatGPT řekl:

Výborná otázka, Fido! 🧠 Nasazení (deployment) tvé aplikace **ArteModerno** na produkci _živě_ je velký krok, ale zvládnutelný – zvlášť když už to máš celé funkční v debug režimu. Níže ti rozepíšu **hlavní možnosti**, **doporučení**, **potenciální problémy** a **co zkontrolovat před deployem**:

---

## 🔧 KROK ZA KROKEM: CO POTŘEBUJEŠ K LIVE NASAZENÍ

### 1. **Zvol platformu**

Nejčastější možnosti pro Flask:

|Hosting|Výhody|Nevýhody|
|---|---|---|
|**Render**|Snadné nasazení, free plán, Git integrace|Omezené prostředky, studený start|
|**Railway**|Free tier, jednoduchý deploy|Méně dokumentace pro Flask|
|**VPS (např. DigitalOcean)**|Plná kontrola (Gunicorn + Nginx)|Více práce, ruční správa serveru|
|**Heroku**|Snadný deploy, Git podpora|Nutný Heroku buildpack, free plán zrušen|

Pro začátek doporučuji **Render** nebo **Railway**, pokud nechceš řešit infrastrukturu. Pro maximální kontrolu je ale nejlepší VPS.

---

### 2. **Zkontroluj před nasazením**

-  `DEBUG = False` v `config.py`
    
-  Vygenerovaný **secret key**
    
-  Bezpečná konfigurace `SQLALCHEMY_DATABASE_URI` – produkční DB
    
-  Email funguje i na produkci (ověření SMTP)
    
-  Ošetřený **CSRF** (už máš přes Flask-WTF ✅)
    
-  Veškeré `print()` → přesuň do loggeru nebo odstraň
    
-  Logování chyb (např. Sentry nebo basic logging)
    
-  Statické soubory správně načítané (včetně `app/static/`)
    

---

### 3. **Nejčastější problémy po nasazení**

|Problém|Řešení|
|---|---|
|❌ App se nenačítá, 500 error|Chybí `.env`, špatný path, špatný import (např. relativní vs absolutní)|
|📦 Neinstalované moduly|Zkontroluj `requirements.txt`|
|🗂️ Statické soubory nejsou vidět|Zkontroluj `static_folder` a `url_for('static', ...)`|
|🔐 Problém s CSRF nebo session|SECRET_KEY není nastaven|
|📧 E-maily nefungují|SMTP blokován, špatná konfigurace|
|🧾 PDF generace padá|Chybí fonty nebo obrázky (zkontroluj cesty!)|
|🌍 Jazykové přepínače nefungují|Zkontroluj `lang` prop a JSON překlady|

---

## ✅ DOPORUČENÍ

- Měj vlastní `config.py` s třídami `DevelopmentConfig` a `ProductionConfig`
    
- Odděl sensitive údaje do `.env` a načítej přes `python-dotenv`
    
- Zkontroluj timeouty (např. PDF generace nebo scraping)
    
- Pokud používáš **PostgreSQL**, ověř, že `psycopg2` běží i na serveru
    
- Ujisti se, že tvůj AI agent není vázaný na localhost, ale podporuje CORS a má správné URL
    

---

Chceš-li, můžu ti připravit:

1. **Checklist PDF ke stažení**
    
2. **Hotový `config.py` pro prod + dev**
    
3. **Render.yaml nebo Dockerfile pro VPS**
    
4. Pomoc s **konkrétní platformou** podle toho, co si vybereš
    

---

Co z toho chceš jako první? Nebo rovnou nasadíme na Render?
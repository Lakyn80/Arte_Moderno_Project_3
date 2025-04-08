# Tento soubor slouží jako plán a dokumentace pro rozčlenění route logiky do modulů.

# ====== PLÁNOVANÁ STRUKTURA MODULŮ A ROUTES ======

app/
├ views/                    # Klientské funkce (frontend, login, profil)
│  ├ __init__.py
│  ├ home_routes.py          # Domůvská stránka, galerie
│  ├ auth_routes.py          # Registrace, login, logout
│  ├ profile_routes.py       # Profil uživatele
│  ├ contact_routes.py       # Kontaktní formulář
│  ├ reset_routes.py         # Reset hesla klienta
│  ├ orders_routes.py        # Moje objednávky (detail, faktura, e-mail)
│  ├ language_routes.py      # Změna jazyka
│  └ views_init_routes.py    # Blueprint registrace views (pokud potřeba)

├ admin/
│  ├ __init__.py
│  ├ admin_dashboard.py      # Admin dashboard + produkty
│  ├ admin_auth.py           # Admin login, reset
│  ├ admin_orders.py         # Admin objednávky + detail + export
│  ├ admin_users.py          # Detail uživatele
│  ├ admin_discounts.py      # Slevové kupony

├ cart/
│  ├ __init__.py
│  ├ cart_routes.py          # Zobrazení košíku, přidání, odebrání
│  ├ cart_discount_routes.py # Sleva, odstranění slevy
│  ├ cart_api_routes.py       # /api/cart/* REST API

├ checkout/
│  ├ __init__.py
│  ├ checkout_routes.py       # Rekapitulace a potvrzení objednávky

# Každý modul obsahuje svůj vlastní Blueprint a je registrován v app/__init__.py
# Struktura db models, forms a pdf_generator zůstane stejná

# ====== DALŠÍ KROKY ======
# 1. Rozdělit routes podle tohoto plánu do jednotlivých souborů
# 2. Vytvořit blueprint registraci v app/__init__.py
# 3. Otestovat jednotlivé route importy a view funkce
# 4. Ošetřit circular imports (pozor na db, mail, bcrypt atd.)

# Tento plán je zcela univerzální a vhodný i pro další projekty.

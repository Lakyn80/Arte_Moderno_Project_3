import os
import re

BASE_DIR = os.path.join("app")  # hlavní složka projektu
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
ROUTES_DIR = os.path.join(BASE_DIR, "routes")

template_re = re.compile(r"render_template\(['\"](.*?)['\"]")
url_for_static_re = re.compile(r"url_for\(['\"]static['\"],\s*filename=['\"](.*?)['\"]")
url_for_any_re = re.compile(r"url_for\(['\"](.*?)['\"]")

templates_used = set()
statics_used = set()
endpoints_used = set()

print("🔍 Prohledávám soubory ve složkách /routes a /templates...\n")

# Projdi soubory .py ve složce routes
for root, _, files in os.walk(ROUTES_DIR):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file), encoding="utf-8") as f:
                content = f.read()
                templates_used.update(template_re.findall(content))
                statics_used.update(url_for_static_re.findall(content))
                endpoints_used.update(url_for_any_re.findall(content))

# Projdi šablony a vyhledej další statické soubory a url_for
for root, _, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith(".html"):
            with open(os.path.join(root, file), encoding="utf-8") as f:
                content = f.read()
                statics_used.update(url_for_static_re.findall(content))
                endpoints_used.update(url_for_any_re.findall(content))

# Výpis výsledků
print("✅ Použité HTML šablony:")
for tpl in sorted(templates_used):
    print(f"  - {tpl}")

print("\n✅ Odkazy na statické soubory:")
for stat in sorted(statics_used):
    print(f"  - {stat}")

print("\n✅ Použitá url_for volání (endpoints):")
for ep in sorted(endpoints_used):
    print(f"  - {ep}")

print("\n📌 Zkontroluj, jestli všechny uvedené šablony a statické soubory fyzicky existují.")
print("🧠 A zda všechny endpointy v `url_for()` opravdu existují v @app.route nebo @blueprint.route.")

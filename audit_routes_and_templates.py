import os
import re

TEMPLATE_EXT = (".html", ".jinja", ".jinja2")
STATIC_EXT = (".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp")

project_root = os.getcwd()

templates_used = set()
statics_used = set()
routes_found = set()

template_re = re.compile(r"render_template\(['\"](.*?)['\"]")
url_for_static_re = re.compile(r"url_for\(['\"]static['\"],\s*filename=['\"](.*?)['\"]")
url_for_endpoint_re = re.compile(r"url_for\(['\"](.*?)['\"]")

print("🔍 Prohledávám soubory...\n")

for root, dirs, files in os.walk(project_root):
    for filename in files:
        if filename.endswith(".py"):
            with open(os.path.join(root, filename), encoding="utf-8") as f:
                content = f.read()
                templates_used.update(template_re.findall(content))
                statics_used.update(url_for_static_re.findall(content))
                routes_found.update(url_for_endpoint_re.findall(content))
        if filename.endswith(TEMPLATE_EXT):
            with open(os.path.join(root, filename), encoding="utf-8") as f:
                content = f.read()
                statics_used.update(url_for_static_re.findall(content))
                routes_found.update(url_for_endpoint_re.findall(content))

print("✅ Použité šablony:")
for t in sorted(templates_used):
    print("  -", t)

print("\n✅ Použité statické soubory:")
for s in sorted(statics_used):
    print("  -", s)

print("\n✅ Použitá `url_for()` volání (endpointy):")
for r in sorted(routes_found):
    print("  -", r)

print("\n💡 Zkontroluj, zda všechny tyto soubory ve složkách `/templates/` a `/static/` opravdu existují.")
print("📌 A ujisti se, že všechny endpointy uvedené v `url_for()` opravdu existují v `@app.route` nebo `@blueprint.route`.")

print("\n🧠 Hotovo.")

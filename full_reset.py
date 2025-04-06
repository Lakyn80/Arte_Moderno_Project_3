# full_reset.py
import subprocess
import os
import shutil
from dotenv import load_dotenv
from app import create_app
from flask_migrate import upgrade

# Načti proměnné z .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "arte_moderno")
DB_USER = os.getenv("DB_USER", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Cesty ke složkám se soubory
UPLOAD_FOLDER = "app/static/uploads"
INVOICE_FOLDER = "invoices"
OTHER_FOLDERS = ["app/static/client/uploads", "app/static/product_images"]

def reset_postgres_db():
    print(f"❗ Smažu databázi: {DB_NAME}")
    try:
        subprocess.run(["dropdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME], check=True)
        print("✅ Databáze úspěšně smazána.")
    except subprocess.CalledProcessError:
        print("⚠️  Databázi se nepodařilo smazat. Možná už neexistuje?")

    print(f"📦 Vytvářím novou databázi: {DB_NAME}")
    subprocess.run(["createdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME], check=True)
    print("✅ Nová databáze připravena.")

def apply_migrations():
    app = create_app()
    with app.app_context():
        print("🚀 Spouštím migrace...")
        upgrade()
        print("✅ Migrace dokončeny.")

def remove_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"🧹 Složka '{folder_path}' byla smazána.")
    else:
        print(f"📁 Složka '{folder_path}' neexistuje nebo už byla smazána.")

def clean_static_files():
    print("🧼 Mažu všechny nahrané soubory...")
    remove_folder(UPLOAD_FOLDER)
    remove_folder(INVOICE_FOLDER)
    for folder in OTHER_FOLDERS:
        remove_folder(folder)
    print("✅ Všechny soubory byly smazány.")

if __name__ == "__main__":
    reset_postgres_db()
    apply_migrations()
    clean_static_files()
    print("\n🎉 Hotovo! Projekt je připravený pro čisté nasazení.")

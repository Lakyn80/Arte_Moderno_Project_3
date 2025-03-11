from werkzeug.security import generate_password_hash

new_password = "admin"
hashed = generate_password_hash(new_password)
print(hashed)

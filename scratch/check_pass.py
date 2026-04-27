from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

password = "Aqib@1012"
hash_val = "$2b$12$s5WNFldc8vNwP1ANTGzTPuBoxo7SBgsSFrdy4BY3ncf2.z0BHJ8Uy"

if bcrypt.check_password_hash(hash_val, password):
    print("Password matches!")
else:
    print("Password DOES NOT match!")

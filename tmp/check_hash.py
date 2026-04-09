import os
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

hash_from_db = "$2b$12$8QzYwJ8sYJ0l0rRz6lHk3eR1k6bK1lK2dYz0Gv1Xy3Q0VZ8xG7W6K"
test_password = "Aqib@1012"

is_match = bcrypt.check_password_hash(hash_from_db, test_password)
print(f"Match: {is_match}")

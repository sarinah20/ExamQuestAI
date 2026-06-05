from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create a Flask SQLAlchemy User model with id, username, email and password fields.
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'
    

@app.route("/")
def home():
    return "Welcome to ExamQuest AI"

# Create a registration route that renders register.html
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
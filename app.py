from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

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

# Create a registration route that accepts POST requests and saves a user to the database
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Create a new user instance
        new_user = User(username=username, email=email, password=password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return "Registration successful!"

    # If it's a GET request, render the registration form
    return render_template("register.html")

# Create a login route that checks email and password against the database and returns a success message if they match
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Query the database for a user with the provided email and password
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return redirect("/dashboard")
        else:
            return "Invalid email or password."

    # If it's a GET request, render the login form
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "<h1>Welcome to ExamQuest AI Dashboard</h1>"
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
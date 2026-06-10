from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

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
    
# Create an Exam model with id, exam_name, exam_date and user_id fields, where user_id is a foreign key referencing the User model.
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(120), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('exams', lazy=True))
    def __repr__(self):
        return f'<Exam {self.exam_name} for User ID {self.user_id}>'
    

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

# Create a route called create_exam that renders exam.html
@app.route("/create_exam", methods=["GET", "POST"])
def create_exam():
    if request.method == "POST":
        exam_name = request.form["exam_name"]
        exam_date = datetime.strptime(
            request.form["exam_date"],
            "%Y-%m-%d"
        ).date()

        # Create a new exam instance
        new_exam = Exam(exam_name=exam_name, exam_date=exam_date, user_id=1)

        # Add the new exam to the database
        db.session.add(new_exam)
        db.session.commit()

        return redirect("/dashboard")

    # If it's a GET request, render the exam creation form
    return render_template("exam.html")

@app.route("/dashboard")
def dashboard():

    exam = Exam.query.first()

    if not exam:
        return "<h1>No Exams Added Yet</h1>"

    days_remaining = (exam.exam_date - date.today()).days

    return f"""
    <h1>Welcome to ExamQuest AI Dashboard</h1>

    <h2>{exam.exam_name}</h2>

    <p>Exam Date: {exam.exam_date}</p>

    <p>Days Remaining: {days_remaining}</p>
    """
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
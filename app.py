from flask import Flask, request, render_template, redirect, url_for
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
    
# Create a Subject model with id, subject_name and exam_id fields, where exam_id is a foreign key referencing the Exam model.
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(120), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    exam = db.relationship('Exam', backref=db.backref('subjects', lazy=True))
    total_units = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return f'<Subject {self.subject_name} for Exam ID {self.exam_id}>'
    

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

# Create a route called add_subject that renders subjects.html and saves a subject to the database
@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    if request.method == "POST":
        subject_name = request.form["subject_name"]
        total_units = int(request.form["total_units"])

        # Create a new subject instance
        new_subject = Subject(subject_name=subject_name, exam_id=1  , total_units=total_units)

        # Add the new subject to the database
        db.session.add(new_subject)
        db.session.commit()

        return redirect("/dashboard")

    # If it's a GET request, render the subject creation form
    return render_template("subjects.html")

# Create a route called generate_plan that calculates study days remaining and displays a study plan based on the number of subjects and total units for each subject.
@app.route("/generate_plan")
def generate_plan():

    preparation_level = request.args.get("preparation_level")
    study_hours = int(request.args.get("study_hours", 2))
    favorite_subject = request.args.get("favorite_subject")
    least_favorite_subject = request.args.get("least_favorite_subject")
    exam = Exam.query.first()
    subjects = Subject.query.filter_by(exam_id=exam.id).all()
    schedule = []
    remaining_units = {}

    for subject in subjects:
        remaining_units[subject.subject_name] = subject.total_units
    if least_favorite_subject in remaining_units:
        remaining_units[least_favorite_subject] += 1

    while any(units > 0 for units in remaining_units.values()):

        for subject_name in remaining_units:

            if remaining_units[subject_name] > 0:

                unit_number = (
                    subjects[
                        [s.subject_name for s in subjects].index(subject_name)
                    ].total_units
                    - remaining_units[subject_name]
                    + 1
                )

                schedule.append(
                    f"{subject_name} - Unit {unit_number}"
                )

                remaining_units[subject_name] -= 1

    study_days = (exam.exam_date - date.today()).days - 1
    total_units = sum(subject.total_units for subject in subjects)
    units_per_day = total_units / study_days
    if study_hours <= 2:
        max_units_per_day = 1

    elif study_hours <= 4:
        max_units_per_day = 2

    else:
        max_units_per_day = 3

    if not exam:
        return "No Exam Found"
    
    if preparation_level == "Beginner":
        max_units_per_day = max(1, max_units_per_day - 1)
    
    elif preparation_level == "Revision Only":
        max_units_per_day += 1

    subject_info = ""

    for subject in subjects:
        subject_info += f"""
        {subject.subject_name}
        - {subject.total_units} Units<br>
        """
    
    plan_html = ""

    day = 1

    for i in range(0, len(schedule), max_units_per_day):

        day_tasks = schedule[i:i + max_units_per_day]

        plan_html += f"<b>Day {day}</b><br>"

        for task in day_tasks:
            plan_html += f"{task}<br>"

        plan_html += "<br>"

        day += 1

    message = ""

    if least_favorite_subject:
        message += f"""
        ⚡ {least_favorite_subject} is marked as your least favorite subject.
        Make sure to generate quizzes and revision notes frequently for this subject.<br><br>
        """

    if favorite_subject:
        message += f"""
        🌟 {favorite_subject} is your favorite subject.
        Use it as a confidence booster between difficult study sessions.<br><br>
        """

    if preparation_level == "Beginner":
        message += """
        📚 You selected Beginner mode.
        Focus on understanding concepts first and don't rush through units.<br><br>
        """

    elif preparation_level == "Revision Only":
        message += """
        🚀 You selected Revision Only mode.
        Focus on solving questions and revising weak areas.<br><br>
        """    

    return f"""
    <h1>Study Plan Generator</h1>
    {message}
    Exam: {exam.exam_name}<br>
    Exam Date: {exam.exam_date}<br>
    Study Days Available: {study_days}<br>
    Total Units: {total_units}<br>
    Units Per Day: {round(units_per_day, 2)}<br>
    Max Units Per Day: {max_units_per_day}<br>
    <h2>Generated Plan</h2>
    Favorite Subject: {favorite_subject}<br>
    Least Favorite Subject: {least_favorite_subject}<br>
    Study Hours: {study_hours}<br>
    Preparation Level: {preparation_level}<br><br>
    {plan_html}

    <h2>Subjects</h2>
    {subject_info}
    """

@app.route("/planner_setup", methods=["GET", "POST"])
def planner_setup():
    if request.method == "POST":
        preparation_level = request.form["preparation_level"]
        study_hours = int(request.form["study_hours"])
        favorite_subject = request.form["favorite_subject"]
        least_favorite_subject = request.form["least_favorite_subject"]
        subjects = Subject.query.all()

        return redirect(
            url_for(
                "generate_plan",
                preparation_level=preparation_level,
                study_hours=study_hours,
                favorite_subject=favorite_subject,
                least_favorite_subject=least_favorite_subject
            )
        )
    return render_template(
        "planner_setup.html",
        subjects=subjects
    )


@app.route("/dashboard")
def dashboard():

    exam = Exam.query.first()

    if not exam:
        return "<h1>No Exams Added Yet</h1>"

    days_remaining = (exam.exam_date - date.today()).days

    subjects = Subject.query.filter_by(exam_id=exam.id).all()

    subject_list = ""

    for subject in subjects:
        subject_list += f"<li>{subject.subject_name}</li>"

    return f"""
    <h1>Welcome to ExamQuest AI Dashboard</h1>

    <h2>{exam.exam_name}</h2>

    <p>Exam Date: {exam.exam_date}</p>

    <p>Days Remaining: {days_remaining}</p>

    <h3>Subjects</h3>

    <ul>
        {subject_list}
    </ul>
    """
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
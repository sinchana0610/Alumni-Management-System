from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
import re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret123'

db = SQLAlchemy(app)

# -------------------- MODELS --------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    job = db.Column(db.String(100), nullable=False)


# -------------------- BASE TEMPLATE --------------------

base = """
<!DOCTYPE html>
<html>
<head>
    <title>Alumni Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-4">
    {{ content | safe }}
</div>
</body>
</html>
"""

# -------------------- REGISTER --------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):
            return "Invalid Email Format"

        if len(password) < 6:
            return "Password must be at least 6 characters"

        if User.query.filter_by(email=email).first():
            return "Email already registered"

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    content = """
    <h2>Register</h2>
    <form method="post" class="card p-4 shadow">
        <input class="form-control mb-2" name="name" placeholder="Name" required>
        <input class="form-control mb-2" type="email" name="email" placeholder="Email" required>
        <input class="form-control mb-2" type="password" name="password" placeholder="Password (min 6 chars)" required>
        <button class="btn btn-success w-100">Register</button>
    </form>
    <p class="mt-3">Already have an account? <a href="/login">Login</a></p>
    """
    return render_template_string(base, content=content)


# -------------------- LOGIN --------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))

        return render_template_string(base, content="""
        <div class="alert alert-danger">Invalid email or password</div>
        <a href="/login">Try Again</a>
        """)

    content = """
    <h2>Login</h2>
    <form method="post" class="card p-4 shadow">
        <input class="form-control mb-2" type="email" name="email" placeholder="Email" required>
        <input class="form-control mb-2" type="password" name="password" placeholder="Password" required>
        <button class="btn btn-primary w-100">Login</button>
    </form>
    <p class="mt-3">New user? <a href="/register">Register</a></p>
    """
    return render_template_string(base, content=content)


# -------------------- LOGOUT --------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# -------------------- HOME --------------------

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    alumni = Alumni.query.all()
    rows = ""

    for a in alumni:
        rows += f"""
        <tr>
            <td>{a.name}</td>
            <td>{a.department}</td>
            <td>{a.year}</td>
            <td>{a.email}</td>
            <td>{a.phone}</td>
            <td>{a.job}</td>
            <td>
                <a href="/delete/{a.id}" class="btn btn-danger btn-sm">Delete</a>
            </td>
        </tr>
        """

    content = f"""
    <div class="d-flex justify-content-between">
        <h2>Alumni Management System</h2>
        <a href="/logout" class="btn btn-danger">Logout</a>
    </div>

    <a href="/add" class="btn btn-success my-3">Add New Alumni</a>

    <table class="table table-bordered table-striped">
        <thead class="table-dark">
            <tr>
                <th>Name</th><th>Department</th><th>Year</th>
                <th>Email</th><th>Phone</th><th>Job</th><th>Action</th>
            </tr>
        </thead>
        <tbody>
            {rows if rows else '<tr><td colspan="7" class="text-center">No Alumni Found</td></tr>'}
        </tbody>
    </table>
    """

    return render_template_string(base, content=content)


# -------------------- ADD ALUMNI --------------------

@app.route('/add', methods=['GET', 'POST'])
def add_alumni():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        year = int(request.form['year'])
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        job = request.form['job'].strip()

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):
            return "Invalid Email Format"

        if not phone.isdigit() or len(phone) != 10:
            return "Phone number must be 10 digits"

        current_year = datetime.now().year
        if year < 1980 or year > current_year:
            return "Invalid Passing Year"

        new = Alumni(
            name=name,
            department=department,
            year=year,
            email=email,
            phone=phone,
            job=job
        )

        db.session.add(new)
        db.session.commit()
        return redirect(url_for('index'))

    content = """
    <h2>Add New Alumni</h2>
    <form method="post" class="card p-4 shadow">
        <input class="form-control mb-2" name="name" placeholder="Full Name" required>
        <input class="form-control mb-2" name="department" placeholder="Department" required>
        <input class="form-control mb-2" type="number" name="year" placeholder="Passing Year" required>
        <input class="form-control mb-2" type="email" name="email" placeholder="Email" required>
        <input class="form-control mb-2" name="phone" placeholder="10-digit Phone" required>
        <input class="form-control mb-2" name="job" placeholder="Job" required>
        <button class="btn btn-success w-100">Save Alumni</button>
    </form>
    <a href="/" class="btn btn-secondary mt-3">Back</a>
    """

    return render_template_string(base, content=content)


# -------------------- DELETE --------------------

@app.route('/delete/<int:id>')
def delete_alumni(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    alumni = Alumni.query.get_or_404(id)
    db.session.delete(alumni)
    db.session.commit()
    return redirect(url_for('index'))


# -------------------- RUN APP --------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

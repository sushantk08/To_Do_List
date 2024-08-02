from flask import Flask,render_template,request,flash,url_for,redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fa2ddd7e0cbaa3933f0f4cadc9bc7a90d68ec19cd3cc7000c6a65e9055f0639e'

db = SQLAlchemy(app)

class Registrations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == 'POST':
        name=request.form.get("Name")
        username=request.form.get("Email")
        password=request.form.get("Password")
        confirmed_password=request.form.get("Cnf_Password")

        if len(username)<4:
            flash("Please Enter Valid Email!!")
            return redirect(url_for('register'))
        if len(password)<6:
            flash("Please Enter Valid Password!!")
            return redirect(url_for('register'))
        if password != confirmed_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))

        existing_user = Registrations.query.filter_by(email=username).first()
        if existing_user:
            flash('Username already exists. Plz proceed to Login!!')
            return redirect(url_for('register'))

        new_user = Registrations(name=name, email=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=='POST':
        username=request.form.get("Email")
        password=request.form.get("Password")

        user = Registrations.query.filter_by(email=username,password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        todo_list = Todo.query.all()
        return render_template("dashboard.html", todo_list=todo_list)
    else:
        return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todo = Todo.query.get(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))





if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
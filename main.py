from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        unhashed_password = request.form["password"]
        hashed_password = generate_password_hash(password=unhashed_password,
                                                 method="pbkdf2:sha256",
                                                 salt_length=8)
        user_email = request.form["email"]
        email_exists = User.query.filter_by(email=user_email).first()
        if email_exists:
            flash(message="This email address already exists")
            return redirect(url_for("register"))
        else:
            new_user = User(email=request.form["email"],
                            name=request.form["name"],
                            password=hashed_password)
            name = request.form["name"]
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("secrets", name=current_user.name, logged_in=True))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        user = User.query.filter_by(email=user_email).first()
        if user:
            if check_password_hash(pwhash=user.password, password=user_password):
                login_user(user)
                return redirect(url_for("secrets", name=user.name))
            else:
                flash(message="Password incorrect. Please try again")
                return redirect(url_for("login"))

        else:
           flash(message="This email does not exist. Please try again")
           return redirect(url_for("login"))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    directory = "static/files"
    filename = "cheat_sheet.pdf"
    return send_from_directory(directory=directory, path=filename)



if __name__ == "__main__":
    app.run(debug=True)

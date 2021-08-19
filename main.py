from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField, FileField, PasswordField
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, UserMixin, login_required, logout_user, login_user
import requests
app = Flask(__name__)
app.secret_key="114511616"
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///AllData.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db=SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class UpdateForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/movies/update", methods=["GET", "POST"])
def update():
    form=UpdateForm()
    movie_id=request.args.get('id')
    movie=Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect('/movies')
    return render_template("update.html", forms=form)

class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hash_salted_password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        new_user=User(email=request.form.get('email'),
                      password=hash_salted_password, username=request.form.get('username'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect('/movies')
    return render_template('recieve_data.html', logged_in=current_user.is_authenticated)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email=request.form.get("email")
        password=request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if not check_password_hash(user.password, password):
                flash('Password incorrect, please try again.')
                return redirect(url_for('login'))
            else:
                login_user(user)
                return redirect(url_for('movie'))
        else:
            flash("You haven't registered yet. Please register first.")
            return redirect("register")
    return render_template('login.html', logged_in=current_user.is_authenticated)

@app.route("/movies", methods=['GET', 'POST'])
@login_required
def movie():
    all_movies=Movie.query.all()
    return render_template("movies.html", name=current_user.username, movies=all_movies, logged_in=True)
@app.route("/movie-api-documention")
def api():
    return redirect("https://documenter.getpostman.com/view/9443554/Tzz5tJMu")
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        query=form.title.data
    return render_template("add.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)


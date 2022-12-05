from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask import flash
import unicodedata
import pandas as pd
import string
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pyresparser import ResumeParser
from docx import Document
import re
import joblib
from werkzeug.utils import secure_filename
import spacy

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load the spacy library for text cleaning
nlp = spacy.load('en_core_web_sm')
# Loading the saved model
rf_clf = joblib.load('rf_clf.pkl')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@app.before_first_request
def create_tables():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[
                           InputRequired()])
    password = PasswordField('Password:', validators=[
                             InputRequired()])
    remember = BooleanField('Remember me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('Username:', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password:', validators=[
                             InputRequired(), Length(min=5, max=80)])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        # return '<h1>Invalid username or password</h1>'
        flash("Invalid username or password")
        return redirect(url_for('login'))
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        # return '<h1>New user has been created!</h1>'
        flash("User created")
        return redirect(url_for('signup'))
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


@app.route('/uploader', methods=['GET', 'POST'])
def dashboards():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        try:
            doc = Document()
            with open(f.filename, 'r') as file:
                doc.add_paragraph(file.read())
                doc.save("text.docx")
                data = ResumeParser('text.docx').get_extracted_data()

        except:
            data = ResumeParser(f.filename).get_extracted_data()

        cleaned_data = {x.replace('_', ' '): v
                        for x, v in data.items()}

        def clean_content(text):
            text = text.replace("uf0b7", "").replace(
                "'", "").replace("[", "").replace("]", "")
            return text

        df = pd.DataFrame()
        df["key"] = cleaned_data.keys()
        df["content"] = cleaned_data.values()
        df["content"] = df.content.apply(lambda x: clean_content(str(x)))
        final_data = df.set_index('key')['content'].to_dict()

        datas = []
        datas.append(final_data)

        flash("File uploaded successfully")
      #  return redirect(url_for('dashboard'))

      # Turn a Unicode string to plain ASCII, thanks to https://stackoverflow.com/a/518232/2809427
        def unicode_to_ascii(s):
            all_letters = string.ascii_letters + " .,;'-"
            return ''.join(
                c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn'
                and c in all_letters
            )

        # Remove Stop Words
        def remove_stopwords(text):
            doc = nlp(text)
            return " ".join([token.text for token in doc if not token.is_stop])

        def clean_text(text):
            #print(f'Text before Cleaning: {text}')
            # Text to lowercase
            text = text.lower()
            # Remove URL from text
            text = re.sub(r"http\S+", "", text)
            # Remove Numbers from text
            text = re.sub(r'\d+', '', text)
            # Convert the unicode string to plain ASCII
            text = unicode_to_ascii(text)
            # Remove Punctuations
            text = re.sub(r'[^\w\s]', '', text)
            #text = remove_punct(text)
            # Remove StopWords
            text = remove_stopwords(text)
            # Remove empty spaces
            text = text.strip()
            # \s+ to match all whitespaces
            # replace them using single space " "
            text = re.sub(r"\s+", " ", text)
            #print(f'Text after Cleaning: {text}')
            return text

        data = str(data)
        cleaned = clean_text(data)
        prediction = rf_clf.predict([cleaned])
        result = prediction[0]

    return render_template('dashboard.html', name=current_user.username, res_content=datas, pred=result)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    #app.run('0.0.0.0', port=(os.environ.get("PORT", 5000)))
     app.run(debug=True)

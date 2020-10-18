from flask import Flask, render_template, send_from_directory, redirect, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_required, logout_user, login_user, current_user
from urllib.parse import urlparse, urljoin
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_ckeditor import CKEditor
from os.path import dirname, join


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

path =  join(dirname(__file__), 'static/images/')

ckeditor = CKEditor(app)

db = SQLAlchemy(app)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.Integer, nullable=False)
    verse = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<blogpost %r' % (self.id)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return '<User %r' % (self.username)

class UserView(ModelView):
    column_exclude_list = ['password']
    column_display_pk = True
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, template_mode='bootstrap3', index_view=MyAdminView())
admin.add_view(UserView(User, db.session))
admin.add_view(UserView(Books, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Remaining endpoints
@app.route("/", methods=["POST","GET"])
def home():

    posts = None

    if request.method == 'POST':
        chapter = request.form['chapter']
        verse = request.form['verse']

        posts = Books.query.filter_by(verse=verse).one() 

        print(posts.content)
        return render_template('index.html', posts=posts)

    return render_template('index.html', posts=posts)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    if request.method == 'POST':
        username = request.form.get("user")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials")
            return redirect(url_for("login"))

        login_user(user, remember=True)

        if 'next' in session:
            next = session['next']

            if is_safe_url(next):
                return redirect(next) 

    session['next'] = request.args.get('next')
    return redirect(url_for('home'))

@app.route('/shlok/<int:id>/')
def post(id):
    post = Books.query.filter_by(id=id).one() 
    return render_template('shlok.html', post=post)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>", methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Books.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add')
@login_required
def add():
    return render_template('add.html')

@app.route('/addverse', methods=['POST'])
@login_required
def addverse():

    chapter = request.form['chapter']
    verse = request.form['verse']
    date_posted = datetime.now()
    content = request.form['ckeditor']

    post = Books(chapter=chapter, verse=verse, date_posted=date_posted, content=content)

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Books.query.filter_by(id=id).first()

    if request.method == 'POST':
        post.chapter = request.form['chapter']
        post.verse = request.form['verse']
        post.content = request.form['content']

        db.session.commit()
        return redirect('/shlok/' + str(post.id) + '/')

    else:
        return render_template('edit.html', post=post)

    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(e):
  return render_template('error.html')

if __name__ == '__main__':
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
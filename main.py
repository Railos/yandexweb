from flask import Flask, render_template, request, redirect, url_for
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
import logging
from flask_login import LoginManager, login_required, login_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'markdaun'
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def home():
    return render_template('home.html', menuname="Главная")

@app.route('/recipes')
def recipes():
    return render_template('recipes.html', menuname="Рецепты")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', menuname="Регистрация", form=form)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, menuname="Вход")
    return render_template('login.html', menuname="Вход", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(debug=True, port=8000)
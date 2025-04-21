from flask import Flask, render_template, request, redirect, url_for
from data import db_session
from data.users import User
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'markdaun'


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

@app.route('/login')
def login():
    return render_template('login.html', menuname="Вход")

if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(debug=True)
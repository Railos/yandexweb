from flask import Flask, render_template, request, redirect, url_for
from data import db_session
from data.users import User
from data.recipes import Recipes
from forms.recipe import RecipeForm
from forms.user import RegisterForm, LoginForm
import logging
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import bleach

app = Flask(__name__)
app.config['SECRET_KEY'] = 'markdaun'
db_session.global_init("db/users.db")
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def home():
    return render_template('home.html', menuname="Главная")

@app.route('/recipes')
def recipes():
    db_sess = db_session.create_session()
    my_recipes = []
    if current_user.is_authenticated:
        my_id = db_sess.query(User).filter(User.name == current_user.name).first()
        my_recipes = db_sess.query(Recipes).filter(Recipes.user_id == my_id.id).all()
    recipes = db_sess.query(Recipes).all()
    return render_template('recipes.html', menuname="Рецепты", recipes=recipes, my_recipes=my_recipes)

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

@app.route('/<int:id>')
def view_recipe(id: int):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipes).filter(Recipes.id == id).first()
    return render_template("recipe.html", menuname="Рецепт", dynamic_html=recipe.content, recipe=recipe)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        recipe = Recipes(
            title=form.name.data,
            description=form.description.data,
            content=form.content.data,
            user_id=db_sess.query(User).filter(User.id == current_user.id).first().id
        )
        db_sess.add(recipe)
        db_sess.commit()
        return redirect('/recipes')
    return render_template('new_recipe.html', menuname="Новый рецепт", form=form)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
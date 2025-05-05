from flask import Flask, render_template, request, redirect, url_for
from data.db_session import init_db, db_session
from data.users import User
from data.recipes import Recipes
from forms.recipe import RecipeForm
from forms.user import RegisterForm, LoginForm
import logging
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import bleach
from sqlalchemy import func, or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'markdaun'
#db_session.global_init("db/users.db")
login_manager = LoginManager()
login_manager.init_app(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def home():
    return render_template('home.html', menuname="Главная")

@app.route('/recipes')
def recipes():
    my_recipes = []
    if current_user.is_authenticated:
        my_id = db_session.query(User).filter(User.name == current_user.name).first()
        my_recipes = db_session.query(Recipes).filter(Recipes.user_id == my_id.id).all()
    recipes = db_session.query(Recipes).all()
    db_session.close()
    return render_template('recipes.html', menuname="Рецепты", recipes=recipes, my_recipes=my_recipes)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip().lower()

    if not query:
        return render_template("recipes.html", menuname="Рецепты", recipes=[], my_recipes=[])
    
    search_pattern = f"%{query}%"
    results = db_session.query(Recipes).filter(
        or_(
            func.lower(Recipes.title).like(search_pattern),
            func.lower(Recipes.description).like(search_pattern)
        )
    )
    my_recipes = []
    if current_user.is_authenticated:
        my_recipes = results.filter(Recipes.user_id == current_user.id).all()

    db_session.close()
    return render_template("recipes.html", menuname="Рецепты", recipes=results.all(), my_recipes=my_recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_session.add(user)
        db_session.commit()
        db_session.close()
        return redirect('/login')
    return render_template('register.html', menuname="Регистрация", form=form)

@login_manager.user_loader
def load_user(user_id):
    z = db_session.query(User).get(user_id)
    db_session.close()
    return z

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        db_session.close()
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
    recipe = db_session.query(Recipes).filter(Recipes.id == id).first()
    return render_template("recipe.html", menuname="Рецепт", dynamic_html=recipe.content, recipe=recipe)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipes(
            title=form.name.data,
            description=form.description.data,
            content=form.content.data,
            user_id=db_session.query(User).filter(User.id == current_user.id).first().id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.close()
        return redirect('/recipes')
    return render_template('new_recipe.html', menuname="Новый рецепт", form=form)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
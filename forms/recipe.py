from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class RecipeForm(FlaskForm):
    name = StringField('Имя Рецепта', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    content = TextAreaField('Контент', validators=[DataRequired()])
    submit = SubmitField('Создать')

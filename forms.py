from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class Get_Plot(FlaskForm):
    str_input = StringField('Enter a Plot Command Here',
                            validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Generate Climate Plot!')

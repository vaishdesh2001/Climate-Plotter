from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class Get_Plot(FlaskForm):
    str_input = StringField('Enter something like "Bangalore rainfall" or "Chicago and Madison snowfall"',
                            validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Generate Climate Plot!')

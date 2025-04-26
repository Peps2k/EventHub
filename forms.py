from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed

class RegisterForm(FlaskForm):
    email = StringField('E-post', validators=[DataRequired(), Email()])
    name = StringField('Navn', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Passord', validators=[DataRequired()])
    submit = SubmitField('Registrer')

class LoginForm(FlaskForm):
    email = StringField('E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired()])
    submit = SubmitField('Logg inn')

class EventForm(FlaskForm):
    name = StringField('Arrangementnavn', validators=[DataRequired()])
    description = TextAreaField('Beskrivelse', validators=[DataRequired()])
    date = DateTimeField('Dato (YYYY-MM-DD HH:MM)', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    location = StringField('Sted', validators=[DataRequired()])
    submit = SubmitField('Opprett arrangement')
    image = FileField('Bilde', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectMultipleField, BooleanField, widgets
from wtforms.validators import DataRequired, Length, URL, Email


class EditUserForm(Form):
    username_field = StringField('username', validators = [Length(max=50, message = "username must be less than 50 characters")])
    email_field = StringField('email', validators = [Email(message="hmm.. this doesnt seem like a valid email")])

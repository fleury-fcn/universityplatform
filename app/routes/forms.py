from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email Institutionnel', 
                       validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "prenom.nom@institution.edu"})
    submit = SubmitField('Envoyer le lien')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', 
                           validators=[
                               DataRequired(),
                               Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
                           ])
    confirm_password = PasswordField('Confirmez le mot de passe',
                                    validators=[
                                        DataRequired(),
                                        EqualTo('password', message='Les mots de passe doivent correspondre')
                                    ])
    submit = SubmitField('Mettre à jour le mot de passe')
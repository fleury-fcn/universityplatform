from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, BooleanField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileAllowed

class ActualiteForm(FlaskForm):
    titre = StringField('Titre', validators=[DataRequired(), Length(max=150)])
    slug = StringField('Slug (URL)', validators=[DataRequired(), Length(max=150)])
    contenu = TextAreaField('Contenu', validators=[DataRequired()])
    resume = TextAreaField('Résumé', validators=[Length(max=300)])
    categorie = SelectField('Catégorie', choices=[
        ('evenement', 'Événement'),
        ('conference', 'Conférence'),
        ('diplome', 'Diplôme'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre')
    ], validators=[DataRequired()])
    sous_categorie = StringField('Sous-catégorie', validators=[Optional(), Length(max=50)])
    image = FileField('Image principale', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images seulement!')
    ])
    image_alt = StringField('Description de l\'image', validators=[Optional(), Length(max=100)])
    date_evenement = DateTimeField('Date de l\'événement', format='%Y-%m-%d %H:%M', validators=[Optional()])
    lieu = StringField('Lieu', validators=[Optional(), Length(max=100)])
    statut = SelectField('Statut', choices=[
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé')
    ], default='publie', validators=[DataRequired()])
    est_important = BooleanField('Mettre en avant')
    mots_cles = StringField('Mots-clés (séparés par des virgules)', validators=[Optional(), Length(max=255)])
    meta_description = StringField('Description pour le référencement', validators=[Optional(), Length(max=160)])
    pieces_jointes = MultipleFileField('Pièces jointes', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Fichiers autorisés: PDF, Word, Images')
    ])

class CommentaireForm(FlaskForm):
    contenu = TextAreaField('Commentaire', validators=[DataRequired(), Length(min=5, max=1000)])
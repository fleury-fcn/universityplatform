from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SelectField, DateTimeField, BooleanField, FileField, MultipleFileField, RadioField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileAllowed
from app.models.actualites import Departement  

class ActualiteForm(FlaskForm):
    # Type d'actualité (nouveau champ)
    type_actualite = RadioField('Type d\'actualité', 
                              choices=[
                                  ('ista', 'ISTA (Interne)'),
                                  ('nationale', 'Nationale'),
                                  ('internationale', 'Internationale')
                              ],
                              default='ista',
                              validators=[DataRequired()])
    
    # Champs communs à tous les types
    titre = StringField('Titre', validators=[DataRequired(), Length(max=150)])
    slug = StringField('Slug (URL)', validators=[DataRequired(), Length(max=150)])
    
    contenu = TextAreaField(
    'Contenu',
    render_kw={"placeholder": "Rédigez ici le contenu complet de l’actualité..."},
    description="Vous pouvez mettre en forme le texte, insérer des images, des liens, etc.",
    validators=[DataRequired(), Length(min=10)]
    )
    
    resume = TextAreaField(
        'Résumé',
        render_kw={"placeholder": "Résumé court (max 300 caractères)"},
        validators=[Length(max=300)]
    )
    
    # Catégories (adaptées pour les 3 types)
    categorie = SelectField('Catégorie principale', choices=[
        ('evenement', 'Événement'),
        ('conference', 'Conférence'),
        ('diplome', 'Diplôme'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre')
    ], validators=[DataRequired()])
    
    sous_categorie = StringField('Sous-catégorie', validators=[Optional(), Length(max=50)])
    
    # Champs spécifiques à ISTA
    departement = SelectField('Département concerné', 
                            choices=[],  # Rempli dynamiquement dans la route
                            validators=[Optional()])
    
    # Champs spécifiques aux actualités nationales/internationales
    pays = SelectField('Pays', 
                     choices=[],  # Rempli dynamiquement dans la route
                     validators=[Optional()])
    ville = StringField('Ville', validators=[Optional(), Length(max=100)])
    
    # Champs médias et dates
    image = FileField('Image principale', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images seulement!')
    ])
    image_alt = StringField('Description de l\'image', validators=[Optional(), Length(max=100)])
    date_evenement = DateTimeField('Date de l\'événement', 
                                   format='%Y-%m-%dT%H:%M', 
                                   validators=[])
    
    lieu = StringField('Lieu', validators=[Optional(), Length(max=100)])
    
    # Paramètres de publication
    statut = SelectField('Statut', choices=[
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé')
    ], default='publie', validators=[DataRequired()])
    est_important = BooleanField('Mettre en avant')
    
    # SEO et métadonnées
    mots_cles = StringField('Mots-clés (séparés par des virgules)', validators=[Optional(), Length(max=255)])
    meta_description = StringField('Description pour le référencement', validators=[Optional(), Length(max=160)])
    
    # Pièces jointes
    pieces_jointes = MultipleFileField('Pièces jointes', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Fichiers autorisés: PDF, Word, Images')
    ])

    def __init__(self, *args, **kwargs):
        super(ActualiteForm, self).__init__(*args, **kwargs)
        # Initialisation dynamique des choix pour les sélecteurs
        #self.departement.choices = [('', 'Sélectionnez un département')] + \
                                  # [(d.id, d.nom) for d in Departement.query.order_by('nom').all()]
        # Pour les pays, vous pouvez utiliser une liste statique ou une table Pays
        self.pays.choices = [('', 'Sélectionnez un pays')] + [
            
                    ('AF', 'Afghanistan'),
                    ('ZA', 'Afrique du Sud'),
                    ('AL', 'Albanie'),
                    ('DZ', 'Algérie'),
                    ('DE', 'Allemagne'),
                    ('AD', 'Andorre'),
                    ('AO', 'Angola'),
                    ('AI', 'Anguilla'),
                    ('AQ', 'Antarctique'),
                    ('AG', 'Antigua-et-Barbuda'),
                    ('SA', 'Arabie Saoudite'),
                    ('AR', 'Argentine'),
                    ('AM', 'Arménie'),
                    ('AW', 'Aruba'),
                    ('AU', 'Australie'),
                    ('AT', 'Autriche'),
                    ('AZ', 'Azerbaïdjan'),
                    ('BS', 'Bahamas'),
                    ('BH', 'Bahreïn'),
                    ('BD', 'Bangladesh'),
                    ('BB', 'Barbade'),
                    ('BY', 'Biélorussie'),
                    ('BE', 'Belgique'),
                    ('BZ', 'Belize'),
                    ('BJ', 'Bénin'),
                    ('BM', 'Bermudes'),
                    ('BT', 'Bhoutan'),
                    ('BO', 'Bolivie'),
                    ('BA', 'Bosnie-Herzégovine'),
                    ('BW', 'Botswana'),
                    ('BR', 'Brésil'),
                    ('BN', 'Brunei'),
                    ('BG', 'Bulgarie'),
                    ('BF', 'Burkina Faso'),
                    ('BI', 'Burundi'),
                    ('KH', 'Cambodge'),
                    ('CM', 'Cameroun'),
                    ('CA', 'Canada'),
                    ('CV', 'Cap-Vert'),
                    ('CF', 'Centrafrique'),
                    ('CL', 'Chili'),
                    ('CN', 'Chine'),
                    ('CY', 'Chypre'),
                    ('CO', 'Colombie'),
                    ('KM', 'Comores'),
                    ('CG', 'Congo'),
                    ('CD', 'Congo (RDC)'),
                    ('KP', 'Corée du Nord'),
                    ('KR', 'Corée du Sud'),
                    ('CR', 'Costa Rica'),
                    ('CI', 'Côte d\'Ivoire'),
                    ('HR', 'Croatie'),
                    ('CU', 'Cuba'),
                    ('DK', 'Danemark'),
                    ('DJ', 'Djibouti'),
                    ('DM', 'Dominique'),
                    ('EG', 'Égypte'),
                    ('AE', 'Émirats arabes unis'),
                    ('EC', 'Équateur'),
                    ('ER', 'Érythrée'),
                    ('ES', 'Espagne'),
                    ('EE', 'Estonie'),
                    ('US', 'États-Unis'),
                    ('ET', 'Éthiopie'),
                    ('FJ', 'Fidji'),
                    ('FI', 'Finlande'),
                    ('FR', 'France'),
                    ('GA', 'Gabon'),
                    ('GM', 'Gambie'),
                    ('GE', 'Géorgie'),
                    ('GH', 'Ghana'),
                    ('GI', 'Gibraltar'),
                    ('GR', 'Grèce'),
                    ('GD', 'Grenade'),
                    ('GL', 'Groenland'),
                    ('GP', 'Guadeloupe'),
                    ('GU', 'Guam'),
                    ('GT', 'Guatemala'),
                    ('GN', 'Guinée'),
                    ('GQ', 'Guinée équatoriale'),
                    ('GW', 'Guinée-Bissau'),
                    ('GY', 'Guyana'),
                    ('GF', 'Guyane française'),
                    ('HT', 'Haïti'),
                    ('HN', 'Honduras'),
                    ('HU', 'Hongrie'),
                    ('IN', 'Inde'),
                    ('ID', 'Indonésie'),
                    ('IQ', 'Irak'),
                    ('IR', 'Iran'),
                    ('IE', 'Irlande'),
                    ('IS', 'Islande'),
                    ('IL', 'Israël'),
                    ('IT', 'Italie'),
                    ('JM', 'Jamaïque'),
                    ('JP', 'Japon'),
                    ('JO', 'Jordanie'),
                    ('KZ', 'Kazakhstan'),
                    ('KE', 'Kenya'),
                    ('KG', 'Kirghizistan'),
                    ('KI', 'Kiribati'),
                    ('KW', 'Koweït'),
                    ('LA', 'Laos'),
                    ('LS', 'Lesotho'),
                    ('LV', 'Lettonie'),
                    ('LB', 'Liban'),
                    ('LR', 'Libéria'),
                    ('LY', 'Libye'),
                    ('LI', 'Liechtenstein'),
                    ('LT', 'Lituanie'),
                    ('LU', 'Luxembourg'),
                    ('MK', 'Macédoine'),
                    ('MG', 'Madagascar'),
                    ('MY', 'Malaisie'),
                    ('MW', 'Malawi'),
                    ('MV', 'Maldives'),
                    ('ML', 'Mali'),
                    ('MT', 'Malte'),
                    ('MA', 'Maroc'),
                    ('MQ', 'Martinique'),
                    ('MU', 'Maurice'),
                    ('MR', 'Mauritanie'),
                    ('YT', 'Mayotte'),
                    ('MX', 'Mexique'),
                    ('FM', 'Micronésie'),
                    ('MD', 'Moldavie'),
                    ('MC', 'Monaco'),
                    ('MN', 'Mongolie'),
                    ('ME', 'Monténégro'),
                    ('MS', 'Montserrat'),
                    ('MZ', 'Mozambique'),
                    ('MM', 'Myanmar'),
                    ('NA', 'Namibie'),
                    ('NR', 'Nauru'),
                    ('NP', 'Népal'),
                    ('NI', 'Nicaragua'),
                    ('NE', 'Niger'),
                    ('NG', 'Nigéria'),
                    ('NU', 'Niue'),
                    ('NO', 'Norvège'),
                    ('NC', 'Nouvelle-Calédonie'),
                    ('NZ', 'Nouvelle-Zélande'),
                    ('OM', 'Oman'),
                    ('UG', 'Ouganda'),
                    ('UZ', 'Ouzbékistan'),
                    ('PK', 'Pakistan'),
                    ('PW', 'Palaos'),
                    ('PA', 'Panama'),
                    ('PG', 'Papouasie-Nouvelle-Guinée'),
                    ('PY', 'Paraguay'),
                    ('NL', 'Pays-Bas'),
                    ('PE', 'Pérou'),
                    ('PH', 'Philippines'),
                    ('PL', 'Pologne'),
                    ('PF', 'Polynésie française'),
                    ('PR', 'Porto Rico'),
                    ('PT', 'Portugal'),
                    ('QA', 'Qatar'),
                    ('RO', 'Roumanie'),
                    ('GB', 'Royaume-Uni'),
                    ('RU', 'Russie'),
                    ('RW', 'Rwanda'),
                    ('EH', 'Sahara occidental'),
                    ('KN', 'Saint-Christophe-et-Niévès'),
                    ('SM', 'Saint-Marin'),
                    ('PM', 'Saint-Pierre-et-Miquelon'),
                    ('VC', 'Saint-Vincent-et-les-Grenadines'),
                    ('SH', 'Sainte-Hélène'),
                    ('LC', 'Sainte-Lucie'),
                    ('SV', 'Salvador'),
                    ('WS', 'Samoa'),
                    ('AS', 'Samoa américaines'),
                    ('ST', 'Sao Tomé-et-Principe'),
                    ('SN', 'Sénégal'),
                    ('RS', 'Serbie'),
                    ('SC', 'Seychelles'),
                    ('SL', 'Sierra Leone'),
                    ('SG', 'Singapour'),
                    ('SK', 'Slovaquie'),
                    ('SI', 'Slovénie'),
                    ('SO', 'Somalie'),
                    ('SD', 'Soudan'),
                    ('SS', 'Soudan du Sud'),
                    ('LK', 'Sri Lanka'),
                    ('SE', 'Suède'),
                    ('CH', 'Suisse'),
                    ('SR', 'Suriname'),
                    ('SZ', 'Swaziland'),
                    ('SY', 'Syrie'),
                    ('TJ', 'Tadjikistan'),
                    ('TW', 'Taïwan'),
                    ('TZ', 'Tanzanie'),
                    ('TD', 'Tchad'),
                    ('CZ', 'Tchéquie'),
                    ('TH', 'Thaïlande'),
                    ('TL', 'Timor oriental'),
                    ('TG', 'Togo'),
                    ('TK', 'Tokelau'),
                    ('TO', 'Tonga'),
                    ('TT', 'Trinité-et-Tobago'),
                    ('TN', 'Tunisie'),
                    ('TM', 'Turkménistan'),
                    ('TR', 'Turquie'),
                    ('TV', 'Tuvalu'),
                    ('UA', 'Ukraine'),
                    ('UY', 'Uruguay'),
                    ('VU', 'Vanuatu'),
                    ('VA', 'Vatican'),
                    ('VE', 'Venezuela'),
                    ('VN', 'Viêt Nam'),
                    ('WF', 'Wallis-et-Futuna'),
                    ('YE', 'Yémen'),
                    ('ZM', 'Zambie'),
                    ('ZW', 'Zimbabwe')

                        ]

class CommentaireForm(FlaskForm):
    contenu = TextAreaField('Commentaire', validators=[DataRequired(), Length(min=5, max=1000)])
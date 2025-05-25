from datetime import datetime
from app.extensions import db

class Club(db.Model):
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)  # Changé en Text pour descriptions longues
    category = db.Column(db.String(50), nullable=False)
    banner = db.Column(db.String(255), default='default-banner.jpg')
    logo = db.Column(db.String(255), default='default-logo.jpg')
    meeting_frequency = db.Column(db.String(100))
    tags = db.Column(db.String(255))  # Pour stocker les tags séparés par des virgules
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))  # Supposant que vous avez une table users
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    name = db.Column(db.String(100))
    
    # Relations
    members = db.relationship('Member', back_populates='club', cascade='all, delete-orphan')
   
    @property
    def member_count(self):
        return self.members.count()
    
    def is_member(self, user_id):
        return self.members.filter_by(user_id=user_id).first() is not None
    
    def is_admin(self, user):
        return user.id == self.admin_id or user.role == 'administrateur'

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50), nullable=False)  # Ex: '1ère année', '2ème année'
    department = db.Column(db.String(50), nullable=False)  # Ex: 'Informatique', 'Actuariat'
    academic_year = db.Column(db.String(20), nullable=False)  # Ex: '2023-2024'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Clés étrangères
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)  # Lien vers le compte utilisateur
    
    # Relations
    club = db.relationship('Club', back_populates='members')
    user = db.relationship('User')  # Supposant que vous avez un modèle User
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
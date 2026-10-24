"""Actualités et annonces de l'institut."""
from app.extensions import db

from . import TimestampMixin, utcnow


class NewsCategory(db.Model):
    __tablename__ = "news_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)

    def __str__(self):
        return self.name


class News(TimestampMixin, db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("news_categories.id"))
    # Vide = visible par tout l'institut ; sinon réservé à une promotion (et au personnel).
    promotion_id = db.Column(db.Integer, db.ForeignKey("promotions.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False)
    published_at = db.Column(db.DateTime, index=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    category = db.relationship("NewsCategory")
    promotion = db.relationship("Promotion")
    author = db.relationship("User")

    @classmethod
    def visible_to(cls, user):
        query = cls.query.filter(cls.is_published.is_(True))
        if not user.is_staff:
            query = query.filter(db.or_(cls.promotion_id.is_(None), cls.promotion_id == user.promotion_id))
        return query

    @property
    def excerpt(self):
        text = " ".join(self.body.split())
        return text if len(text) <= 160 else text[:157].rsplit(" ", 1)[0] + "…"

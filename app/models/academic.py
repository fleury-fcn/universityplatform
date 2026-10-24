"""Référentiel académique : départements, filières, promotions."""
from app.extensions import db

from . import TimestampMixin

CYCLES = ("licence", "master")


class Department(TimestampMixin, db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    programs = db.relationship("Program", back_populates="department", order_by="Program.name")

    def __str__(self):
        return self.name


class Program(TimestampMixin, db.Model):
    """Filière."""

    __tablename__ = "programs"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    cycle = db.Column(db.String(20), nullable=False, default="licence")
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    department = db.relationship("Department", back_populates="programs")
    promotions = db.relationship("Promotion", back_populates="program", order_by="Promotion.name")

    def __str__(self):
        return self.name


class Promotion(TimestampMixin, db.Model):
    """Promotion (classe) : un niveau d'une filière pour une année académique."""

    __tablename__ = "promotions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    academic_year = db.Column(db.String(9), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    program = db.relationship("Program", back_populates="promotions")
    students = db.relationship("User", back_populates="promotion")

    def __str__(self):
        return self.name

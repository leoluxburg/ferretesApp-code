from flask_login import UserMixin
from . import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    irons = db.relationship('Iron', backref='user', lazy = True)

class Iron(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(200), nullable = False)
    cedula = db.Column(db.String(200), nullable = False)
    domicilio = db.Column(db.String(600), nullable = False)
    correo = db.Column(db.String(600), nullable = False)
    telefono = db.Column(db.String(600), nullable = False)
    fecha_registro = db.Column(db.DateTime, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)



from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))  # Column to store the name of the file
    data = db.Column(db.LargeBinary)
    tag = db.Column(db.LargeBinary)
    nonce = db.Column(db.LargeBinary)
    encrypted_aes_key = db.Column(db.LargeBinary)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    files = db.relationship('File')
    public_key = db.Column(db.Text, nullable=True)
    private_key = db.Column(db.Text, nullable=True)
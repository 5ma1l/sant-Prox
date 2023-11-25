from flask import Flask,render_template,url_for,g,request
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sante_prox.db"
db = SQLAlchemy(app)

class Hospitals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    ville = db.Column(db.String, nullable=False)
    media_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Hospital(id={self.id}, name={self.name}, location={self.location}, type={self.type}, ville={self.ville}, media_id={self.media_id})"

class Pharmacie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Pharmacie(id={self.id}, name={self.name}, address={self.address},city={self.city},location={self.location},phone_number={self.phone_number}"

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    isAdmin = db.Column(db.Integer)
    location = db.Column(db.String)
    ville = db.Column(db.String)
    date_inscription = db.Column(db.Date, nullable=False)
    media_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, password={self.password}, isAdmin={self.isAdmin}, location={self.location}, ville={self.ville}, date_inscription={self.date_inscription}, media_id={self.media_id})"


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    fichier = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Media(id={self.id}, type={self.type}, fichier={self.fichier})"


class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, nullable=True)
    pharmacie_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Service(id={self.id}, hospital_id={self.hospital_id}, pharmacie_id={self.pharmacie_id})"


class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Discussion(id={self.id}, contenu={self.contenu}, user_id={self.user_id}, service_id={self.service_id})"


class Urgence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    service_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Urgence(id={self.id}, description={self.description}, user_id={self.user_id}, service_id={self.service_id})"

class Avis(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commentaire = db.Column(db.Text)
    note = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    service_id = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)

    def __repr__(self):
        return f"Avis(id={self.id}, commentaire={self.commentaire}, note={self.note}, user_id={self.user_id}, service_id={self.service_id}, datetime={self.datetime})"

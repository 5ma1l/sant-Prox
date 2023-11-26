from main import *
from math import radians, sin, cos, sqrt, atan2
import re
from werkzeug.security import generate_password_hash, check_password_hash

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6371.0
    distance = radius * c
    return distance

def getClosestServices(user_lat, user_lon, service_type='Tout', num_services=5):
    services = {
        'Pharmacies':None,
        'Hopitaux':None
    }
    closest_services={
        'Pharmacies':None,
        'Hopitaux':None
    }
    if service_type.title() in ('Pharmacie','Tout'):
        services['Pharmacies']=Pharmacie.query.all()
        distances = [(service, haversine(user_lat, user_lon, float(service.location.split(',')[0]), float(service.location.split(',')[1])))
                    for service in services['Pharmacies']]
        sorted_distances = sorted(distances, key=lambda x: x[1])
        closest_services['Pharmacies'] = sorted_distances[:num_services]
    if service_type.title() in ('Hopital','Tout'):
        services['Hopitaux'] = Hospitals.query.all()
        distances = [(service, haversine(user_lat, user_lon, float(service.location.split(',')[0]), float(service.location.split(',')[1])))
                    for service in services['Hopitaux']]
        sorted_distances = sorted(distances, key=lambda x: x[1])
        closest_services['Hopitaux'] = sorted_distances[:num_services]
    return closest_services

def getServiceIdForPharmacie(id):
    service_entry = Services.query.filter_by(pharmacie_id=id).first()
    return service_entry.id

def getServiceIdForHospital(id):
    service_entry = Services.query.filter_by(hospital_id=id).first()
    return service_entry.id


def update_location(data):
    location=str(data['latitude'])+', '+str(data['longitude'])
    if current_user.is_authenticated:
        user=Users.query.get(current_user.id)
        user.location=location
        db.session.commit()
        login_user(user)


def is_valid_password(password):
    if len(password) < 8:
        flash("Le mot de passe doit comporter au moins 8 caractères.", category='error')
        return False

    if not any(char.isupper() for char in password):
        flash("Le mot de passe doit contenir au moins une lettre majuscule.", category='error')
        return False

    if not any(char.islower() for char in password):
        flash("Le mot de passe doit contenir au moins une lettre minuscule.", category='error')
        return False

    if not any(char.isdigit() for char in password):
        flash("Le mot de passe doit contenir au moins un chiffre.", category='error')
        return False

    return True

def is_valid_signup(full_name, email, phone_number, password1, password2):
    if Users.query.filter_by(email=email).first():
        flash('Email already exists.', category='error')
        return False

    if len(full_name) < 4:
        flash("Full name must be greater than 3 characters.", category='error')
        return False

    if not re.match(r'^\d{10}$', phone_number):
        flash('Phone number is not correct.', category='error')
        return False

    if password1 != password2:
        flash("Passwords don't match.", category='error')
        return False

    if len(password1) < 8:
        flash("Password must be at least 8 characters.", category='error')
        return False

    return True

def update_user_profile(username, email, telephone, fullname, password):
    if username:
        current_user.username = username

    if email:
        current_user.email = email

    if telephone:
        current_user.phone_number = telephone

    if fullname:
        current_user.full_name = fullname

    if password:
        current_user.password = generate_password_hash(password)

    db.session.commit()
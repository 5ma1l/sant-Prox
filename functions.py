from main import *
from math import radians, sin, cos, sqrt, atan2

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
    search_value=str(data['latitude'])+', '+str(data['longitude'])
    if current_user.is_authenticated:
        user=Users.query.get(current_user.id)
        user.location=search_value
        db.session.commit()
        login_user(user)
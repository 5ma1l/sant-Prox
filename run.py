from main import *
from functions import *

@app.route('/')
def home():
    g.connected=False
    return render_template('home.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/forgetpassword')
def forgetPassword():
    return render_template('forgetpassword.html')

@app.route('/service',methods=['POST'])
def service():
    data=request.form
    keys=list(data.keys())
    if 'type' in keys and  data['latitude']!='':
        services=getClosestServices(float(data['latitude']),float(data['longitude']),data['type'])
        pharmacies=[service for service, _ in services['Pharmacies']] if services['Pharmacies']!=None else None
        hopitaux=[service for service, _ in services['Hopitaux']] if services['Hopitaux']!=None else None
        search_value=str(data['latitude'])+', '+str(data['longitude'])
        return render_template('service.html',pharmacies=pharmacies,hopitaux=hopitaux,search_value=search_value,getServiceIdForHospital=getServiceIdForHospital,getServiceIdForPharmacie=getServiceIdForPharmacie)
    elif not data['input']:
        return render_template('service.html',services=None)
    else:
        pharmacies=None
        hopitaux=None
        with app.app_context():
            search_value=data['input']
            if data['type'] in ('Tout','Pharmacie'):
                pharmacies = Pharmacie.query.filter(db.func.lower(Pharmacie.address +', '+ Pharmacie.city+', '+Pharmacie.name).like(f'%{search_value.lower()}%')).all()
            if data['type'] in ('Tout','Hopital'):
                hopitaux= Hospitals.query.filter(db.func.lower(Hospitals.ville+', '+Hospitals.name).like(f'%{search_value.lower()}%')).all()
        return render_template('service.html',pharmacies=pharmacies,hopitaux=hopitaux,search_value=search_value,getServiceIdForHospital=getServiceIdForHospital,getServiceIdForPharmacie=getServiceIdForPharmacie)

@app.route('/serviceinfo/<id>')
def serviceinfo(id):
    service={
    'pharmacie':['rabat'],
    'hospital':['casa']
}
    return render_template('serviceinfo.html',service=service)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    services=getClosestServices(float(data['latitude']),float(data['longitude']))
    pharmacies=[service for service, _ in services['Pharmacies']] if services['Pharmacies']!=None else None
    hopitaux=[service for service, _ in services['Hopitaux']] if services['Hopitaux']!=None else None
    search_value=str(data['latitude'])+', '+str(data['longitude'])
    return render_template('service.html',pharmacies=pharmacies,hopitaux=hopitaux,search_value=search_value,getServiceIdForHospital=getServiceIdForHospital,getServiceIdForPharmacie=getServiceIdForPharmacie)


if __name__=='__main__':
    app.run(debug=True)
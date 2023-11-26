from main import *
from functions import *
from werkzeug.utils import secure_filename
import json

@app.route('/')
def home():
    g.connected=True
    return render_template('home.html')



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/emergency', methods=['POST','GET'])
def emergency():
    session["username"]="test"
    if "username" in session:
        if request.method=='GET':
            user = Users.query.filter_by(username=session["username"]).first()
            type=user.type
            if type=="client":
                emergencies=Urgence.query.filter_by(user_id=user.id).all()
                hospital=None
                if emergencies:
                    for emergency in emergencies:
                        service=Services.query.filter_by(id=emergency.service_id).first()
                        hospital=Hospitals.query.filter_by(id=service.hospital_id).first()
                        emergency.hospital_name=hospital.name
                        emergency.ville=hospital.ville
                return render_template("emergency_historique.html",emergencies=emergencies,type=type)
            else:
                hospital=Hospitals.query.filter_by(name=session["username"]).first()
                service=Services.query.filter_by(hospital_id=hospital.id).first()
                emergencies=Urgence.query.filter_by(service_id=service.id).all()
                return render_template("emergency_historique.html",emergencies=emergencies,type=user)
        else:
            data = request.get_json()
            emergency_id = data.get('emergency_id')
            action = data.get('action')

            emergency = Urgence.query.get(emergency_id)
            if emergency:
                emergency.statut = action
                db.session.commit()
            return redirect(url_for("emergency"))

    else:
        return redirect(url_for("login"))

@app.route('/send-emergency', methods=['POST','GET'])
def add_urgence():
    if "username" in session:
        if request.method=='GET':
            return render_template("emergency.html")
        else:
            user = Users.query.filter_by(username=session["username"]).first()

            description = request.form['message']
            location = json.loads(request.form['location'])
            filename=None

            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            localisation=(location["latitude"],location["longitude"])
            hospital=getClosestServices(localisation[0],localisation[1],service_type='Hopital',num_services=1)['Hopitaux'][0][0]
            service=Services.query.filter_by(hospital_id=hospital.id).first()

            new_urgence = Urgence(description=description, image=filename, localisation=str(localisation), service_id=service.id, user_id=user.id, statut="attendre la décision du service")
            db.session.add(new_urgence)
            db.session.commit()

            return redirect(url_for('emergency'))
    else:
        return redirect(url_for("login"))

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

@app.route('/aboutus')
def aboutUs():
    return render_template('ourteam.html')


if __name__=='__main__':
    app.run(debug=True)
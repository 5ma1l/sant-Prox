from main import *
from functions import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in succefully!', category='success')
                return redirect(url_for('home'))

        flash('Your credential is an incorrect.', category='error')
        return redirect(url_for('login'))
    else:
        return render_template("login.html",Text='')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        full_name = request.form.get('fullName')
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phoneNumber')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Users.query.filter_by(email=email).first()
        if user:
             flash('Email already exists.', category='error')
        if len(full_name) < 4:
            flash("Full name must be greater than 3 character.", category='error')
        elif len(email) < 5:
            flash('Email is too short.', category='error')
        elif len(phone_number) != 10:
            flash('Phone number is not correct.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 8:
            flash("Password must be at least 7 characters.", category='error')
        else:
            new_user = Users(email=email, full_name=full_name, username=username, phone_number=phone_number, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category='success')
            
            return redirect(url_for('home'))

    return render_template("signup.html")


@app.route('/emergency', methods=['POST','GET'])
@login_required
def emergency():
    if current_user.is_authenticated:
        if request.method=='GET':
            user = current_user
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
                hospital=Hospitals.query.filter_by(name=current_user).first()
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
    if current_user.is_authenticated:
        if request.method=='GET':
            return render_template("emergency.html")
        else:
            user = current_user
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
def forgetpassword():
    return render_template('forgetpassword.html')

@app.route('/service',methods=['POST'])
def service():
    data=request.form
    keys=list(data.keys())
    if 'type' in keys and  data['latitude']!='':
        update_location(data)
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

 
@app.route('/aboutus')
def aboutUs():
    return render_template('ourteam.html')


if __name__=='__main__':
    app.run(debug=True)
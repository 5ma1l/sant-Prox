from main import *
from functions import *
from werkzeug.utils import secure_filename
import json
import re

@app.route('/')
def home():
    if current_user.is_authenticated :
        if current_user.type!='client':
            return redirect(url_for('profile'))
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

        if is_valid_signup(full_name, email, phone_number, password1, password2) and is_valid_password(password1):
            new_user = Users(email=email, full_name=full_name, username=username, phone_number=phone_number, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category='success')
            return redirect(url_for('home'))

    return render_template("signup.html")


@app.route('/emergency', methods=['POST','GET'])
@login_required
def emergency():
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
            return render_template("emergency_historique.html",emergencies=emergencies)
        else:
            hospital=Hospitals.query.filter_by(name=current_user.full_name).first()
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

@app.route('/send-emergency', methods=['POST','GET'])
def add_urgence():
    if current_user.is_authenticated:
        if current_user.type=='client':
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
            redirect(url_for('profile'))
    else:
        return redirect(url_for("login"))

@app.route('/forgetpassword')
def forgetpassword():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template('forgetpassword.html')

@app.route('/service',methods=['GET','POST'])
def service():
    if current_user.is_authenticated :
        if current_user.type!='client':
            return redirect(url_for('home'))
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
@app.route('/service/<id>',methods=['GET','POST'])
@login_required
def serviceinfo(id):
    if current_user.is_authenticated :
        if current_user.type!='client':
            return redirect(url_for('home'))
    comment=[]
    user=current_user
    service = Services.query.filter_by(id=id).first()
    if service:
        pharmacie = Pharmacie.query.filter_by(id=service.pharmacie_id).first()
        hopital = Hospitals.query.filter_by(id=service.hospital_id).first()
    if request.method == 'POST':
        comment= request.form['comment']
        avis = Avis( commentaire=comment,user_id=user.id,service_id=id)
        db.session.add(avis)
        db.session.commit()
    comments=Avis.query.filter_by(service_id=id)
    return render_template('serviceinfo.html', pharmacie=pharmacie, hopital=hopital,comments=comments,get_username=get_username,id=id)

@app.route('/profile')
@login_required
def profile():
    img=Media.query.get(current_user.media_id).fichier
    return render_template('profile.html',img=img)

@app.route('/updateprofile', methods=['POST'])
@login_required
def updateprofile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_address = request.form.get('address')
        new_telephone = request.form.get('telephone')
        new_fullname = request.form.get('fullname')
        new_password = request.form.get('password')
        rpassword = request.form.get('rpassword')

        if new_username and re.search(r'\s', new_username):
            flash('Le nom d\'utilisateur ne doit pas contenir d\'espaces', 'error')
        elif new_address and not re.match(EMAIL_REGEX, new_address):
            flash('Adresse e-mail invalide', 'error')
        elif new_password and not is_valid_password(new_password):
            pass  # is_valid_password will handle the flash messages
        elif new_password and new_password != rpassword:
            flash('Les mots de passe ne correspondent pas', 'error')
        elif not is_valid_signup(new_fullname, new_address, new_telephone, new_password, rpassword):
            pass  # is_valid_signup will handle the flash messages
        else:
            if Users.query.filter_by(username=new_username).filter(Users.id != current_user.id).first():
                flash('Ce nom d\'utilisateur est déjà utilisé, veuillez en choisir un autre', 'error')
            elif Users.query.filter_by(email=new_address).filter(Users.id != current_user.id).first():
                flash('Cette adresse e-mail est déjà associée à un compte, veuillez en choisir une autre', 'error')
            elif new_telephone and not re.match(r'^\d{10}$', new_telephone):
                flash('Le numéro de téléphone doit comporter 10 chiffres', 'error')
            else:
                update_user_profile(new_username, new_address, new_telephone, new_fullname, new_password)
                flash('Profil mis à jour avec succès', 'success')

    return redirect(url_for('profile'))

@app.route('/hospitalprofile')
def hospitalProfile():
    return render_template('hospitalprofile.html')
 
@app.route('/aboutus')
def aboutUs():
    return render_template('ourteam.html')


if __name__=='__main__':
    app.run(debug=True)
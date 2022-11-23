from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import datetime
import uuid

load_dotenv()

mysql_username = os.getenv("MYSQL_USERNAME")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://' + mysql_username + \
    ':' + mysql_password + '@' + mysql_host + ':3306/patient_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sdf#$#dfjkhdf0SDJH0df9fd98343fdfu34rf'

db.init_app(app)

### Models ###


class Users(db.Model):
    __tablename__ = 'production_accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    account_type = db.Column(db.String(80), nullable=False)
    mrn = db.Column(db.String(80), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp(
    ), onupdate=db.func.current_timestamp())

    def __init__(self, username, password, email, account_type, mrn, date_created, last_login):
        self.username = username
        self.password = password
        self.email = email
        self.account_type = account_type
        self.mrn = mrn
        self.date_created = date_created
        self.last_login = last_login

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'account_type': self.account_type,
            'mrn': self.mrn,
            'date_created': self.date_created,
            'last_login': self.last_login
        }


class Patients(db.Model):
    __tablename__ = 'production_patients'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    zip_code = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(255), nullable=True)
    contact_mobile = db.Column(db.String(255), nullable=True)
    contact_home = db.Column(db.String(255), nullable=True)

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_home):
        self.mrn = mrn
        self.first_name = first_name
        self.last_name = last_name
        self.zip_code = zip_code
        self.dob = dob
        self.gender = gender
        self.contact_mobile = contact_mobile
        self.contact_home = contact_home

    # this second function is for the API endpoints to return JSON

    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'zip_code': self.zip_code,
            'dob': self.dob,
            'gender': self.gender,
            'contact_mobile': self.contact_mobile,
            'contact_home': self.contact_home
        }


class Conditions_patient(db.Model):
    __tablename__ = 'production_patient_conditions'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('production_patients.mrn'))
    icd10_code = db.Column(db.String(255), db.ForeignKey(
        'production_conditions.icd10_code'))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, icd10_code):
        self.mrn = mrn
        self.icd10_code = icd10_code

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'icd10_code': self.icd10_code
        }


class Conditions(db.Model):
    __tablename__ = 'production_conditions'

    id = db.Column(db.Integer, primary_key=True)
    icd10_code = db.Column(db.String(255))
    icd10_description = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, icd10_code, icd10_description):
        self.icd10_code = icd10_code
        self.icd10_description = icd10_description

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'icd10_code': self.icd10_code,
            'icd10_description': self.icd10_description
        }


class Medications_patient(db.Model):
    __tablename__ = 'production_patient_medications'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('production_patients.mrn'))
    med_ndc = db.Column(db.String(255), db.ForeignKey(
        'production_medications.med_ndc'))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, med_ndc):
        self.mrn = mrn
        self.med_ndc = med_ndc

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'med_ndc': self.med_ndc
        }


class Medications(db.Model):
    __tablename__ = 'production_medications'

    id = db.Column(db.Integer, primary_key=True)
    med_ndc = db.Column(db.String(255))
    med_human_name = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, med_ndc, med_human_name):
        self.med_ndc = med_ndc
        self.med_human_name = med_human_name

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'med_ndc': self.med_ndc,
            'med_human_name': self.med_human_name
        }


#### BASIC ROUTES WITHOUT DATA PULSL FOR NOW ####
@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = Users.query.filter_by(
            username=username, password=password).first()
        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['mrn'] = account.mrn
            session['username'] = account.username
            session['account_type'] = account.account_type
            msg = 'Logged in successfully !'
            # push update to user with new login time
            account.last_login = datetime.datetime.now()
            db.session.commit()
            if session['account_type'] == 'admin':
                return redirect(url_for('get_gui_patients'))
            elif session['account_type'] == 'patient':
                # go to /details/{{row.mrn}}
                return redirect(url_for('get_patient_details', mrn=session['mrn']))
        else:
            msg = 'Incorrect username / password !'
    return render_template('/login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'account_type' in request.form:
        if request.form['account_type'] == 'admin':
            # redirect to admin registration page
            return redirect(url_for('register_admin'))
        elif request.form['account_type'] == 'patient':
            # redirect to patient registration page
            return redirect(url_for('register_patient'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account_type = 'admin'
        mrn = None
        # check if email already exists
        account = Users.query.filter_by(email=email).first()
        if account:
            msg = 'Account already exists !'
        else:
            datecreated = datetime.datetime.now()
            lastlogin = datetime.datetime.now()
            new_user = Users(username, password, email,
                             account_type, mrn, datecreated, lastlogin)
            db.session.add(new_user)
            db.session.commit()
            msg = "You have successfully registered a ADMIN account!"
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register_admin.html', msg=msg)


@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():

    db_conditions = Conditions.query.all()
    db_medications = Medications.query.all()

    print('count of conditions loaded: ', len(db_conditions))
    print('count of medications loaded: ', len(db_medications))

    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        mrn = str(uuid.uuid4())[:8]
        account_type = 'patient'

        # Fields to capture for account table
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Fields to capture for patient table
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        zip_code = request.form['zip_code']
        dob = request.form['dob']
        gender = request.form['gender']
        contact_mobile = request.form['contact_mobile']
        contact_home = request.form['contact_home']

        # Fields to capture patient conditions
        pt_conditions = request.form.getlist('conditions')
        print('pt_conditions: ', pt_conditions)

        # check if email already exists in account table or contact_mobile already exists in patient table
        account = Users.query.filter_by(email=email).first()
        patient = Patients.query.filter_by(
            contact_mobile=contact_mobile).first()
        if account or patient:
            msg = 'Account already exists !'
        else:
            datecreated = datetime.datetime.now()
            lastlogin = datetime.datetime.now()

            new_user = Users(username, password, email,
                             account_type, mrn, datecreated, lastlogin)
            new_patient = Patients(
                mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_home)

            db.session.add(new_user)
            db.session.commit()
            db.session.add(new_patient)
            db.session.commit()

            # then loop through each condition and add to patient_conditions table after patient has been added to pt table
            for condition in pt_conditions:
                new_patient_condition = Conditions_patient(mrn, condition)
                db.session.add(new_patient_condition)
                db.session.commit()

            msg = 'You have successfully registered a PATIENT account !'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register_patient.html', msg=msg, conditions=db_conditions, medications=db_medications)


@app.route('/account')
def account():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all account data for logged in user
        account = Users.query.filter_by(id=session['id']).first()
        print('Account details: ', account.to_json())
        # Show the profile page with account info
        return render_template('account.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('dashboard.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


##### CREATE BASIC GUI FOR CRUD #####
@app.route('/patients', methods=['GET'])
def get_gui_patients():
    if 'loggedin' in session and session['account_type'] == 'admin':
        # documentation for .query exists: https://docs.sqlalchemy.org/en/14/orm/query.html
        returned_Patients = Patients.query.all()
        return render_template("patient_all.html", patients=returned_Patients)
    else:
        return redirect(url_for('get_patient_details', mrn=session['mrn']))

# this endpoint is for inserting in a new patient


@app.route('/insert', methods=['POST'])
def insert():  # note this function needs to match name in html form action
    if request.method == 'POST':
        mrn = request.form['mrn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        zip_code = request.form['zip_code']
        new_patient = Patients(mrn, first_name, last_name, gender, zip_code)
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient Inserted Successfully")
        return redirect(url_for('get_gui_patients'))
    else:
        flash("Something went wrong")
        return redirect(url_for('get_gui_patients'))

# this endpoint is for updating our patients basic info


@app.route('/update', methods=['GET', 'POST'])
def update():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_mrn = request.form.get('mrn')
        patient = Patients.query.filter_by(mrn=form_mrn).first()
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.gender = request.form.get('gender')
        db.session.commit()
        flash("Patient Updated Successfully")
        return redirect(url_for('get_gui_patients'))

# This route is for deleting our patients


@app.route('/delete/<string:mrn>', methods=['GET', 'POST'])
def delete(mrn):  # note this function needs to match name in html form action
    patient = Patients.query.filter_by(mrn=mrn).first()
    print('Found patient: ', patient)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient Deleted Successfully")
    return redirect(url_for('get_gui_patients'))


# This route is for getting patient details
@app.route('/details/<string:mrn>', methods=['GET'])
def get_patient_details(mrn):
    patient_details = Patients.query.filter_by(mrn=mrn).first()
    patient_conditions = Conditions_patient.query.filter_by(mrn=mrn).all()
    patient_medications = Medications_patient.query.filter_by(mrn=mrn).all()
    db_conditions = Conditions.query.all()
    db_medications = Medications.query.all()
    print('Number of conditions total loaded: ', len(db_conditions))
    print('Number of medications total loaded: ', len(db_medications))
    return render_template("patient_details.html", patient_details=patient_details,
                           patient_conditions=patient_conditions, patient_medications=patient_medications,
                           db_conditions=db_conditions, db_medications=db_medications)


# this endpoint is for updating ONE patient condition
@app.route('/update_conditions', methods=['GET', 'POST'])
def update_conditions():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_id = request.form.get('id')
        print('form_id', form_id)
        form_icd10_code = request.form.get('icd10_code')
        print('form_icd10_code', form_icd10_code)
        patient_condition = Conditions_patient.query.filter_by(
            id=form_id).first()
        print('patient_condition', patient_condition)
        patient_condition.icd10_code = request.form.get('icd10_code')
        db.session.commit()
        flash("Patient Condition Updated Successfully")
        # then return to patient details page
        return redirect(url_for('get_patient_details', mrn=patient_condition.mrn))


# this endpoint is for adding a new condition to a patient
@app.route('/add_condition', methods=['GET', 'POST'])
def add_condition():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_mrn = request.form.get('mrn')
        print('form_mrn', form_mrn)
        form_icd10_code = request.form.get('icd10_code')
        print('form_icd10_code', form_icd10_code)
        new_condition = Conditions_patient(form_mrn, form_icd10_code)
        db.session.add(new_condition)
        db.session.commit()
        flash("Patient Condition Added Successfully")
        # then return to patient details page
        return redirect(url_for('get_patient_details', mrn=form_mrn))


@app.route('/add_medication', methods=['GET', 'POST'])
def add_medication():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_mrn = request.form.get('mrn')
        print('form_mrn', form_mrn)
        form_ndc_code = request.form.get('med_ndc')
        print('form_icd10_code', form_ndc_code)
        new_medication = Medications_patient(form_mrn, form_ndc_code)
        db.session.add(new_medication)
        db.session.commit()
        flash("Patient Medication Added Successfully")
        # then return to patient details page
        return redirect(url_for('get_patient_details', mrn=form_mrn))

# this endpoint is for deleting a condition from a patient


@app.route('/delete_condition', methods=['GET', 'POST'])
def delete_condition():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_mrn = request.form.get('mrn')
        form_icd10_code = request.form.get('icd10_code')
        print('form_id', form_mrn)
        print('form_icd10_code', form_icd10_code)
        patient_condition = Conditions_patient.query.filter_by(
            mrn=form_mrn, icd10_code=form_icd10_code).all()
        print('Found conditions: ', patient_condition)
        for condition in patient_condition:
            db.session.delete(condition)
        db.session.commit()
        flash("Patient Condition Deleted Successfully")
        # then return to patient details page
        return redirect(url_for('get_patient_details', mrn=form_mrn))


##### CREATE BASIC API ENDPOINTS #####
# get all Patients
@app.route("/api/patients/list", methods=["GET"])
def get_patients():
    if 'loggedin' in session and session['account_type'] == 'admin':
        patients = Patients.query.all()
        return jsonify([patient.to_json() for patient in patients])
    else:
        return jsonify({'error': 'Not logged in as admin user, try again....'})

# get specific Patient by MRN


@app.route("/api/patients/<string:mrn>", methods=["GET"])
def get_patient(mrn):
    # get patient by mrn column
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    return jsonify(patient.to_json())

# BASIC POST ROUTES ##### [isnert new data into the database]
# new patient


@app.route('/api/patient', methods=['POST'])
def create_patient():
    if not request.json:
        abort(400)
    patient = Patients(
        mrn=request.json.get('mrn'),
        first_name=request.json.get('first_name'),
        last_name=request.json.get('last_name')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_json()), 201

# BASIC PUT ROUTES ##### [updating existing data]
# update patient


@app.route('/api/patient/<string:mrn>', methods=['PUT'])
def update_patient(mrn):
    if not request.json:
        abort(400)
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    patient.first_name = request.json.get('first_name', patient.first_name)
    patient.last_name = request.json.get('price', patient.last_name)
    db.session.commit()
    return jsonify(patient.to_json())


##### BASIC DELETE ROUTES #####
# delete patient
@app.route("/api/patient/<string:mrn>", methods=["DELETE"])
def delete_patient(mrn):
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=81)

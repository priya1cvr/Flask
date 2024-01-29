import sqlite3

from flask import Flask, render_template, url_for,redirect,request,session,render_template_string,make_response
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import re
import cv2


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.app_context().push()

class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"Register('{self.username}','{self.email}')"

    username = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

#@app.route('/',methods=['GET','POST'])
#def index():
#    return render_template('index.html')

@app.route("/upload", methods=['GET','POST'])
def upload():
    faceDetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cam = cv2.VideoCapture(0);
    sampleNum = 0
    pathDataset = "/Users/priyabratkumarbishwal/Documents/Techie/Python/SCBAccelerate/cameraImages/"
    print("req method")
    print(request.method)
    if request.method == 'GET':
        print("get ",request.form.get('email'))
        connection = sqlite3.connect(
            '/Users/priyabratkumarbishwal/Documents/Techie/Python/SCBAccelerate/instance/register.db')
        cursor = connection.cursor()
        id = cursor.execute(f'SELECT max(id) FROM register').fetchall()[0][0]
        email = cursor.execute(f"SELECT email FROM register WHERE id = {id} ").fetchall()[0][0]

        #username = request.form.get('username')
        #email = request.form.get('email')
        #password = request.form['password']
        print("email:", email)
        connection.close()
    while (True):
        ret, img = cam.read();
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3, 5);
        for (x, y, w, h) in faces:
            sampleNum = sampleNum + 1;
            cv2.imwrite(pathDataset + f"dataSet/{email}" + "_" + str(sampleNum) + ".jpg",
                        gray[y:y + h, x:x + w])
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.waitKey(100);
        #cv2.imshow("Face", img);
        cv2.waitKey(1);
        if (sampleNum > 50):
            break;
    cam.release()
    cv2.destroyAllWindows()
    return 'Your Picture is Sucessfully captured'





@app.route('/register',methods=['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form  and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print("first:"+request.method)
        connection = sqlite3.connect(
            '/Users/priyabratkumarbishwal/Documents/Techie/Python/SCBAccelerate/instance/register.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM register WHERE email = '{email}' AND username ='{username}' ")
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
            print(msg)
        else:
            print("first")
            #user = Register(username=username, email=email, password=password)
            #db.session.add(user)
            #db.session.commit()
            id =cursor.execute(f'SELECT max(id) FROM register').fetchall()[0][0]+1
            print("id"+str(id))
            cursor.execute(f"INSERT INTO register VALUES  ({id},'{username}', '{email}' , '{password}')")
            connection.commit()
            msg = f'{username} is Sucessfully Registered'
            print(msg)
    elif request.method == 'POST':
            msg = 'Please fill out the form !'
            print(msg)
    return render_template('register.html', msg=msg)

@app.route('/users')
def users():
    users = Register.query.all()
    return render_template('users.html',users=users)

@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
   msg =''
   if request.method == 'POST' and 'username' in request.form:
       username = request.form['username']
       #email = request.form['email']
       password = request.form['password']
       connection = sqlite3.connect('/Users/priyabratkumarbishwal/Documents/Techie/Python/SCBAccelerate/instance/register.db')
       cursor = connection.cursor()
       cursor.execute(f"SELECT * FROM register WHERE username = '{username}'")
       account = cursor.fetchone()
       print(account)
       if account:
           session['loggedin'] = True
           session['id'] = account[0]
           session['username'] = account[1]
           msg = 'Logged in successfully !'
           return render_template('index1.html', msg=msg)
       else:
           msg = 'Incorrect username / password !'
   return render_template('login.html', msg=msg)

@app.route('/webcam')
def webCamindex():
    print("request")
    print(request.method)
    return render_template('image_capture.html')




if __name__=='__main__':
    app.run(debug=True)
    exit(0)
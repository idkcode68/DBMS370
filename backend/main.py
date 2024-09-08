from flask import Flask, redirect, render_template,flash,request
from flask.globals import request, session
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, login_user, LoginManager, current_user
from sqlalchemy import text
import json 
from flask.helpers import url_for

# from flask_mail import Mail


# I am getting error like this..AttributeError: 'Engine' object has no attribute 'execute' .  I am using SQLalchemy  2.0.30 version. I googled and found out that  in the new version of SqlAlchemy execute method is not supported any more. Please help me how to correct this.

# my database connection
local_server = True
app = Flask(__name__)
app.secret_key = "qwerty"


# with open('config.json', 'r') as c:
#     params=json.load(c)["params"]



# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-password']
# )
# mail = Mail(app)


# this is for getting the unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/san_maria_tunes'
db = SQLAlchemy(app)







@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100))
    dob = db.Column(db.String(1000))

class Artistuser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Acode = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000))

class Artistdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Acode = db.Column(db.String(20), unique=True)
    Aname = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    records = db.Column(db.Integer)
    label = db.Column(db.String(100))

class Trackallot(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),unique=True)
    genretype=db.Column(db.String(100))
    Acode=db.Column(db.String(20))
    duration=db.Column(db.Integer)
    albumname=db.Column(db.String(100))
    albumlabel=db.Column(db.String(100))
    releasedate = db.Column(db.Date)






@app.route("/")
def home():
    return render_template("index.html")

@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        dob=request.form.get('dob')
        user=User.query.filter_by(name=name).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email is already taken","warning")
            return render_template("usersignup.html")
        new_user=User(name=name,email=email,dob=dob)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")
    # eikhane thik eki ee bhabe flash use kore amader message ta dibo, then dewar por oita amader index or home ee redirect hobe (index ee dewa tai beshi better)



@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        name=request.form.get('name')
        dob=request.form.get('dob')
        user=User.query.filter_by(name=name).first()
        if user and user.dob==dob:
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")


@app.route('/artistlogin', methods=['POST', 'GET'])
def artistlogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user=Artistuser.query.filter_by(email=email).first()

        if user and user.password==password:
            login_user(user)
            flash("login success", "info")
            return render_template("index.html")
        else:
            flash("Inappropriate Credentials", "danger")
            return render_template("artistlogin.html")
     
    
    return render_template("/artistlogin.html")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if(username=="admin" and password=="admin"):
            session['user'] = username
            flash("Login Success", "info")
            return render_template("addArtistUser.html")
        else:
            flash("Invalid Credentials", "danger")
    
    return render_template("/admin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

# eikhane login korte gele kintu jhamela hobe aagei, dekhabe login hobe na ei shei, **eitar solution hoilo google er 2 step verification bondho kora lagbe, bondho kore tarpor try korle tokhon hobe
# Rename the function to avoid name collision with the model
@app.route('/addArtistUser', methods=['POST', 'GET'])
def artistuser():
    
    if 'user' in session and session['user']=="admin":
        if request.method == "POST":
            Acode = request.form.get('Acode')
            email = request.form.get('email')
            password = request.form.get('password')
            # encpassword = generate_password_hash(password)
            Acode=Acode.upper()
            # Use the model to query the database
            emailUser = Artistuser.query.filter_by(email=email).first()
            if emailUser:
                flash("Email is already taken", "warning")
                
            query=Artistuser(Acode=Acode,email=email,password=password)
            db.session.add(query)
            db.session.commit()
            
            # mail.send_message(
            #     'Music Management System',
            #     sender=params['gmail-user'],
            #     recipients=[email],
            #     body=f"Welcome thank you for choosing us\nYour Credentials Are:\nEmail Address: {email}\nPassword: {password}\n\nHospital Code {Acode}\n Do not share your information\n\n\n Thanks"
            # )
            
            flash("Data Inserted", "warning")
            return render_template("addArtistUser.html")
        
        
    else:
        flash("Login and try Again", "warning")
        return render_template("addArtistUser.html")






# testing whether db is connected or not
# pore eita try korsi, its actually not connected at all
# testing wheather db is connected or not  
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'



@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')


# @login_required na dile dekhai hoilo  (AttributeError AttributeError: 'AnonymousUserMixin' object has no attribute 'email' Traceback (most recent call last); chatgpt amake ei solution ta dise pore 

@app.route("/addartistinfo", methods=['POST', 'GET'])
@login_required

def addartistinfo():
        email = current_user.email
        posts = Artistuser.query.filter_by(email=email).first()
        code=posts.Acode
        postsdata=Artistdata.query.filter_by(Acode=code).first()
        
        if request.method == "POST":
            Acode = request.form.get('Acode')
            Aname = request.form.get('Aname')
            genre = request.form.get('Genre')
            records = request.form.get('Records')
            label = request.form.get('Label')
            Acode = Acode.upper()

            auser = Artistuser.query.filter_by(Acode=Acode).first()
            aduser = Artistdata.query.filter_by(Acode=Acode).first()
            if aduser:
                flash("Data is already Present you can update it", "primary")
                return render_template("artistdata.html")  
            if auser:
                query=Artistdata(Acode=Acode,Aname=Aname,genre=genre,records=records,label=label)
                db.session.add(query)
                db.session.commit()
                flash("Data is Added", "primary")
                return redirect('/addartistinfo')
            else:
                flash("Artist Code does not exist", "warning")
                return redirect('/addartistinfo')

        return render_template("artistdata.html", postsdata=postsdata)  
    

 
@app.route("/aedit/<string:id>", methods=['POST','GET'])
@login_required
def aedit(id):
    posts=Artistdata.query.filter_by(id=id).first()
    if request.method == "POST":
            Acode = request.form.get('Acode')
            Aname = request.form.get('Aname')
            genre = request.form.get('Genre')
            records = request.form.get('Records')
            label = request.form.get('Label')
            Acode = Acode.upper()
            post=Artistdata.query.filter_by(id=id).first()
            post.Acode=Acode
            post.Aname=Aname
            post.genre=genre
            post.records=records
            post.label=label
            db.session.commit()
            flash("Slot Updated", "danger")
            return render_template("/addartistinfo")


    return render_template("aedit.html",posts=posts)



@app.route("/adelete/<string:id>", methods=['POST','GET'])
@login_required
def adelete(id):
    post=Artistdata.query.filter_by(id=id).first()
    db.session.delete(post)
    flash("Date Deleted", "danger")
    return redirect("/addartistinfo")




app.run(debug=True)
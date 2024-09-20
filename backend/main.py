from flask import Flask, redirect, render_template,flash,request
from flask.globals import request, session
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, login_user, LoginManager, current_user
from sqlalchemy import text
import json 
from flask.helpers import url_for
from datetime import datetime
from flask_login import current_user
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
# Initialize the SQLAlchemy object



# from flask_mail import Mail




# my database connection
local_server = True
app = Flask(__name__)
app.secret_key = "qwerty"




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
    Genre = db.Column(db.String(100))
    Records = db.Column(db.Integer)
    Label = db.Column(db.String(100))



class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User table

    def __repr__(self):
        return '<Playlist %r>' % self.id

class Concert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100))  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User table

    def __repr__(self):
        return '<Concert %r>' % self.id





 


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


# Rename the function to avoid name collision with the model
@app.route('/addArtistUser', methods=['POST', 'GET'])
def artistuser():
    if 'user' in session and session['user'] == "admin":
        if request.method == "POST":
            Acode = request.form.get('Acode')
            email = request.form.get('email')
            password = request.form.get('password')
            Acode = Acode.upper()
            
            emailUser = Artistuser.query.filter_by(email=email).first()
            if emailUser:
                flash("Email is already taken", "warning")
                return render_template("addArtistUser.html")

            query = Artistuser(Acode=Acode, email=email, password=password)
            db.session.add(query)
            db.session.commit()
            
            flash("Data Inserted Successfully", "success")
            return redirect('/addArtistUser')
        
    else:
        flash("Login and try Again", "warning")
        return redirect('/login')
    return render_template("addArtistUser.html")







# testing whether db is connected or not


with app.app_context():
    db.create_all()


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



@app.route("/addartistinfo", methods=['POST', 'GET'])
@login_required
def addartistinfo():
    email = current_user.email
    posts = Artistuser.query.filter_by(email=email).first()
    code = posts.Acode if posts else None
    postsdata = Artistdata.query.filter_by(Acode=code).first() if code else None
    
    if request.method == "POST":
        Acode = request.form.get('Acode')
        Aname = request.form.get('Aname')
        Genre = request.form.get('Genre')
        Records = request.form.get('Records')
        Label = request.form.get('Label')
        Acode = Acode.upper()

        auser = Artistuser.query.filter_by(Acode=Acode).first()
        aduser = Artistdata.query.filter_by(Acode=Acode).first()
        if aduser:
            flash("Data is already Present you can update it", "primary")
            return render_template("artistdata.html", postsdata=postsdata)
        if auser:
            query = Artistdata(Acode=Acode, Aname=Aname, Genre=Genre, Records=Records, Label=Label)
            db.session.add(query)
            db.session.commit()
            flash("Data is Added", "primary")
            return redirect('/addartistinfo')
        else:
            flash("Artist Code does not exist", "warning")
            return redirect('/addartistinfo')

    return render_template("artistdata.html", postsdata=postsdata)
  # Ensure postsdata is passed
  
    

 
@app.route("/aedit/<string:id>", methods=['POST', 'GET'])
@login_required
def aedit(id):
    post = Artistdata.query.filter_by(id=id).first()
    if not post:
        flash("Record not found", "danger")
        return redirect('/addartistinfo')

    if request.method == "POST":
        Acode = request.form.get('Acode')
        Aname = request.form.get('Aname')
        Genre = request.form.get('Genre')
        Records = request.form.get('Records')
        Label = request.form.get('Label')
        Acode = Acode.upper()
        
        post.Acode = Acode
        post.Aname = Aname
        post.Genre = Genre
        post.Records = Records
        post.Label = Label
        db.session.commit()
        flash("Slot Updated", "success")
        return redirect('/addartistinfo')

    return render_template("aedit.html", posts=post)



@app.route("/adelete/<string:id>", methods=['POST', 'GET'])
@login_required
def adelete(id):
    post = Artistdata.query.filter_by(id=id).first()
    if not post:
        flash("Record not found", "danger")
        return redirect('/addartistinfo')
    
    db.session.delete(post)
    db.session.commit()
    flash("Data Deleted", "success")
    return redirect('/addartistinfo')



# playlist_CRUD


@app.route('/makeplaylist', methods=['POST', 'GET'])
@login_required
def makeplaylist():
    if request.method == 'POST':
        playlist_title = request.form['title']
        playlist_artist = request.form['artist']
        playlist_album = request.form['album']
        new_playlist = Playlist(title=playlist_title, artist=playlist_artist, album=playlist_album, user_id=current_user.id)  # Assign current user's ID

        try:
            db.session.add(new_playlist)
            db.session.commit()
            return redirect('/makeplaylist')  # Update the redirect path
        except:
            return 'There was an issue adding your track to the playlist'
    else:
        # Filter playlists by the current user's ID
        playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.date_added).all()
        return render_template('pindex.html', playlists=playlists)




@app.route('/pupdate/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    playlist = Playlist.query.get_or_404(id)
    
    # Check if the playlist belongs to the current user
    if playlist.user_id != current_user.id:
        flash("You do not have permission to edit this playlist", "danger")
        return redirect('/makeplaylist')

    if request.method == 'POST':
        playlist.title = request.form['title']
        playlist.artist = request.form['artist']
        playlist.album = request.form['album']

        try:
            db.session.commit()
            return redirect('/makeplaylist')  
        except:
            return 'There was an issue updating your track in the playlist'

    else:
        return render_template('pupdate.html', playlist=playlist)





@app.route('/pdelete/<int:id>')
@login_required
def delete(id):
    playlist_to_delete = Playlist.query.get_or_404(id)

    try:
        db.session.delete(playlist_to_delete)
        db.session.commit()
        return redirect('/makeplaylist')  
    except:
        return 'There was a problem deleting that track from the playlist'


@app.route('/plist', methods=['GET'])
@login_required
def plist():
    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.date_added).all()
    return render_template('plist.html', playlists=playlists)





# take help from the playlist 


# Book concert route
@app.route('/bookconcert', methods=['POST', 'GET'])
@login_required
def bookconcert():
    if request.method == 'POST':
        concert_name = request.form['name']
        concert_artist = request.form['artist']
        concert_location = request.form['location']
        new_concert_booking = Concert(name=concert_name, artist=concert_artist, location=concert_location, user_id=current_user.id)  # Assign current user's ID

        try:
            db.session.add(new_concert_booking)
            db.session.commit()
            return redirect('/bookconcert')  # Update the redirect path
        except:
            return 'There was an issue booking your concert slot'
    else:
        # Filter concerts by the current user's ID
        concerts = Concert.query.filter_by(user_id=current_user.id).order_by(Concert.date_added).all()
        return render_template('cindex.html', concerts=concerts)



# Update concert route
@app.route('/cupdate/<int:id>', methods=['GET', 'POST'])
@login_required
def cupdate(id):
    concert = Concert.query.get_or_404(id)
    
    # Check if the concert belongs to the current user
    if concert.user_id != current_user.id:
        flash("You do not have permission to edit this concert booking", "danger")
        return redirect('/bookconcert')

    if request.method == 'POST':
        concert.name = request.form['name']
        concert.artist = request.form['artist']
        concert.location = request.form['location']

        try:
            db.session.commit()
            return redirect('/bookconcert')
        except:
            return 'There was an issue updating your concert booking'
    else:
        return render_template('cupdate.html', concert=concert)

# Delete concert route
@app.route('/cdelete/<int:id>')
@login_required
def cdelete(id):
    concert_to_delete = Concert.query.get_or_404(id)

    try:
        db.session.delete(concert_to_delete)
        db.session.commit()
        return redirect('/bookconcert')
    except:
        return 'There was a problem deleting the booking slot for the concert'


@app.route('/clist', methods=['GET'])
@login_required
def clist():
    concerts = Concert.query.filter_by(user_id=current_user.id).order_by(Concert.date_added).all()
    
    return render_template('clist.html', concerts=concerts)





if local_server:
    app.run(debug=True)
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from functools import wraps
import os
from werkzeug import secure_filename
from flask_mail import Mail, Message

POSTS_PER_PAGE = 6
POSTS_PER_PAGE_ADMIN = 4


app = Flask(__name__)
bcrypt = Bcrypt(app)
# DEBUG in testing. Change to False before deploy.
DEBUG = True
app.secret_key = "IT'S A SECRET"

#MySQL database config
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:password@localhost:3306/cooking'

db = SQLAlchemy(app)

import models
from models import *


# mail setting
mail = Mail()
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'superyaooo@gmail.com'
app.config["MAIL_PASSWORD"] = 'secret password'

mail.init_app(app)


app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif','PNG','JPG','JPEG','GIF'])



#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

    

@app.route('/', methods=['GET','POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    query = models.Recipe.query.order_by(Recipe.id.desc())
    recipes = query.paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', recipes=recipes)


@app.route('/recipe/<int:id>', methods=['GET','POST'])
def recipe(id):
    recipe = db.session.query(Recipe).get(id)
    return render_template('recipe.html', recipe=recipe)



@app.route('/about', methods=['GET','POST'])
def about():
    error = None
    if request.method == 'POST':
        msg = Message('New message from Easy Chinese Kitchen', sender='superyaooo@gmail.com', recipients=['superyaooo@gmail.com'])
        msg.body = """
        From: %s <%s>
        %s
        """ % (request.form['name'], request.form['email'], request.form['message'])
        
        if not request.form['name']:
            error = 'Your name cannot be empty in the contact form. Please try again.'
        elif not request.form['message']:
            error = 'Message area cannot be empty in the contact form. Please try again.'
        elif not request.form['email']:
            error = 'Your email cannot be empty in the contact form. Please try again.'
        else:
            mail.send(msg)
            flash('Thank you for your message. I\'ll get back to you soon.')
            return redirect(url_for('about'))
        
    return render_template('about.html', error=error)

    
#hash username and password during login
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    
    if request.method=='POST':
        pw_hash = bcrypt.generate_password_hash('admin', 10)
        usn_hash = bcrypt.generate_password_hash('admin', 10)
        
        if not bcrypt.check_password_hash(usn_hash, request.form['username']):
            error = 'Invalid username. Please try again.'
        elif not bcrypt.check_password_hash(pw_hash, request.form['password']):
            error = 'Invalid password. Please try again.'
        else:
            session['logged_in'] = True
            flash('You are logged in.')
            return redirect(url_for('admin'))

    return render_template('admin/login.html', error=error)
    

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You are logged out.')
    return redirect(url_for('login'))


# allowed file upload format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
    

@app.route('/admin', methods=['GET','POST'])
@app.route('/admin/<int:page>', methods=['GET', 'POST'])
@login_required
def admin(page=1):

    error = None
    
    if request.method =='POST':

        file=request.files['file']

        if file and not allowed_file(file.filename):
            error = 'Only pictures are allowed to be uploaded!'
            
        elif not file:
            error = 'Must upload a picture!'
            
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.static_folder,'img/upload_img',filename))
            
            new_recipe=Recipe(
                request.form['title'],
                '/static/img/upload_img/'+ filename,
                request.form['description'],
                request.form['content']
            )
            db.session.add(new_recipe)
            db.session.commit()
            flash('New entry was successfully posted.')
            return redirect(url_for('admin'))

    query = models.Recipe.query.order_by(Recipe.id.desc())
    recipes = query.paginate(page, POSTS_PER_PAGE_ADMIN, False)
    return render_template('admin/admin.html',recipes=recipes,error=error)


@app.route('/delete/<int:id>', methods=['POST','GET'])
@login_required
def delete(id):
    recipe = db.session.query(Recipe).get(id)
    db.session.delete(recipe)
    db.session.commit()
    flash('Entry was successfully deleted.')
    return redirect(url_for('admin'))


@app.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    recipe = db.session.query(Recipe).get(id)
    error = None
    
    if request.method=='POST':   
         
        recipe.title = request.form['title']
        recipe.pub_date = request.form['pub_date']
        recipe.description = request.form['description']
        recipe.content = request.form['content']

        
        file=request.files['file']

        # If choose to upload a new file, then set recipe.img_url to new file. 
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.static_folder, 'img/upload_img',filename))
            
            recipe.img_url= '/static/img/upload_img/'+ filename

            db.session.add(recipe)
            db.session.commit()
                    
            flash('Your changes have been saved.')
            return redirect(url_for('admin'))     

        elif not file:
            db.session.add(recipe)
            db.session.commit()
                    
            flash('Your changes have been saved.')
            return redirect(url_for('admin'))     

        else:
            error = 'Only pictures are allowed to be uploaded!'
            
    return render_template('admin/edit.html', recipe=recipe, error=error)



# show images in static/img/upload_img folder
@app.route('/show_imgs',methods=['POST','GET'])
@login_required
def show_imgs():    
    imgs = os.listdir(os.path.join(app.static_folder,'img/upload_img'))
    
    return render_template('admin/show_imgs.html', imgs=imgs)
    
# delete images in static/img/upload_img folder
@app.route('/remove_img/<img>',methods=['POST','GET'])
@login_required
def remove_img(img):
    os.remove(os.path.join(app.static_folder,'img/upload_img', img))
 
    flash('Image has been removed.')
    return redirect(url_for('show_imgs'))




# need work on ---------------------------------
@app.route('/search', methods=['GET','POST'])
def search():
    return render_template('search.html')

#-----------------------------------------------











if __name__ == '__main__':
    app.run()


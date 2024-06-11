#app.py

from flask import Flask, render_template ,request,flash,Response,url_for,session,redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_admin import Admin, AdminIndexView,BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import Account

import re
from werkzeug.utils import secure_filename
import wget
import cv2
import os
import calendar
import time
import getpass
import platform
from compression import compression
from effects import remove_background, photo_to_sketch ,photo_to_cartoon,photo_to_oil_painting,photo_to_sepia,unblur_to_blur,photo_to_pixel,photo_to_vintage,photo_to_warhol,photo_to_hdr_effect,line_art,crayon_drawing,download
from edit import brightness,contrast,blur,resize,denoise,rotate,sharp,downloads
from filter import nepal,phool,junga,micky,tika,thug,thug2,sunglass,mask,rcb,mi,gunda

app = Flask(__name__)
app.config['SECRET_KEY']='ezEdit'


#MYSQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'auth_system'

UPLOAD_FOLDER = 'static/images/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Initialize MySQL
mysql = MySQL(app)

# Custom view for Account model
class AccountView(BaseView):
    @expose('/')
    def index(self):
        accounts = Account.get_all(mysql)
        return self.render('admin/account_list.html', accounts=accounts)

    @expose('/new/', methods=['GET', 'POST'])
    def create(self):
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            account = Account(username=username, email=email, password=password)
            account.save(mysql)
            return redirect(url_for('.index'))
        return self.render('admin/account_form.html')

    @expose('/edit/<int:id>/', methods=['GET', 'POST'])
    def edit(self, id):
        account = Account.get_by_id(mysql, id)
        if request.method == 'POST':
            account.username = request.form['username']
            account.email = request.form['email']
            account.password = request.form['password']
            account.update(mysql)
            return redirect(url_for('.index'))
        return self.render('admin/account_form.html', account=account)

    @expose('/delete/<int:id>/', methods=['POST'])
    def delete(self, id):
        account = Account.get_by_id(mysql, id)
        account.delete(mysql)
        return redirect(url_for('.index'))
    
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/admin.html')

    @expose('/logout/')
    def logout(self):
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    
    

# Initialize Flask-Admin
admin = Admin(app, name='Admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(AccountView(name='Accounts'))


@app.route('/admin/')
def admin_home():
    return redirect(url_for('admin.index'))




@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            # Check if the user is an admin and their ID is 6
            if username == 'admin' and password == 'admin' and account['id'] == 6:
                return redirect(url_for('admin_home'))  # Redirect to admin home page
            else:
                return redirect(url_for('home'))   # Redirect to regular user page
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)




@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)





@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

###################################################################################################home page
@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')


#################################################################################about page

@app.route('/about')
def about():
	return render_template('about.html')













#Edit route
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    if request.method == 'POST':
        if 'button' in request.form:
            if request.form['button'] == 'Upload':
                if request.form['path'] != '' and request.files['local_file'].filename == '':
                    path = request.form['path']
                    a = path.split('/')
                    previous = os.getcwd()
                    edit_img = os.path.join(previous, 'static/images/uploads', a[-1])
                    if os.path.isfile(edit_img):
                        session['uploaded_image'] = edit_img
                        # Initialize all values in the session
                        session['brightness_value'] = '0'
                        session['contrast_value'] = '1'
                        session['sharp_value'] = 'none'
                        session['resize_value'] = 'none'
                        session['rotate_value'] = 'none'
                        session['denoise_value'] = 'none'
                        session['blur_value'] = '0'
                        return render_template('edit.html', image_filename='../static/images/uploads/' + a[-1], brightness_value='0', contrast_value='1', sharp_value='none', resize_value='none', rotate_value='none', denoise_value='none', blur_value='0')
                    folder = os.path.join(previous, 'static/images/uploads')
                    os.chdir(folder)
                    image_filename = wget.download(path)
                    os.chdir(previous)
                    session['uploaded_image'] = os.path.join(folder, image_filename)
                    # Initialize all values in the session
                    session['brightness_value'] = '0'
                    session['contrast_value'] = '1'
                    session['sharp_value'] = 'none'
                    session['resize_value'] = 'none'
                    session['rotate_value'] = 'none'
                    session['denoise_value'] = 'none'
                    session['blur_value'] = '0'
                    return render_template('edit.html', image_filename='../static/images/uploads/' + image_filename, brightness_value='0', contrast_value='1', sharp_value='none', resize_value='none', rotate_value='none', denoise_value='none', blur_value='0')

                elif request.form['path'] == '' and request.files['local_file'].filename != '':
                    f = request.files['local_file']
                    previous = os.getcwd()
                    edit_img = os.path.join(previous, 'static/images/uploads', f.filename)
                    folder = os.path.join(previous, 'static', 'images', 'uploads')
                    os.chdir(folder)
                    f.save(secure_filename(f.filename))
                    os.chdir(previous)
                    session['uploaded_image'] = edit_img
                    # Initialize all values in the session
                    session['brightness_value'] = '0'
                    session['contrast_value'] = '1'
                    session['sharp_value'] = 'none'
                    session['resize_value'] = 'none'
                    session['rotate_value'] = 'none'
                    session['denoise_value'] = 'none'
                    session['blur_value'] = '0'
                    return render_template('edit.html', image_filename='../static/images/uploads/' + f.filename, brightness_value='0', contrast_value='1', sharp_value='none', resize_value='none', rotate_value='none', denoise_value='none', blur_value='0')

            elif request.form['button'] == 'Apply' and 'uploaded_image' in session:
                edit_img = session['uploaded_image']
                brightness_value = request.form['brightness']
                contrast_value = request.form['Contrast']
                sharp_value = request.form['type']
                resize_value = request.form['type2']
                rotate_value = request.form['type1']
                denoise_value = request.form['type3']
                blur_value = request.form['Blur']
                # Store all values in the session
                session['brightness_value'] = brightness_value
                session['contrast_value'] = contrast_value
                session['sharp_value'] = sharp_value
                session['resize_value'] = resize_value
                session['rotate_value'] = rotate_value
                session['denoise_value'] = denoise_value
                session['blur_value'] = blur_value
                previous = os.getcwd()
                folder = os.path.join(previous, 'static/images/uploads')
                edited_image_path = ''  # Initialize edited image path

                if edit_img.endswith(('jpeg', 'jpg')):
                    edited = os.path.join(folder, 'edited.jpg')
                    edited_image_path = 'edited.jpg'
                elif edit_img.endswith('png'):
                    edited = os.path.join(folder, 'edited.png')
                    edited_image_path = 'edited.png'

                os.chdir(folder)
                if brightness_value:
                    brightness(edit_img, int(brightness_value))
                if contrast_value:
                    contrast(edited, float(contrast_value))
                if sharp_value != 'none':
                    sharp(edited, sharp_value)
                if resize_value != 'none':
                    resize(edited, resize_value)
                if rotate_value != 'none':
                    rotate(edited, rotate_value)
                if denoise_value != 'none':
                    denoise(edited, denoise_value)
                if blur_value and blur_value != '0':
                    blur(edited, int(blur_value))
                os.chdir(previous)

                if edited_image_path:
                    session['edited_image'] = edited
                    session['edited_image_path'] = edited_image_path  # Store edited image path in session
                    return render_template('edit.html', image_filename='../static/images/uploads/' + edited_image_path, brightness_value=brightness_value, contrast_value=contrast_value, sharp_value=sharp_value, resize_value=resize_value, rotate_value=rotate_value, denoise_value=denoise_value, blur_value=blur_value)
                else:
                    flash("Oops Something went wrong!")
                    return render_template('edit.html', brightness_value=brightness_value, contrast_value=contrast_value, sharp_value=sharp_value, resize_value=resize_value, rotate_value=rotate_value, denoise_value=denoise_value, blur_value=blur_value)

            elif request.form['button'] == 'Download' and 'edited_image' in session:
                downloads(session['edited_image'])
                session.pop('uploaded_image', None)
                session.pop('edited_image', None)
                flash("Successfully Downloaded! Image available in Downloads")
                return render_template('edit.html', brightness_value='0', contrast_value='1', blur_value='0', sharp_value='none', denoise_value='none', rotate_value='none', resize_value='none')

    uploaded_image = session.get('uploaded_image')
    brightness_value = session.get('brightness_value', '0')
    contrast_value = session.get('contrast_value', '1')
    sharp_value = session.get('sharp_value', 'none')
    resize_value = session.get('resize_value', 'none')
    rotate_value = session.get('rotate_value', 'none')
    denoise_value = session.get('denoise_value', 'none')
    blur_value = session.get('blur_value', '0')

    return render_template('edit.html', image_filename='../static/images/uploads/' + os.path.basename(uploaded_image) if uploaded_image else '', brightness_value=brightness_value, contrast_value=contrast_value, blur_value=blur_value, sharp_value=sharp_value, denoise_value=denoise_value, rotate_value=rotate_value, resize_value=resize_value)



##############compression route
com_img = ''

@app.route('/compression', methods=['GET', 'POST'])
def compress():
    global com_img
    if 'username' not in session:
        return redirect(url_for('login')) 
    
    if request.method == 'POST':
        if request.form['button'] == 'Upload' and request.form['path'] != '' and request.files['local_file'].filename == '':
            path = request.form['path']
            a = path.split('/')
            previous = os.getcwd()
            com_img = session.get('edited_image_path', '')  # Retrieve edited image path from session
            if com_img:
                return render_template('compression.html', image_filename='../static/images/uploads/' + com_img)
            else:
                flash("No image found!")
                return render_template('compression.html')

        elif request.form['button'] == 'Upload' and request.form['path'] == '' and request.files['local_file'].filename != '':
            typ = request.form['type']
            f = request.files['local_file']
            previous = os.getcwd()
            com_img = os.path.join(previous, 'static/images/uploads', f.filename)
            folder = os.path.join(previous, 'static/images/uploads')
            os.chdir(folder)
            f.save(secure_filename(f.filename))
            os.chdir(previous)
            return render_template('compression.html', image_filename='../static/images/uploads/' + f.filename)

        elif request.form['button'] == 'Compress' and com_img != '':
            typ = request.form['type']
            compression(com_img, typ)
            com_img = ''
            flash("Successfully compressed! Compressed Image available in Downloads.")
            return render_template('compression.html')

        else:
            com_img = ''
            flash("Oops Something went wrong !")
            return render_template('compression.html')

    # Check if there is an edited image in the session when GET request
    com_img = session.get('edited_image_path', '')
    if com_img:
        return render_template('compression.html', image_filename='../static/images/uploads/' + com_img)

    return render_template('compression.html')




#################################################################################################effects page
eff_img=''
effected=''
@app.route('/effects',methods=['GET','POST'])
def effects():
    if 'username' not in session:
        return redirect(url_for('login'))  

    if request.method=='POST':
       print("Entered Post")
       global eff_img
       global effected
       if request.form['button']=='Upload' and request.form['path']!='' and  request.files['local_file'].filename=='':
           path = request.form['path']
           a = path.split('/')
           previous = os.getcwd()
           eff_img=previous+'/static/images/trash/'+a[len(a)-1]
           if os.path.isfile(previous+'/static/images/trash/'+a[len(a)-1]):
              return render_template('effects.html',image_filename='../static/images/trash/'+a[len(a)-1])
           folder = previous +'/static/images/trash/'
           os.chdir(folder)
           image_filename = wget.download(path)
           os.chdir(previous)
           return render_template('effects.html',image_filename='../static/images/trash/'+image_filename)

       elif request.form['button']=='Upload' and request.form['path']=='' and  request.files['local_file'].filename!='':
            f = request.files['local_file']
            previous = os.getcwd()
            eff_img=previous+'/static/images/trash/'+f.filename
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            f.save(secure_filename(f.filename))
            os.chdir(previous)
            return render_template('effects.html',image_filename='../static/images/trash/'+f.filename)

       elif request.form['button']=='Download' and effected!='':
            download(effected)
            effected=""
            eff_img=""
            flash("Successfully Downloaded! Image available in Downloads")
            return render_template('effects.html')
                        
       elif request.form['button'] == 'CUT BG' and eff_img != '':
            previous = os.getcwd()
            folder = previous + '/static/images/trash/'
            os.chdir(folder)
            remove_background(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg') > 0 or eff_img.count("jpg") > 0:
                effected = folder + 'intermediate.jpg'
                return render_template('effects.html', image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png') > 0:
                effected = folder + 'intermediate.png'
                return render_template('effects.html', image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')
       
       elif request.form['button']=='Sketch' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_sketch(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            else:
                return render_template('effects.html')

       elif request.form['button']=='Cartoon' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_cartoon(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')
  
       elif request.form['button']=='Oil Paint' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_oil_painting(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')

       elif request.form['button']=='Muddy' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_sepia(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')

       elif request.form['button']=='Blur' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            unblur_to_blur(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')
      
       elif request.form['button']=='Pixel Art' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_pixel(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')   
     
       elif request.form['button']=='Vintage' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_vintage(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html') 

       elif request.form['button']=='Invert' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_warhol(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')
   
       elif request.form['button']=='HDR' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            photo_to_hdr_effect(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')

       elif request.form['button']=='Line Art' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            line_art(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')
        
       
       elif request.form['button']=='Drawing' and eff_img!='':
            previous = os.getcwd()
            folder = previous +'/static/images/trash/'
            os.chdir(folder)
            crayon_drawing(eff_img)
            os.chdir(previous)
            if eff_img.count('jpeg')>0 or eff_img.count("jpg")>0:
                effected=folder+'intermediate.jpg'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.jpg')
            elif eff_img.count('png')>0:
                effected=folder+'intermediate.png'
                return render_template('effects.html',image_filename='../static/images/trash/intermediate.png')
            else:
                return render_template('effects.html')

       else:
           eff_img=''
           effected=''
           flash("Oops Something went wrong !")
           return render_template('effects.html')

    return render_template('effects.html')

############################################################################################filters page
cap = ''
value = 0
filter_img = ''
flag = False

def stream():
    global cap
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame")
            break

        _, imgencode = cv2.imencode('.jpg', frame)
        strinData = imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + strinData + b'\r\n')

def stop():
    global cap
    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()

@app.route('/filters/video')
def video():
    global value
    if 'username' not in session:
        return redirect(url_for('login'))

    if value == 0:
        return Response(stream(), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 1:
        return Response(nepal(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 2:
        return Response(junga(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 3:
        return Response(phool(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 4:
        return Response(micky(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 5:
        return Response(tika(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 6:
        return Response(thug(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 7:
        return Response(thug2(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 8:
        return Response(sunglass(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 9:
        return Response(mask(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 10:
        return Response(mi(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 11:
        return Response(rcb(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 12:
        return Response(gunda(cap), mimetype='multipart/x-mixed-replace;boundary=frame')
    elif value == 13:
        stop()
        return Response("Camera stopped", mimetype='text/plain')

@app.route('/filters', methods=['GET', 'POST'])
def filters():
    global value
    global filter_img
    global flag

    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    if request.method == 'POST':
        if request.form['button'] == 'Nepal':
            value = 1
        elif request.form['button'] == 'Junga':
            value = 2
        elif request.form['button'] == 'Phool':
            value = 3
        elif request.form['button'] == 'Micky':
            value = 4
        elif request.form['button'] == 'Tika':
            value = 5
        elif request.form['button'] == 'Thug':
            value = 6
        elif request.form['button'] == 'Thug2':
            value = 7
        elif request.form['button'] == 'Sunglass':
            value = 8
        elif request.form['button'] == 'Mask':
            value = 9
        elif request.form['button'] == 'MI':
            value = 10
        elif request.form['button'] == 'RCB':
            value = 11
        elif request.form['button'] == 'Gunda':
            value = 12
        elif request.form['button'] == 'Clear':
            value = 0
        elif request.form['button'] == 'Capture':
            value = 13
            flag = True
            filter_img = '../static/images/trash/filter.jpg'
            return render_template('filters.html', img_filename='../static/images/trash/filter.jpg')
        elif request.form['button'] == 'Download' and flag:
            value = 0
            flag = False
            gmt = time.gmtime()
            ts = calendar.timegm(gmt)
            ts = str(ts)
            username = getpass.getuser()
            folder = ''
            if platform.system() == 'Linux':
                folder += '/home/' + username + '/Downloads/'
            else:
                folder += 'C:\\Downloads'
            previous = os.getcwd()
            image = cv2.imread(previous + '/static/images/trash/filter.jpg')
            os.chdir(folder)
            outpath = "ezEdit_Filter_" + ts + ".jpg"
            cv2.imwrite(outpath, image)
            os.chdir(previous)
            flash("Image downloaded successfully!")
            return render_template('filters.html', message=True)
        else:
            value = 0
    return render_template('filters.html', img_filename=None)


###############################################################################################main function
if __name__ == '__main__':
	app.run(debug=True,port=5000)

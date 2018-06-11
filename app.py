from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, Response
import subprocess
#from data import Articles
#from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha512_crypt
from functools import wraps

app = Flask(__name__)


# Config MySQL
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = '123456'
#app.config['MYSQL_DB'] = 'myflaskapp'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
#mysql = MySQL(app)

#Articles = Articles()

# Index
@app.route('/')
def index():
    return render_template('home.html')


# sobre
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
#        username = request.form['username']
        password_candidate = request.form['password']


        passfile=open('password','rb')
        if sha512_crypt.verify(password_candidate,passfile.read()):
                # Passed
            session['logged_in'] = True
            passfile.close()
            flash('Login realizado com sucesso', 'success')
            return redirect(url_for('index'))
        else:
            error = 'Senha inválida'
            return render_template('login.html', error=error)
            # Close connection
#            cur.close()
#        else:
#            error = 'Username not found'
#            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Acesso não autorizado. Por favor, fazer login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logout feito com sucesso', 'success')
    return redirect(url_for('login'))


class ChangePassword(Form):
    password = PasswordField('Nova senha', [validators.InputRequired(message='Este campo é obrigatório'), validators.EqualTo('confirm', message='As senhas não batem'),validators.Length(min=5, max=50, message='A senha deve ter de 5 a 50 caracteres')])
    confirm  = PasswordField('Repetir senha')


# change password
@app.route('/changepass', methods=['GET', 'POST'])
@is_logged_in
def changepass():
    form = ChangePassword(request.form)
    if request.method == 'POST' and form.validate():
        passfile = open('password', 'wb')
        passfile.write(sha512_crypt.encrypt(str(form.password.data)).encode())
        flash('Senha trocada com sucesso', 'success')
        passfile.close()

        return redirect(url_for('index'))
#    return render_template('changepass.html')
    return render_template('changepass.html', form=form)



def webcam_video_stream():
    command = ("gst-launch-1.0 -v v4l2src device=/dev/video0 !"
               "'video/x-raw,width=320,height=240,framerate=30/1'"
               " ! jpegenc ! multipartmux boundary=spionisto ! "
               "filesink location=/dev/stdout")
#    command = ("gst-launch-1.0 -v videotestsrc !"
#               "'video/x-raw,width=320,height=240,framerate=30/1'"
#               " ! jpegenc ! multipartmux boundary=spionisto ! "
#               "filesink location=/dev/stdout")
    p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1, shell=True)
    print("starting polling loop.")
    while(p.poll() is None):
        yield p.stdout.read(1024)


@app.route('/videofeed')
@is_logged_in
def videofeed():
    return Response(webcam_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=--spionisto')

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)

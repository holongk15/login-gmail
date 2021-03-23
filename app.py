from flask import Flask, request, url_for, render_template,redirect,url_for
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector

app = Flask(__name__, template_folder='templates')
app.config.from_pyfile('config.cfg')
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
app.config['USE_SESSION_FOR_NEXT'] = True


global COOKIE_TIME_OUT
COOKIE_TIME_OUT = 60*5 

mail = Mail(app)

mysql = MySQL(app)



s = URLSafeTimedSerializer('thisisascrect!')

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return '<form action="/" method="POST"> <input name = "email" type="email"> <input type="submit"></form>'
    email = request.form['email']
    token = s.dumps(email, salt ='email-confirm')
    msg = Message('Confirm email', sender="holongk15@gmail.com", recipients=[email])
    link = url_for('confirm_email', token = token, _external = True)
    msg.body = 'your link is {}'.format(link)
    mail.send(msg)
    return '<h1>The email you entered is {}. The token is {}</h1>'.format(email, token)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=36000)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (username) VALUES (%s)", (email,))
        mysql.connection.commit()
        return redirect(url_for('change_pass', email = email))
    except SignatureExpired:
        return '<h1> The token is expired </h1>' 

@app.route('/change_pass', methods=['GET','POST'])
def change_pass():
    email = request.args.get('email', None)
    if request.method == 'POST':
        id = request.form.get('id')
        # email = request.form['email']
        password = request.form['password']
        data = request.data
        # dataDict = json.loads(data)
        request.get_data(as_text=True)
        cur = mysql.connection.cursor()
        cur.execute('UPDATE user SET password=%s WHERE username=%s ', (password,email))
        # mycursor.execute(mysql)
        mysql.connection.commit()
      
        return "Thành Công"
    return render_template('changepass.html', email=email)
if __name__ == '__main__':
    app.run(debug = True)

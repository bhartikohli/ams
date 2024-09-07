from flask import Flask, render_template,request,session,redirect, url_for,flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

local_server=True
app = Flask(__name__)
app.secret_key='asdf'


#connection with database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'fqyAhD@1'
app.config['MYSQL_DB'] = 'db'

mysql = MySQL(app)
login_manager = LoginManager(app)


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    user = User()
    user.id = user_id
    user.username = cur.fetchone()[1]
    cur.close()
    return user


#***********************************HOME PAGE *************************************

@app.route('/')
def home():
    return render_template('index.html')




#***********************************ADMIN*************************************************
@app.route('/a_login',methods=["POST","GET"])
def a_login():
    if request.method == "POST":
        #username = request.form['username']
        password = request.form['password']


        if password=="1962":
            flash(" Welcome","success")
            return render_template('data.html')

        else:
            # Invalid login credentials, show error message
            flash("Invalid Password","danger")
            return render_template('a_login.html')

    return render_template('a_login.html')



#***************************************database************************************
@app.route('/b',methods=["POST","GET"])
def b():  
    cur = mysql.connection.cursor()
    cur.execute("select * from book")        
    query=cur.fetchall()     
    return render_template('b.html',query=query)
    

@app.route('/d',methods=["POST","GET"])
def d():
    cur = mysql.connection.cursor()
    cur.execute("select * from doctor")        
    query=cur.fetchall()     
    return render_template('d.html',query=query)
    


@app.route('/u',methods=["POST","GET"])
def u():
    cur = mysql.connection.cursor()
    cur.execute("select * from user")        
    query=cur.fetchall()     
    return render_template('u.html',query=query)

@app.route('/a',methods=["POST","GET"])
def a():
    return render_template('data.html')

#*************************************  SIGNUP  ******************************************************


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        encpassword = generate_password_hash(password)
        

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cur.fetchone()

        if user:
            # User exists and password is correct, log them in and redirect to home page
            flash("E-mail already exist. Please Login","danger")
            return render_template('login.html')
        
        else:
            cur.execute("INSERT INTO user(username, email, password) VALUES (%s, %s, %s)", (username, email, encpassword))
            mysql.connection.commit()                                   #to save changes done to databaes
            cur.close()
            flash("SignUp Successful. Please Login","success")
            return render_template('login.html')
    return render_template('signup.html')



#*********************************************  LOGIN  *********************************************

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        #username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        encpassword = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cur.fetchone()

        if user and check_password_hash(user[2], password):
            # User exists and password is correct, log them in and redirect to home page
            session['user_id'] = user[0]
            session['user_email']=user[1]
            flash("Login Successful. Welcome","success")
            return render_template('patients.html')

        else:
            # Invalid login credentials, show error message
            flash("Invalid Credentials. Please login","danger")
            return render_template('signup.html')
        
            
    return render_template('login.html')



#******************************************* BOOKING PAGE ********************************

@app.route('/patients',methods=['POST','GET'])
def patients():
    if 'user_id' in session:
        if request.method=="POST":
            email=session['user_email']
            name=request.form['name']
            gender=request.form['gender']
            slot=request.form['slot']
            disease=request.form['disease']
            dept=request.form['dept']
            phone=request.form['phone']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO book(email, name, gender, slot, disease, dept, phone) VALUES (%s, %s, %s, %s, %s, %s, %s)", (email, name, gender, slot, disease, dept, int(phone),))        
            mysql.connection.commit()                                   #to save changes done to databases
            cur.close()       
            flash("Booking confirmed","info")


        return render_template('patients.html')
    else:
        flash("Please Login first","danger")
        return render_template('login.html')


#******************************************** BOOKING DETAILS PAGE **********************

@app.route('/bookings')
def bookings():
    if 'user_id' in session:
        email=session['user_email']
        cur = mysql.connection.cursor()
        cur.execute("select * from book where email=%s",(email,))        
        query=cur.fetchall()     
        return render_template('bookings.html',query=query)
    
    else:
        flash("Please Login first","danger")
        return render_template('login.html')



#******************************************** EDIT BOOKING ****************************
@app.route("/edit/<int:bid>",methods=['POST','GET'])
def edit(bid):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM book WHERE bid = %s', (bid,))
    user = cur.fetchone()

    if request.method=="POST":
            name=request.form['name']
            gender=request.form['gender']
            slot=request.form['slot']
            disease=request.form['disease']
            dept=request.form['dept']
            phone=request.form['phone']

            cur = mysql.connection.cursor()
            cur.execute("UPDATE book SET name=%s, gender=%s, slot=%s, disease=%s, dept=%s, phone=%s WHERE bid=%s", (name, gender, slot, disease, dept, int(phone), bid))        
            mysql.connection.commit()  # to save changes done to the database    
            flash("Booking updated","info")
    return render_template('edit.html',user=user)



#*********************************** DELETE BOOKING  *****************

@app.route("/delete/<int:bid>",methods=['POST','GET'])
def delete(bid):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM book WHERE bid = %s', (bid,))
    mysql.connection.commit()                                   #to save changes done to databases
    flash("Booking deleted","danger")
    return render_template('bookings.html')



#************************************** DOCTORS LOGIN PAGE ****************

@app.route('/doctors',methods=["POST","GET"])
def d_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM doctor WHERE email = %s', (email,))
        user = cur.fetchone()

        if user and (user[2]==password): #and check_password_hash(user[2], password):
            # User exists and password is correct, log them in and redirect to home page
            session['user_id'] = user[0]
            session['user_email']=user[1]
            flash("Login Successful. Welcome","success")
            return render_template('d_index.html')
    

        else:
            # Invalid login credentials, show error message
            flash("Invalid Credentials. Please login","danger")
            
    return render_template('doctors.html')



#********************************************DOCTOR'S BOOKING PAGE **********************

@app.route('/d_booking')
def d_booking():
    if 'user_id' in session:
        email=session['user_email']
        cur = mysql.connection.cursor()


        cur.execute('select spc from doctor where email=%s',(email,))  
        esp=cur.fetchone()      

        cur.execute('select * from book where dept=%s',(esp,))        
        query=cur.fetchall()     
        return render_template('d_booking.html',query=query)
    
    else:
        flash("Please Login first","danger")
        return render_template('doctors.html')

#****************************************  LOG OUT ********************

@app.route('/logout')
def logout():
    session.clear()
    flash("Log-out Successful","warning")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
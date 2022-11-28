#Import Flask Library
from datetime import datetime 
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='air_ticket_reservation_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/customerViews/success')
def success():
	username = session['username']
	return render_template('/customerViews/success.html',username=username)

@app.route('/adminViews/successAdmin')
def successAdmin():
	username = session['username']
	return render_template('/adminViews/successAdmin.html',username=username)

@app.route('/customerViews/cancelTripScreen')
def cancelTripScreen():
	username = session['username']
	return render_template('/customerViews/cancelTripScreen.html',username=username)

@app.route('/customerViews/purchaseScreen')
def purchaseScreen():
	username = session['username']
	return render_template('/customerViews/purchaseScreen.html',username=username)

@app.route('/customerViews/rateCommentScreen')
def rateCommentScreen():
	username = session['username']
	return render_template('/customerViews/rateCommentScreen.html',username=username)

@app.route('/default')
def default():
	return render_template('default.html',)

#Define a route to hello function
@app.route('/', methods=['GET','POST'])
def index():
	print("Hello")
	return render_template('index.html')

@app.route('/searchFlight', methods=['GET', 'POST'])
def searchFlight():
	# necessary flight information 
	departure_city = request.form['departCity']
	departure_airport = request.form['departAiport']
	arrival_city = request.form['arriveCity']
	arrival_airport = request.form['arriveAirport']
	depart_date_time = request.form['departDT']
	arrival_date_time = request.form['ReturnDT']

	#cursor used to send queries
	cursor = conn.cursor()

	# execute query for ONEWAY TRIP into cursor
	if arrival_date_time == "":
		query = ('SELECT * FROM flight WHERE '
		'('
			'(departure_airport = %s OR departure_airport IN (SELECT name FROM airport WHERE city = %s)) AND '
			'(arrival_airport = %s OR arrival_airport IN (SELECT name FROM airport WHERE city = %s)) AND '
			'(depart_date_time = %s)'
		')')
		cursor.execute(query, (departure_airport, departure_city, arrival_airport, arrival_city, depart_date_time))
	# execute query for ROUND TRIP into cursor 
	else:
		query = ('SELECT * FROM flight WHERE '
		'('
			'(departure_airport = %s OR departure_airport IN (SELECT name FROM airport WHERE city = %s)) AND '
			'(arrival_airport = %s OR arrival_airport IN (SELECT name FROM airport WHERE city = %s)) AND '
			'(arrive_date_time = %s AND depart_date_time = %s AND arrival_airport = departure_airport)'
		')')
		cursor.execute(query, (departure_airport, departure_city, arrival_airport, arrival_city, arrival_date_time, depart_date_time))

	# catch data
	data = cursor.fetchall()
	error = None 	
	cursor.close()

	# TODO: render template with queried data 
	return render_template('flightdata.html', data= data)

@app.route('/searchFlightStatus', methods=['GET', 'POST'])
def searchFlightStatus():
	# necessary flight information 

	airline_name = request.form['airline']
	flight_number = request.form['flight']
	date = request.form['depArr']

	cursor = conn.cursor()
	query = "SELECT stat FROM flight WHERE airline_name = %s AND flight_num = %s AND ((DATE(depart_date_time) = %s) OR (DATE(arrive_date_time) = %s))"
	cursor.execute(query, (airline_name, flight_number, date, date))

	data = cursor.fetchall()
	error = None 
	cursor.close()

	return render_template('flightdata.html', data= data)


#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/customerViews/customerRegister')
def customerRegister():
	return render_template('/customerViews/customerRegister.html')

#Define route for register
@app.route('/adminViews/adminRegister')
def adminRegister():
	return render_template('/adminViews/adminRegister.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	# query = 'SELECT * FROM user WHERE username = %s and password = %s'
	queryAdmin = 'SELECT * FROM airline_staff WHERE username = %s and passwd = %s'
	cursor.execute(queryAdmin, (username, password))

	#stores the results in a variable
	dataAdmin = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()

	cursor = conn.cursor()

	queryCustomer = 'SELECT * FROM customer WHERE username = %s and pass = %s'
	cursor.execute(queryCustomer, (username, password))

		#stores the results in a variable
	dataCustomer = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()

	error = None
	if(dataAdmin or dataCustomer):
		session['username'] = username
		if dataCustomer:
			#creates a session for the the user
			#session is a built in
			session['admin'] = False
			return redirect(url_for('success'))
			# return redirect(url_for('home'))
		elif dataAdmin:
			session['admin'] = True
			return redirect(url_for('successAdmin'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('index.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms

	username = request.form['username']
	password = request.form['password']
	curr_path = request.url_rule

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('adminRegister.html', error = error)
	else:
		dob = request.form['dob']
		airline_name = request.form['airline_name']
		first_name = request.form['first_name']
		last_name = request.form['last_name']

		ins = 'INSERT INTO airline_staff (date_of_birth,username,airline_name,passwd,first_name,last_name) VALUES(%s,%s,%s,%s,%s,%s)'
		# ins = 'INSERT INTO airline_staff (username,passwd) VALUES(%s, %s)'
		# cursor.execute(ins, (username, airline_name, password, first_name, last_name))
		cursor.execute(ins, (dob, username, airline_name, password, first_name, last_name))
		conn.commit()
		cursor.close()
		return render_template('index.html')
		
#Authenticates the customer register
@app.route('/registerCustomerAuth', methods=['GET', 'POST'])
def registerCustomerAuth():
	#grabs information from the forms

	username = request.form['username']
	password = request.form['password']
	# curr_path = request.url_rule

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('customerRegister.html', error = error)
	else:

		building_num = request.form['building_number']
		city = request.form['city']
		dob = request.form['dob']
		email = request.form['email']
		name = request.form['name']
		password = request.form['password']
		passport_country = request.form['passport_country']
		passport_exp = request.form['passport_expiration']
		passport_num = request.form['passport_number']
		phone = request.form['phone_number']
		state = request.form['state']
		street = request.form['street']																																		
		ins = 'INSERT INTO customer (building_num,city,dob,email,name,pass,passport_country,passport_exp,passport_num,phone_number,state,street,username) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)'
		# ins = 'INSERT INTO airline_staff (username,passwd) VALUES(%s, %s)'
		# cursor.execute(ins, (username, airline_name, password, first_name, last_name))
		cursor.execute(ins, (building_num,city,dob, email, name, password, passport_country, passport_exp, passport_num, phone, state, street, username))
		conn.commit()
		cursor.close()
		return render_template('index.html',erorr=error)

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)

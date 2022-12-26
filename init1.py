#Import Flask Library
from datetime import datetime 
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
from datetime import datetime, timedelta
import hashlib

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


#<--------------------------------------------- CUSTOMER ----------------------------------------------------------------------->


@app.route('/checkFlight', methods = ['GET', 'POST'])
def checkFlight(): 

	username = session['username']
	time = str(request.form.get('viewOption'))

	all = (time == "All flights")
	email = session['email']

	cursor = conn.cursor()

	if all:
		checkExistsquery = "SELECT * FROM flight WHERE (flight_num,airline_name) IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s)"
	else:
		checkExistsquery = "SELECT * FROM flight WHERE ((flight_num,airline_name) IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s)) AND depart_date_time > NOW()"

	cursor.execute(checkExistsquery, (email))
	data = cursor.fetchall()
	# data = type(email)
	cursor.close()

	return render_template('/customerViews/customerOperationResult.html', data=data, time = time)

@app.route('/purchaseView', methods = ['GET', 'POST'])
def purchaseView(): 
	username = session['username']
	email = session['email']

	curr_time = datetime.now()
	day_after = curr_time + timedelta(days=1)
	day_after = day_after.strftime("%Y-%m-%d %H:%M:%S")

	cursor = conn.cursor()
	# query = "SELECT * FROM flight WHERE (flight_num,airline_name) NOT IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s) AND depart_date_time > NOW()"
	query = "SELECT * FROM flight WHERE (flight_num,airline_name) NOT IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s) AND depart_date_time > TIME(%s)"
	

	cursor.execute(query, (email,day_after))
	# cursor.execute(query, (email))
	data = cursor.fetchall()
	# data = type(email)
	cursor.close()

	return render_template('/customerViews/purchaseScreen.html', data=data, day_after =day_after)

@app.route('/cancelView', methods = ['GET', 'POST'])
def cancelView(): 

	username = session['username']
	time = str(request.form.get('viewOption'))

	email = session['email']

	cursor = conn.cursor()

	curr_time = datetime.now()
	day_after = curr_time + timedelta(days=1)
	day_after = day_after.strftime("%Y-%m-%d %H:%M:%S")

	query = "SELECT * FROM flight WHERE ((flight_num,airline_name) IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s)) AND depart_date_time > TIME(%s)"

	cursor.execute(query, (email,day_after))
	data = cursor.fetchall()
	# data = type(email)
	cursor.close()

	return render_template('/customerViews/cancelScreen.html', data=data)

@app.route('/cancelFlight', methods = ['GET', 'POST'])
def cancelFlight(): 
	username = session['username']
	airline_name = request.form['airline_name']
	flight_num = request.form['flight_num']
	time = "hehe"
	email = session['email']

	# result_2 = current_date + timedelta(days=7)
	# Adds 7 days to current_date

	cursor = conn.cursor()

	deleteStatement = "DELETE FROM ticket WHERE customer_email = %s AND airline_name = %s AND flight_num = %s"
	cursor.execute(deleteStatement, (email,airline_name,flight_num))
	# query = "SELECT * FROM ticket WHERE 1"
	# cursor.execute(query)
	# data = type(email)
	conn.commit()
	cursor.close()

	curr_time = datetime.now()
	day_after = curr_time + timedelta(days=1)
	day_after = day_after.strftime("%Y-%m-%d %H:%M:%S")

	cursor = conn.cursor()
	query = "SELECT * FROM flight WHERE ((flight_num,airline_name) IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s)) AND depart_date_time > TIME(%s)"
	cursor.execute(query,(email,day_after))

	data = cursor.fetchall()
	cursor.close()
	return render_template('/customerViews/cancelScreen.html', data=data,email = email, time = time)

@app.route('/purchaseFlight', methods = ['GET', 'POST'])
def purchaseFlight(): 
	username = session['username']
	airline_name = request.form['airline_name']
	flight_num = request.form['flight_num']
	card_num = request.form['card_num']
	card_name = request.form['card_name']
	card_type = str(request.form.get('card_type'))
	expiration_date = request.form['expiration_date']


	time = expiration_date

	email = session['email']
	purchase_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	cursor = conn.cursor()
	query = "SELECT MAX(ticket_id) from ticket WHERE airline_name = %s"
	cursor.execute(query, (airline_name))
	tempData = cursor.fetchall()
	ticketNo = tempData[0]['MAX(ticket_id)']
	if ticketNo:
		ticketNo += 1
	else:
		ticketNo = 1

	# ticketNo = purchase_time
	# data = str(email)
	cursor.close()

	cursor = conn.cursor()
	query = "SELECT seats FROM airplane WHERE id = (SELECT airplane_id FROM flight WHERE (airline_name, flight_num) = (%s, %s))"
	cursor.execute(query, (airline_name,flight_num))
	seats = float(cursor.fetchall()[0]['seats'])
	cursor.close()

	cursor = conn.cursor()
	query = "SELECT COUNT(ticket_id) FROM ticket WHERE flight_num = %s"
	cursor.execute(query, (flight_num))
	booked = cursor.fetchall()[0]['COUNT(ticket_id)']
	cursor.close()

	# query = "INSERT INTO airplane(id, airline_name, manufacturer, seats, age) VALUES(%s, %s, %s, %s, %s)"
	cursor = conn.cursor()
	query = "SELECT base_price FROM flight WHERE (airline_name, flight_num) = (%s,%s)"
	cursor.execute(query, (airline_name,flight_num))
	basePrice = cursor.fetchall()[0]['base_price']
	cursor.close()


	if (booked >= 0.6 * seats):
		price = basePrice * 1.25
	else:
		price = basePrice

	cursor = conn.cursor()
	insertStatement = "INSERT INTO ticket(ticket_id, customer_email, airline_name, flight_num, card_type,card_name,card_num,exp_date,sold_price,purchase_date_time) VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)"
	# cursor.execute(insertStatement, (ticketNo,email,airline_name,flight_num,card_type,card_name,card_num,expiration_date,100,purchase_time))
	# query = "SELECT * FROM ticket WHERE 1"
	# cursor.execute(query)
	# data = type(email)
	error = None
	if booked == seats:
		error = "Unable to book seats, maximum capacity reached"
	else:
		try:
			cursor.execute(insertStatement, (ticketNo,email,airline_name,flight_num,card_type,card_name,card_num,expiration_date,price,purchase_time))
			conn.commit() 
			error = "BOUGHT TICKET SUCCESS!"
			cursor.close()

			cursor = conn.cursor()
			query = "SELECT * FROM flight WHERE ((flight_num,airline_name) IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s)) AND depart_date_time > NOW()"
			cursor.execute(query,session['email'])	
			data = cursor.fetchall()	
			cursor.close()

		except:
			error = "FAILED TO BUY TICKET AIRPLANE, Double Check ID/Airline_Name Fields"
			cursor.close()
			data = []
	# finally:
	# 	cursor.close()


	return render_template('/customerViews/purchaseComplete.html', basePrice = basePrice, seats = seats, booked=booked, error=error,email = email, ticketNo = ticketNo, time = time, data=data)

@app.route('/rateCommentPage', methods = ['GET', 'POST'])
def rateCommentPage(): 

	username = session['username']

	email = session['email']

	cursor = conn.cursor()

	checkExistsquery = "SELECT * FROM flight WHERE ((flight_num,airline_name) IN (SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s)) AND depart_date_time < NOW()"

	cursor.execute(checkExistsquery, (email))
	data = cursor.fetchall()
	# data = type(email)
	cursor.close()

	return render_template('/customerViews/rateCommentScreen.html', data=data)

@app.route('/rateComment', methods = ['GET', 'POST'])
def rateComment():
	email = session['email']
	flight_num = request.form['flight_num']
	airline_name = request.form['airline_name']
	rating = request.form['rating']
	comment = request.form['comment']

	cursor = conn.cursor()
	query = "SELECT depart_date_time FROM flight WHERE flight_num = %s AND airline_name = %s"
	cursor.execute(query, (flight_num,airline_name))
	tempData = cursor.fetchall()
	depart_date_time = str(tempData[0]['depart_date_time'])
	# data = str(email)
	cursor.close()

	cursor = conn.cursor()
	query = "INSERT INTO review(flight_num, depart_date_time, airline_name, email, rating, review) VALUES(%s, %s, %s, %s, %s, %s)"
	error = None

	try:
		cursor.execute(query, (flight_num, depart_date_time, airline_name, email, rating, comment))
		conn.commit() 
		error = "COMMENT ADDED!"
	except:
		error = "COMMENT FAILED"
	finally:
		cursor.close()

	return render_template('/customerViews/messagePage.html', error=error)

@app.route('/trackSpending', methods = ['GET', 'POST'])
def trackSpending(): 

	username = session['username']
	email = session['email']

	curr_time = datetime.now()
	before = curr_time - timedelta(days=180)
	before = before.strftime("%Y-%m-%d %H:%M:%S")
	
	# get email from customer data -> use email to find ticket -> get flights that matches flight_id
	cursor = conn.cursor()
	# query = "SELECT SUM(sold_price) from ticket WHERE customer_email = %s"
	query = "SELECT SUM(sold_price) from ticket WHERE customer_email = %s AND purchase_date_time > %s"

	cursor.execute(query, (email,before))
	tempData = cursor.fetchall()
	totalSpent = tempData[0]['SUM(sold_price)']

	cursor.close()

	return render_template('/customerViews/messagePage.html', error=totalSpent)


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

#<--------------------------------------------- CUSTOMER ----------------------------------------------------------------------->


#<--------------------------------------------- ADMIN ----------------------------------------------------------------------->

@app.route('/adminViews/createAirplane', methods = ['GET', 'POST'])
def createAirPlane():
	# Get form inputs required to create airplane
	id = request.form['ID']
	manufacturer = request.form['Manufacturer']
	seats = request.form['Seats']
	age = request.form['Age']
	airline_name = request.form['Airline_name']

	# Check if admin is authorized to create airplane for this airline 
	username = session['username']
	cursor = conn.cursor()
	query = "SELECT airline_name from airline_staff WHERE username = %s"
	cursor.execute(query, (username)) 
	affiliated_airline = cursor.fetchone()['airline_name']
	cursor.close()
	# Not authorized to create airplane
	if airline_name != affiliated_airline:
		error = "THATS NOT YOUR AIRLINE"
	# Create airplane 
	else:
		cursor = conn.cursor()
		query = "INSERT INTO airplane VALUES(%s, %s, %s, %s, %s) "
		error = None
		try:
			cursor.execute(query, (id, airline_name, manufacturer, seats, age))
			conn.commit() 
			error = "AIRPLANE CREATION SUCCESS!"
		except: # Catching foreign key constraint errors
			error = "FAILED TO CREATE AIRPLANE, Double Check ID/Airline_Name Fields"
		finally:
			cursor.close()
	
	#Get all airplanes that belongs to airline
	cursor = conn.cursor()
	query = "SELECT * FROM airplane WHERE airline_name = %s "	
	cursor.execute(query, affiliated_airline)
	data = cursor.fetchall()
	cursor.close()

	# Display all airplanes belonging to admin's airline
	return render_template('/adminViews/airplaneData.html', data=data, error=error)

@app.route('/adminViews/setFlightStatus', methods= ['GET', 'POST'])
def setFlightStatus(): 
	# gather inputs
	new_stat = request.form['status']
	f_num = request.form['F#']
	airline_name = request.form['Airline_name']
	dep_date_time = request.form['dep']

	# check if airine_name matches 
	username = session['username']
	cursor = conn.cursor()
	query = "SELECT airline_name from airline_staff WHERE username = %s"
	cursor.execute(query, (username)) 
	affiliated_airline = cursor.fetchone()['airline_name']
	cursor.close()
	if airline_name != affiliated_airline:
		error = "THATS NOT YOUR AIRLINE"
		return render_template('/adminViews/statusData.html', error=error)

	# Update flight status 
	cursor = conn.cursor()
	checkExistsquery = "SELECT * FROM flight WHERE flight_num = %s AND airline_name = %s AND depart_date_time = %s"
	cursor.execute(checkExistsquery, (f_num, airline_name, dep_date_time))
	data = cursor.fetchall()
	cursor.close()
	error = "FLIGHT STATUS UPDATE COMPLETE!"
	if data:
		second_cursor = conn.cursor()
		setStatusquery = "UPDATE flight SET stat=%s WHERE flight_num = %s AND airline_name = %s AND depart_date_time = %s"
		second_cursor.execute(setStatusquery, (new_stat, f_num, airline_name, dep_date_time))
		conn.commit() 
		second_cursor.close()
	else:
		error = "NO SUCH FLIGHT EXISTS"

	return render_template('/adminViews/statusData.html', error=error)
	
@app.route('/adminViews/createFlight', methods = ['GET', 'POST'])
def createFlight(): 
	# get form inputs
	f_num = request.form['F#']
	airline_name = request.form['airline_name']
	dep_date_time = request.form['dep']
	dep_airport = request.form['departure_airport']
	arr_airport = request.form['arrival_airport']
	airplane_id = request.form['airplane_id']
	arrive_date_time = request.form['arrive_date_time']
	b_price = request.form['base_price']
	status = request.form['status']

	# check if airine_name matches 
	username = session['username']
	cursor = conn.cursor()
	query = "SELECT airline_name from airline_staff WHERE username = %s"
	cursor.execute(query, (username)) 
	affiliated_airline = cursor.fetchone()['airline_name']
	cursor.close()
	if airline_name != affiliated_airline:
		error = "THATS NOT YOUR AIRLINE"
	else:
		# Create flight 
		cursor = conn.cursor()
		query = "INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		error = None
		try:
			cursor.execute(query, (f_num,airline_name,dep_date_time,dep_airport,arr_airport, airplane_id,arrive_date_time,b_price,status))
			conn.commit() 
			error = "FLIGHT CREATED SUCCESSFULLY!"
		except:
			error = "FAILED TO CREATE FLIGHT, Double Check F Number/ Departure Airport/ Arrival Airport"
		finally:
			cursor.close()

	return render_template('/adminViews/createFlightData.html', error=error)

@app.route('/adminViews/adminViewFlight', methods= ['GET', 'POST'])
def viewFlight():
	# get airline
	username = session['username']
	cursor = conn.cursor()
	query = "SELECT airline_name FROM airline_staff WHERE username = %s"
	cursor.execute(query, (username)) 
	affiliated_airline = cursor.fetchone()['airline_name']
	cursor.close()

	# get time 30 days from now 
	starttime = datetime.now()
	delta = timedelta(days= 30)
	endtime = delta + starttime 
	starttime = starttime.strftime("%Y-%m-%d %H:%M:%S")
	endtime = endtime.strftime("%Y-%m-%d %H:%M:%S")

	# get future flights > current time, < 30 days from now
	cursor = conn.cursor()
	# we will assume flight operated by airline are atomic; thus flight must complete before 30 day mark 
	query = ( 
			"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) AS avg_rat FROM "
			"flight NATURAL LEFT OUTER JOIN review "
			"WHERE airline_name = %s "
			"GROUP BY flight_num, airline_name, depart_date_time" 
			)
	cursor.execute(query, (affiliated_airline))
	data = cursor.fetchall()
	cursor.close()
	error = None 

	# refresh with parameters (try statement will collapse if this originates from view button)
	# + get average ratings for each flight
	try: 
		# past/present/current
		reference = request.form['reference']
		# get time range
		rangeLow = request.form['rangeLow']
		rangeHigh = request.form['rangeHigh']
		# get more info (at least one of these are necessary for querying)
		source_air = request.form['source_air']
		dest_air = request.form['dest_air']
		source_city = request.form['source_city']
		dest_city = request.form['dest_city']

		cursor = conn.cursor()
		query = ""
		if reference == "past":
			if source_air or dest_air or source_city or dest_city:
				query = (
				"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) as avg_rat FROM "
					"(" 
						"SELECT * from flight where airline_name = %s AND arrive_date_time < %s AND "
						"(departure_airport = %s OR arrival_airport = %s OR (departure_airport IN (SELECT name FROM airport WHERE city = %s)) OR (arrival_airport IN (SELECT name FROM airport WHERE city = %s))) "
					") as flight NATURAL LEFT OUTER JOIN review "
					"GROUP BY flight_num, airline_name, depart_date_time " 
				) 
				cursor.execute(query, (affiliated_airline, rangeLow, source_air, dest_air, source_city, dest_city))
			else:
				query = (
				"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) as avg_rat FROM "
					"(" 
						"SELECT * from flight where airline_name = %s AND arrive_date_time < %s "
					") as flight NATURAL LEFT OUTER JOIN review "
					"GROUP BY flight_num, airline_name, depart_date_time " 
				) 
				cursor.execute(query, (affiliated_airline, rangeLow))
			
		elif reference == "current":
			if source_air or dest_air or source_city or dest_city:
				query = (	
					"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) as avg_rat FROM "
						"("
							"SELECT * from flight where airline_name = %s AND arrive_date_time >= %s AND arrive_date_time <= %s AND "
							"(departure_airport = %s OR arrival_airport = %s OR (departure_airport IN (SELECT name FROM airport WHERE city = %s)) OR (arrival_airport IN (SELECT name FROM airport WHERE city = %s))) "
						") as flight NATURAL LEFT OUTER JOIN review "
						"GROUP BY flight_num, airline_name, depart_date_time" 
					)
				cursor.execute(query, (affiliated_airline, rangeLow, rangeHigh, source_air, dest_air, source_city, dest_city))
			else:
				query = (	
					"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) as avg_rat FROM "
						"("
							"SELECT * from flight where airline_name = %s AND arrive_date_time >= %s AND arrive_date_time <= %s "
						") as flight NATURAL LEFT OUTER JOIN review "
						"GROUP BY flight_num, airline_name, depart_date_time" 
					)
				cursor.execute(query, (affiliated_airline, rangeLow, rangeHigh))
		else:
			if source_air or dest_air or source_city or dest_city:
				query = (
					"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) as avg_rat FROM "
						"("
							"SELECT * FROM flight WHERE airline_name = %s AND arrive_date_time > %s AND " 
							"(departure_airport = %s OR arrival_airport = %s OR (departure_airport IN (SELECT name FROM airport WHERE city = %s)) OR (arrival_airport IN (SELECT name FROM airport WHERE city = %s))) "
						") as flight NATURAL LEFT OUTER JOIN review "
						"GROUP BY flight_num, airline_name, depart_date_time" 
				)
				cursor.execute(query, (affiliated_airline, rangeHigh, source_air, dest_air, source_city, dest_city))
			else:
				query = (
					"SELECT flight_num, airline_name, depart_date_time, departure_airport, arrival_airport, airplane_id, arrive_date_time, base_price, stat, AVG(rating) as avg_rat FROM "
						"("
							"SELECT * FROM flight WHERE airline_name = %s AND arrive_date_time > %s " 
						") as flight NATURAL LEFT OUTER JOIN review "
						"GROUP BY flight_num, airline_name, depart_date_time" 
				)
				cursor.execute(query, (affiliated_airline, rangeHigh))
		data = cursor.fetchall()
		cursor.close()
	# if just view button press, proceed to return as normal 
	except:
		pass 

	# render future flights by default
	return render_template('/adminViews/adminViewFlight.html', time= starttime, data=data,  error=error)

@app.route('/adminViews/addAirport', methods=['POST', 'GET'])
def addAirport():
	# gather inputs
	name = request.form['name']
	country = request.form['country']
	city = request.form['city']
	type = request.form['type']

	cursor = conn.cursor()
	query = "INSERT INTO airport VALUES(%s, %s, %s, %s)"
	error = None 
	try:
		cursor.execute(query, (name, city, country, type))
		conn.commit()
		error = "Airport Addition Successful"
	except:
		error = "Add Airport Failed, check name input again"
	
	cursor.close()
	return render_template('adminViews/airportData.html', error=error)
	
@app.route('/adminViews/viewReviews', methods=['POST', 'GET'])
def viewReviews():
	# gather flight info 
	flight_num = request.form['F#']
	airline_name = request.form['airline_name']
	depart_date_time = request.form['depart_date_time']

	# get reviews, ratings, and customer info of the relevant flight
	cursor = conn.cursor()
	query = "SELECT * FROM review WHERE flight_num = %s AND airline_name= %s AND depart_date_time = %s "
	cursor.execute(query, (flight_num, airline_name, depart_date_time))
	data = cursor.fetchall()
	cursor.close()
	error = None 

	return render_template('adminViews/reviewsData.html', data=data, flight_num = flight_num, airline_name = airline_name, depart_date_time = depart_date_time, error=error)
	
@app.route('/adminViews/viewCustomers')
def viewCustomers():
	# # get airline
	# username = session['username']
	# cursor = conn.cursor()
	# query = "SELECT airline_name FROM airline_staff WHERE username = %s"
	# cursor.execute(query, (username)) 
	# affiliated_airline = cursor.fetchone()['airline_name']
	# cursor.close()
	
	# get time 30 days from now 
	endtime = datetime.now()
	delta = timedelta(days= 365)
	starttime = endtime - delta
	starttime = starttime.strftime("%Y-%m-%d %H:%M:%S")
	endtime = endtime.strftime("%Y-%m-%d %H:%M:%S")

	# get most frequent customer within last year
	cursor = conn.cursor()
	query = (
		"SELECT name, email, MAX(c) as max_freq FROM"
		"("
			"SELECT name, email, COUNT(ticket_id) as c FROM (ticket,customer) NATURAL JOIN flight "
			"WHERE arrive_date_time >= %s AND arrive_date_time <= %s AND ticket.customer_email = customer.email "
			"GROUP BY email "
		") AS customer_count" 
	)
	cursor.execute(query, (starttime, endtime))
	MFCdata = cursor.fetchall()
	cursor.close()
	error = None 

	# get customer list
	cursor = conn.cursor()
	query = "SELECT * from customer"
	cursor.execute(query)
	customers = cursor.fetchall()
	cursor.close()

	return render_template('/adminViews/customerData.html', data= MFCdata, customers = customers)

@app.route('/adminViews/getCustomerFlights', methods= ['POST', 'GET']) 
def getCustomerFlights():
	email = request.form['email']

	cursor = conn.cursor()
	query = "SELECT flight_num, airline_name FROM ticket WHERE customer_email = %s"
	cursor.execute(query, email)
	data = cursor.fetchall()
	cursor.close()

	return render_template('/adminViews/customerFlights.html', data=data)


@app.route('/adminViews/viewReport', methods= ['GET', 'POST'])
def viewReport():
	# input year
	year = request.form['year']

	# get month & ticket count for each month of the year 
	cursor = conn.cursor()
	query = (
		"SELECT MONTH(purchase_date_time) as M, COUNT(ticket_id) as C "
		"FROM ticket "
		"WHERE YEAR(purchase_date_time) = %s "
		"GROUP BY MONTH(purchase_date_time) "
	)
	cursor.execute(query, (year))
	data = cursor.fetchall()
	cursor.close()
	
	# display monthly ticket sale information
	return render_template('/adminViews/reportData.html', data=data, year=year)

@app.route('/adminViews/viewRevenue', methods=['POST','GET'])
def viewRevenue():
	# get current time 
	year = datetime.now().year 
	month = datetime.now().month
	
	# get total revenue for this month 
	cursor = conn.cursor()
	query = (
		"SELECT SUM(sold_price) as tot_sold_price "
		"FROM ticket "
		"WHERE MONTH(purchase_date_time) = %s AND YEAR(purchase_date_time) = %s"
	)
	cursor.execute(query, (month, year))
	monthData = cursor.fetchall()
	cursor.close()

	# get total revenue for this year
	cursor = conn.cursor()
	query = (
		"SELECT SUM(sold_price) as tot_sold_price "
		"FROM ticket " 	
		"WHERE YEAR(purchase_date_time) = %s "
	)
	cursor.execute(query, (year))
	yearData = cursor.fetchall()
	cursor.close()

	print(yearData,monthData )

	return render_template('/adminViews/revenueData.html', monthData = monthData, month=month, yearData = yearData, year=year)


#<--------------------------------------------- ADMIN ----------------------------------------------------------------------->

#<--------------------------------------------- NON-USER FEATURES ----------------------------------------------------------------------->

def hash_helper(password):
	result = hashlib.md5()
	result.update(password.encode())
	return result.hexdigest()

def checkEmail(email):
	regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
	return re.fullmatch(regex, email)

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

#<--------------------------------------------- NON-USER FEATURES ----------------------------------------------------------------------->

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

	# adding 5gz as password
	salt = "5gz"
	
	# Adding salt at the last of the password
	dataBase_password = password+salt
	# Encoding the password
	password = hashlib.md5(dataBase_password.encode()).hexdigest()

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
		session['logged'] = True 

		# get email from customer data -> use email to find ticket -> get flights that matches flight_id

		if dataCustomer:
			cursor = conn.cursor()
			query = "SELECT email FROM customer WHERE username = %s"
			cursor.execute(query, (username))
			tempData = cursor.fetchall()
			email = str(tempData[0]['email'])
			# data = str(email)
			cursor.close()
			session['email'] = email
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

	# adding 5gz as password
	salt = "5gz"
	
	# Adding salt at the last of the password
	dataBase_password = password+salt
	# Encoding the password
	password = hashlib.md5(dataBase_password.encode()).hexdigest()
	print(password)

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
		return render_template('/adminViews/adminRegister.html', error = error)
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

	# adding 5gz as password
	salt = "5gz"
	
	# Adding salt at the last of the password
	dataBase_password = password+salt
	# Encoding the password
	password = hashlib.md5(dataBase_password.encode()).hexdigest()

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE username = %s'
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
		return render_template('index.html',error=error)

@app.route('/logout', methods=['GET','POST'])
def logout():
	session.pop('username')
	if not session['admin']:
		session.pop('email')
	session.pop('admin')
	return render_template('goodBye.html')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)


# CODE FOR REFERENCE
# -----------------------------------------------------------------------------
# @app.route('/home')
# def home():
#     username = session['username']
#     cursor = conn.cursor()
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, (username))
#     data1 = cursor.fetchall() 
#     for each in data1:
#         print(each['blog_post'])
#     cursor.close()
#     return render_template('home.html', username=username, posts=data1)

# @app.route('/post', methods=['GET', 'POST'])
# def post():
# 	username = session['username']
# 	cursor = conn.cursor()
# 	blog = request.form['blog']
# 	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
# 	cursor.execute(query, (blog, username))
# 	conn.commit()
# 	cursor.close()
# 	return redirect(url_for('home'))

# -----------------------------------------------------------------------------


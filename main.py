import datetime
import random 
from flask import Flask, render_template, request, Response, redirect, url_for, flash, session
from google.cloud import datastore
import google.oauth2.id_token
from google.auth.transport import requests


app = Flask(__name__)
app.secret_key = '12345'
# get access to the datastore client so we can add and store data in the datastore
datastore_client = datastore.Client()

# get access to a request adapter for firebase as we will need this to authenticate users
firebase_request_adapter = requests.Request()
def createUserDetails(claims):
    entity_key = datastore_client.key('UserDetails', claims['email']) 
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email' : claims['email'],
        'name'  : claims['name'],
        'creation_date': datetime.datetime.now(), 
        'bookings_list': [],
        'room_list': []

    })

    datastore_client.put(entity)

def retrieveUserDetails(claims):
    entity_key = datastore_client.key('UserDetails', claims['email']) 
    entity = datastore_client.get(entity_key)
    
    return entity

def createNewBooking(category, status, Date, Duration ):
    id = random.getrandbits(63)

    entity_key = datastore_client.key('Booking', id)

    entity =datastore.Entity(key=entity_key)

    entity.update({
        'category': category,
        'status': status,
        'Date': Date,
        'Duration': Duration,
        'roomID':[]
    })

    datastore_client.put(entity)

    session['entity']=entity

    return id 

def retrieveBooking(userDetails):
    booking_ids=userDetails['bookings_list']
    booking_keys=[]
    

    for i in range(len(booking_ids)):
        booking_keys.append(datastore_client.key('Booking', booking_ids[i]))
    
    bookings_list=datastore_client.get_multi(booking_keys)
    
    return bookings_list

def editBooking(id, roomID, category, status, Date, Duration): 
    entity_key = datastore_client.key('Booking', id)

    entity =datastore.Entity(key=entity_key)

    entity.update({
        'category': category,
        'status': status,
        'Date': Date,
        'Duration': Duration
    })

    datastore_client.put(entity)



def addBookingToUser(userDetails, id):
    booking_keys=userDetails['bookings_list']
    booking_keys.append(id)

    userDetails.update({
        'bookings_list': booking_keys 
    })

    datastore_client.put(userDetails)



def createNewRoom(Rname, Rcapacity, gridRadios):
    id = random.getrandbits(63)
    state='available'
    
    entity_key=datastore_client.key('room', id)
    entity=datastore.Entity(key=entity_key)
    entity.update({
        'id': id,
        'Rname': Rname,
        'Rcapacity': Rcapacity,
        'gridRadios': gridRadios,
        'state':state

    })

    datastore_client.put(entity)

    return id 

def addRoomToBookings(roomID):
    #Booking=session['entity']

    room_keys=Booking['roomID']
    room_keys.append(roomID)
    entity_key=datastore_client.key('GpuApplication', name)
    entity=datastore_client.get(entity_key)
    Booking.update({
        'room_keys': room_keys 
    })

    datastore_client.put(Booking)



def retrieveRoom(roomID):
    entity_key=datastore_client.key('room', roomID)
    entity=datastore_client.get(entity_key)

    return entity

def deleteRoom(roomID):
    entity_key =datastore_client.key('room', roomID)
    datastore_client.delete(entity_key)

def addRoomToUser(userDetails, id):
    room_keys=userDetails['room_list']
    room_keys.append(id)

    userDetails.update({
        'room_list': room_keys 
    })

    datastore_client.put(userDetails)

def deleteBooking(claims, id):
    userDetails = retrieveUserDetails(claims) 
    booking_list_keys = userDetails['bookings_list']
    
    booking_key = datastore_client.key('Booking', booking_list_keys[id]) 
    datastore_client.delete(booking_key)
    
    del booking_list_keys[id] 
    userDetails.update({
        'booking_list' : booking_list_keys 
    })
    
    datastore_client.put(userDetails)

@app.route('/')
def root():
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    result=None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            
            userDetails = retrieveUserDetails(claims)
            if userDetails == None:
                createUserDetails(claims)
                userDetails = retrieveUserDetails(claims)
            

            query = datastore_client.query(kind='room')
            result = query.fetch()
            
                
        except ValueError as exc:
            error_message = str(exc)
    return render_template('indexPage.html', user_data=claims, result=result, userDetails=userDetails, error_message=error_message)

@app.route('/addRoom', methods=['POST', 'GET'])
def addRoomPageHandler():
    return render_template('addRoom.html')

@app.route('/booking', methods=['POST', 'GET'])
def bookingPageHandler():
    return render_template('booking.html')

@app.route('/myRooms', methods=['POST', 'GET'])
def manageRoomHandler():
    return render_template('myRoomList.html')




@app.route('/createRoom', methods=['POST', 'GET'])
def createRoomHander():
    id_token = request.cookies.get("token") 
    claims = None
    userDetails = None
    error_message = None


    if id_token:

        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
            
            id =createNewRoom(request.form.get('Rname'), request.form.get('Rcapacity'), request.form.get('gridRadios'))

        except ValueError as exc: 
            error_message = str(exc)
        
        flash('You have successfully created a room')
        
    return redirect('/')

@app.route('/booking_room/<int:ID>')
def createBookingHander(ID):
    id_token = request.cookies.get("token") 
    claims = None
    userDetails = None

    if id_token:

        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)

            id = createNewBooking(ID, request.form.get('status'), request.form.get('Date'), request.form.get('Duration'))
            addRoomToBookings(id)
            #flask("You have successfully booked a room")

        except ValueError as exc: 
            error_message = str(exc)

    return redirect('/')
   

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

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

def createNewBooking(claims, title, startDate, endDate, startTime, endTime, category, roomID):
    id = random.getrandbits(63)
    
    if isFound(request.form.get('title'), request.form.get('startDate'), request.form.get('endDate'), request.form.get('startTime'), request.form.get('endTime'), request.form.get('category'), bookingID):
        return -1
        
    entity_key = datastore_client.key('UserDetails', claims['email'], 'Booking', id)

    entity =datastore.Entity(key=entity_key)

    entity.update({
        'title': title,
        'startDate': startDate,
        'endDate': endDate,
        'startTime': startTime,
        'endTime': endTime, 
        'category': category,
        'roomID': roomID
    })

    datastore_client.put(entity)  
    
    return id 

def retrieveBooking(email, bookingID):
    entity_key = datastore_client.key('UserDetails', email, 'Booking', bookingID)
    entity = datastore_client.get(entity_key)
    
    return entity

def updateBooking(claims, title, startDate, endDate, startTime, endTime, category, bookingID): 
    ancestor_key= datastore_client.key('UserDetails', claims['email'], 'Booking', bookingID)
    entity = datastore_client.get(ancestor_key)

    entity.update({
        'title': title,
        'startDate': startDate,
        'endDate': endDate,
        'startTime': startTime,
        'endTime': endTime, 
        'category': category
    })

    datastore_client.put(entity)



# def addBookingToUser(userDetails, id):
#     booking_keys=userDetails['bookings_list']
#     booking_keys.append(id)

#     userDetails.update({
#         'bookings_list': booking_keys 
#     })

#     datastore_client.put(userDetails)



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
        'state':state,
        'booking_list':{}

    })

    datastore_client.put(entity)

    return id 

def addBookingsToRoom( bookingID, email, roomID, startDate, endDate, startTime, endTime):
    booking_list=[]
    temp=[]
    entity_key=datastore_client.key('room', roomID)
    entity=datastore_client.get(entity_key)

    myList = {
        "bookingID": bookingID,
        "email": email,
        "startDate": startDate,
        "endDate": endDate,
        "startTime": startTime,
        "endTime": endTime
    }

    if len(entity['booking_list'])==0:
        temp.append(dict(myList))
        entity.update({
            'booking_list':temp 
        })
        datastore_client.put(entity)
    else:    
        temp=entity['booking_list']
        temp.append(dict(myList))
        booking_list=temp
        entity.update({
            'booking_list': booking_list
        })
        datastore_client.put(entity)



def retrieveRoom(roomID):
    entity_key=datastore_client.key('room', roomID)
    entity=datastore_client.get(entity_key)

    return entity

def isFound(title, startDate, endDate, startTime, endTime, category, roomID,bookingID):
    booking_list = None
    entity_key= datastore_client.key('room', roomID)
    mylist = datastore_client.get(entity_key)

    booking_list=mylist['booking_list']
    print(booking_list)
    
    
    for booking in booking_list:
        #print(booking['startDate'])
        if booking['startDate']== startDate and booking['endDate'] == endDate and booking['startTime'] == startTime and booking['endTime'] == endTime and booking['bookingID'] != bookingID :
            print("true")
            return True

    print("False")       
    return False

def updateBookingInRoom(title, startDate, endDate, startTime, endTime, category, roomID,bookingID):
   
    booking_list = None
    entity_key= datastore_client.key('room', roomID)
    mylist = datastore_client.get(entity_key)

    booking_list=mylist['booking_list']
    
    expectedResult = [d for d in booking_list if d['bookingID'] == bookingID]

    for booking in booking_list:
        if booking == expectedResult[0]:
            booking_list.remove(expectedResult[0])

    myDict = {
        "bookingID": bookingID,
        "email": session['email'],
        "startDate": startDate,
        "endDate": endDate,
        "startTime": startTime,
        "endTime": endTime
    }

    temp=[]
    if len(mylist['booking_list'])==0:
        temp.append(dict(myDict))
        mylist.update({
            'booking_list':temp 
        })
        datastore_client.put(mylist)
    else:    
        temp=booking_list
        temp.append(dict(myDict))
        booking_list=temp
        mylist.update({
            'booking_list': booking_list
        })
        datastore_client.put(mylist)
        
    
def deleteRoom(claims, id):
    roomlist=[]
    userDetails = retrieveUserDetails(claims) 
    room_list_keys = userDetails['room_list']

    entity_key =datastore_client.key('room', id)
    datastore_client.delete(entity_key)

    for key in room_list_keys:
        if key !=id:
            roomlist.append(key)
  
    userDetails.update({
    'room_list' : roomlist
    })

    datastore_client.put(userDetails)

def retrieveRooms(userDetails): 
    # make key objects out of all the keys and retrieve them 
    room_ids = userDetails['room_list']
    room_keys = []
    for i in range(len(room_ids)):
        room_keys.append(datastore_client.key('room', room_ids[i]))
    
    room_list = datastore_client.get_multi(room_keys)     
    return room_list

def addRoomToUser(userDetails, id):
    room_keys=userDetails['room_list']
    room_keys.append(id)

    userDetails.update({
        'room_list': room_keys 
    })

    datastore_client.put(userDetails)

def deleteBooking(claims, id):
    entity_key = datastore_client.key('UserDetails', claims['email'], 'Booking', id)    
    datastore_client.delete(entity_key)

def deleteBookingInRoom( roomID, bookingID):
    booking_list = None
    entity_key= datastore_client.key('room', roomID)
    mylist = datastore_client.get(entity_key)

    booking_list=mylist['booking_list']
    
    expectedResult = [d for d in booking_list if d['bookingID'] == bookingID]

    for booking in booking_list:
        if booking == expectedResult[0]:
            booking_list.remove(expectedResult[0])

    mylist.update({
        'booking_list': booking_list
    })
    datastore_client.put(mylist)

def roomList(result):
    
    booking_list = None
    result=result
    mydict={}
    list=[]

    for i in range(len(result)):
        for res in result[i]['booking_list']:
            if res['email']==session['email']:
                mydict.update({
                    'roomName': result[i]['Rname'],
                    'roomCapacity': result[i]['Rcapacity'],
                    'BookingNumber': res['bookingID'],
                    'startDate': res['startDate'],
                    'endDate': res['endDate'],
                    'email':res['email'],
                    'startTime': res['startTime'],
                    'endTime': res['endTime']
                })
                list.append(dict(mydict))

    return list 


@app.route('/')
def root():
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    result=None
    email=None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            session['email']=claims['email']

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

@app.route('/booking/<int:id>', methods=['POST', 'GET'])
def bookingPageHandler(id):

    return render_template('booking.html', id=id)

@app.route('/myRooms', methods=['POST', 'GET'])
def manageRoomHandler():
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    list=[]

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
            if userDetails == None:
                createUserDetails(claims)
                userDetails = retrieveUserDetails(claims)
            
            result=retrieveRooms(userDetails)
            list=roomList(result)

        except ValueError as exc:
            error_message = str(exc)
        
   
    return render_template('myRoomList.html', data_list=list)

@app.route('/editBooking/<int:booking_id>/<int:roomID>', methods=['POST', 'GET'])
def editBookingHandler(booking_id, roomID):
    userEmail=session['email']
    result = retrieveBooking(userEmail, booking_id)
    return render_template('editBookings.html', booking_id=booking_id, roomID=roomID, result=result)

@app.route('/showBooking/<int:id>', methods=['POST', 'GET'])
def ShowBookingHandler(id):
    userEmail=  session['email']
    result = retrieveRoom(id)
    return render_template('showBooking.html', result=result, userEmail=userEmail, roomID=id)

@app.route('/deleteRoom/<int:id>', methods=['POST', 'GET'])
def deleteRoomHandler(id):
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
            if userDetails == None:
                createUserDetails(claims)
                userDetails = retrieveUserDetails(claims)
             
            result = retrieveRoom(id)

            if len(result['booking_list'])==0:
                deleteRoom(claims, id)
                flash("You have successfully deleted the room")
            else:
                flash("You can't delete a room that still have bookings")

        except ValueError as exc:
            error_message = str(exc)

    return redirect('/')

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
            
            createNewRoom(request.form.get('Rname'), request.form.get('Rcapacity'), request.form.get('gridRadios'))
            
           # addBookingToRoom(id)

        except ValueError as exc: 
            error_message = str(exc)
        
        flash('You have successfully created a room')
        
    return redirect('/')

@app.route('/booking_room/<int:id>', methods=['POST', 'GET'])
def createBookingHander(id):
    id_token = request.cookies.get("token") 
    claims = None
    roomID=id
    userDetails = None

    if id_token:

        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
        
            bookingID = createNewBooking(claims, request.form.get('title'), request.form.get('startDate'), request.form.get('endDate'), request.form.get('startTime'), request.form.get('endTime'), request.form.get('category'), roomID)
            #addBookingToUser(userDetails, bookingID)
            addRoomToUser(userDetails, roomID)
            addBookingsToRoom( bookingID, claims['email'], roomID, request.form.get('startDate'), request.form.get('endDate'), request.form.get('startTime'), request.form.get('endTime'))
            #flask("You have successfully booked a room")

        except ValueError as exc: 
            error_message = str(exc)

    return redirect('/')

@app.route('/edit_booking_room/<int:id>/<int:roomID>', methods=['POST', 'GET'])
def edit_BookingHander(id, roomID ):
    id_token = request.cookies.get("token") 
    claims = None
    bookingID=id
    userDetails = None

    if id_token:

        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)

            if isFound(claims, request.form.get('title'), request.form.get('startDate'), request.form.get('endDate'), request.form.get('startTime'), request.form.get('endTime'), request.form.get('category'), bookingID):
                updateBooking(claims, request.form.get('title'), request.form.get('startDate'), request.form.get('endDate'), request.form.get('startTime'), request.form.get('endTime'), request.form.get('category'), bookingID)
                updateBookingInRoom(request.form.get('title'), request.form.get('startDate'), request.form.get('endDate'), request.form.get('startTime'), request.form.get('endTime'), request.form.get('category'), roomID, bookingID)
            else:
                print("error")
            
        except ValueError as exc: 
            error_message = str(exc)

    return redirect('/')

@app.route('/delete_booking_room/<int:id>/<int:roomID>', methods=['POST', 'GET'])
def delete_BookingHander(id, roomID ):
    id_token = request.cookies.get("token") 
    claims = None
    bookingID=id
    userDetails = None

    if id_token:

        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
                      
            deleteBooking(claims, bookingID)
            deleteBookingInRoom( roomID, bookingID)

        except ValueError as exc: 
            error_message = str(exc)

    return redirect('/')

@app.route('/showAllRooms', methods=['POST', 'GET'])
def showAllRoomsHandler():
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    num=None
    list=None
    data=None
    

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
            if userDetails == None:
                createUserDetails(claims)
                userDetails = retrieveUserDetails(claims)
            
            if request.method =='POST':
                if request.form['par']=="all":
                    result=retrieveRooms(userDetails)
                    list=roomList(result)
            
        except ValueError as exc:
            error_message = str(exc)            

     
    return render_template('myRoomList.html', data=list, data_list=list)

@app.route('/filterRoom/<int:id>', methods=['POST', 'GET'])
def filterRoomHandler(id):
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    temp=None
    list=None

    

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
            if userDetails == None:
                createUserDetails(claims)
                userDetails = retrieveUserDetails(claims)
                      
            result=retrieveRooms(userDetails)
            temp=roomList(result)

            for t in temp:
                if(t['BookingNumber']==id):
                    list=t 
            
        except ValueError as exc:
            error_message = str(exc)            

     
    return render_template('myRoomList.html', list=list)



@app.route('/date', methods=['POST', 'GET'])
def dateHandler():
    id_token = request.cookies.get("token") 
    error_message = None
    claims = None
    userDetails = None
    temp=None
    list=[]
    startDate = None
    endDate = None


    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            userDetails = retrieveUserDetails(claims)
            if userDetails == None:
                createUserDetails(claims)
                userDetails = retrieveUserDetails(claims)

            if request.method =="POST":
                startDate=request.form["startDate"]
                endDate=request.form["endDate"]
                      
            result=retrieveRooms(userDetails)
            temp=roomList(result)

            for t in temp:
                if(t['startDate'] >= startDate and t['endDate'] <= endDate):
                    list.append(t)
              
            
        except ValueError as exc:
            error_message = str(exc) 

    return render_template('myRoomList.html', data=list, data_list=temp)    

    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

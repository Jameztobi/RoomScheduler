# RoomScheduler
Working Environment: 
There are a number of things that should be installed and setup before you attempt to run any of the programs here. 
1.	A decent syntax highlighting text editor with support for: 
•	Python
•	HTML 
•	CSS 
•	JS, 
•	Yaml,
•	 JSON  
•	Git integration. 

2.	An installation of python 3.8 that is accessible from anywhere on the command line. i.e. your PATH variable has been modified to find it.

3.	 An installation of google app engine with the app-engine-python and app-engine-python- extras installed that is also accessible from anywhere on the command line. i.e. your PATH variable has been modified to find it 
Once you have all of the above installed and setup then you are ready to go with building Google App Engine applications 

Building a Room Scheduler 
First before we can start with anything we will need to create a python virtual environment as we will need to install things into it without messing with the local python environment. The instructions you see here are taken from: 
https://cloud.google.com/appengine/docs/standard/python3/quickstart 
Specifically the Linux/OSX version. There are Windows versions of these as well on the same page. First open a command line and navigate to the directory where you will write the code for these examples. 
When you get there run the following command: 
python3 -m venv env 
This will create a directory called “env” that contains a python virtual environment that is separate from the regular python environment. 

After this we will need to run the following command 
source env/bin/activate
Application Development Steps:
1.	create a new directory for the application.

2.	inside that directory below is the directory and file structure 
app.yaml 
main.py 
requirements.txt 
static/ 
◦ script.js 
◦ style.css 
templates/ 
◦ main.html 

3.	inside that directory create a file called requirements.txt and add the following text into it   
 Flask==1.1.2 
  google-cloud-datastore==1.15.0
  google-auth==1.21.2
  requests==2.24.0

The requirements.txt file is there to tell Google App Engine what additional libraries are needed in order to run your application. In this case we are stating that we need the Flask web framework and specifically version 1.1.2 in order to run our application. If we are developing the application locally we will need to install the requirements by hand which will be covered in a later step. Any additional libraries you will need must be specified in this file. 

Note that it is not possible to add any Python library of your choosing to this as Google App Engine runs a restricted version of Python3. Google App Engine may also have a deny-list of libraries that are not permitted to be installed as well and your chosen library(ies) may appear on that list. 





4.	In the file called ‘app.yaml’, you find the following code. 
   runtime: python38

 handlers:
- url : /static
  static_dir : static

- url : /.*
  script : auto


5.	In the file called ‘main.py’ and add the python code files 

6.	open a console and navigate to the project directory. Make sure you have created your environment and sourced it as shown above and run the following command 
                pip install -r requirements.txt

7.	Before you go to run this project you will need the JSON file nearby to access the datastore. Before you run your application in your command line you will need to set the session variable GOOGLE_APPLICATION_CREDENTIALS with the location of this JSON file. In my case I have the JSON file above the directory this project runs in so in Linux I would run the following command to set that session variable 

export GOOGLE_APPLICATION_CREDENTIALS=”../app-engine-3-testing.json” 

where app-engine-3-testing.json is my JSON file. After this run the project as normal and every time you visit the root page now a new visit time will be added and the list will be dynamically updated. 

8.	run your application by executing the following command:
                 python main.py      

This will start your Flask application and if you navigate to localhost:8080 in your web browser you will see the message “Hello world” in plain text if everything is working correctly. 












Data structure
-List: A list was used to store the list of room lists for a user entity.  It is far better than having a variable for each room. It will be too cumbersome to manage in an event when the exact number of rooms is not known. A list can also be easily extracted and used to perform some operation and returned to the datastore. 
	
-Dictionary: This data structure helps us to map an attribute to its values. It is essential because using a key-value pair is the same way the datastore works using NoSQL. It makes it very easy and fast to retrieve values from the data store.   

Database design 
The model is made up of a user, booking, and room. The structure of the database design is that every booking is tied to a user. However, the user entity has a list attribute used to save room keys where it has a booking. Then we have the room entity that contains specific attributes for the entity, including a list that contains all the booking for the room entity. 
A user entity is identified uniquely by the user's email, which serves as the key in the data store, while the room entity is identified uniquely by a random 63 bits number, which is also the key for the room entity. Finally, the booking entity is identified uniquely using the ancestry key; this comprises the user entity and its key: the user's email and the booking ID, a random 63-bit number.

 


 


 




 





METHOD IMPLEMENTATION AND DEFINATION 

Helper Method: 
1) To create a user: This method takes in claims to create an entity of a user. A user entity will have a name, email, the entity's creation date, and a list of the potential rooms that the user might create in the application. This information is stored in the datastore using the user's email as a key.

2) To retrieve user details: This method will help to return the user entity.

3) To create a new Booking: This method first calls another helper method to check if that booking is available. If the booking is available, then booking information will be passed into the datastore, and we attach each booking to a particular user entity in the datastore. Also,  a random 63-bit number id is created, using it as a key for the booking in the datastore, and turns the key.

4) To check if a booking is available: This method checks if a particular booking is available in the datastore. If not available, it returns true, and if available, it returns false.

5) To retrieve a particular user's booking: First of all, this method takes in the user's email and the booking ID. Then it uses this information to get the booking from the datastore and return it to the caller. 

6) To update a booking: This method takes a list of variables such as claims, title, startDate, endDate, startTime, endTime, category, booking ID. Then, it retrieves the particular booking to be updated using the booking ID and the ancestry key. Then the attributes of the booking are updated with new values. Finally, the entity is returned to the datastore.
 
7)  To create a room: This method takes in  3 variables: the room name, room capacity, and one option. It generates an id from a random 63-bit number. This number is used as a key when creating a new room entity. Afterward, the variable passed into the method as an attribute of the entity. The room entity has an array to store all the booking id for that particular room. Then it is passed into the datastore, and the room Id is returned to the caller. 

8) To add a booking to a user: This method takes in a list of variables such as booking ID, email, roomID, startDate, endDate, startTime, endTime. Create two list variables using the roomID, retrieve the room entity from the datastore. Next, we populate the first list variable created with all the list values passed into the method. 
some conditions:
if the length of the bookings in the entity equals zero, we equate the variable containing our booking list to the booking array entity in the datastore.  
If not, we retrieve the array of booking in that room, then append the new values to the end of the array and return the entity to the datastore. 

9) To retrieve room: This method takes in the room id and then uses it to retrieve the room entity from the datastore. 

10) To update a booking in a room: This method takes in a list of parameters. Then it uses the roomID, retrieve the room entity from the datastore. Then retrieve the booking list in the entity and save it in another variable. Then iterate through the booking list and retrieve and the attribute for the array where the booking ID is equal to the booking ID passed. 
Then remove the retrieve list from the booking list. Afterward, we create and update the dictionary by passing in the new values into the method. 
some conditions:
if the length of the bookings in the entity equals zero, we equate the variable containing our booking list to the booking array entity in the datastore.  
If not, we retrieve the array of booking in that room, then append the new values to the end of the array and return it to the datastore. 

11) To delete room: This method takes in two variables: the claim and roomID. The user details are retrieved, and from the user detail entity, we extract the room keys (id). Then using the room Id, we get the entity key and then use that to delete the entity from the datastore. We iterate through the extracted rooms id/key and attach to a new list variable all room list items where the room id is not equal to the room id that was passed into the method. Finally, the user entity is returned to the datastore. 

12) To retrieve rooms: This method takes in a user entity. Then all the room id are retrieved from the entity. Using a for loop, we iterate through the list of room ids, pass each one to the datastore, and then append the result to a list variable. We are then using the get_multi method of the datastore. We retrieve all the rooms and return the room list to the caller. 

13) Adding a room to a user: This method takes in an entity user variable and roomID. Add a  room ID  to the user list of room keys; then, return the entity to the datastore.  

14) To delete booking: This method takes two variables: the claims and the booking id. These variables are used to retrieve the booking entity key from the datastore and then delete the entity using the delete method in the datastore and the entity key.

15) To delete the bookings in the room: This method takes in two variables, such as the roomID, booking ID. Using the roomID, we retrieve the entity key. Then, the entity key is used to get the room entity. Afterward, we retrieve the booking_list from the user entity booking list. Then we iterate through the list and get the array where the booking id equals the booking id passed into the method. Then we delete the retrieved array from the booking list and update the entity booking with the updated booking list. Finally, we turn the entity to the datastore.

16) room list: 	This method takes in a list of rooms from a user. We use a nested loop to iterate through a list of rooms passed into the method. Then, we retrieve the booking list, get a list of variables, and store it in another dictionary list. Return the list to the caller. 












Page Return Handler methods:

1) addPageHandler: This method returns addRoom.html page.
2) bookingPageHandler: This method takes in an id and returns the booking.html page with the id. 
3) editBookingHandler: This method takes in the room id and booking id. It also has a variable used to store the user's email. Then using the user email and booking id, use the method to retrieve the booking and then return the editBooking.html along with the retrieved booking id, room id, and retrieved booking. 
4) ShowBookingHandler: This method takes in an id, which is used to retrieve the room. Then we get the user email booking and then return the showBooking.html along with the retrieved booking id, room id, and retrieved booking. 
5) manageRoomHandler: First, we check if the token is present and retrieve or create user detail. Afterward, we return the "myRoomList.html" page with the result gotten from retrieved Rooms. 
 

Main Methods:
1) root: Firstly, we retrieve the user token and store it in a variable. Then, we check if the token is present, then we try to get the claim and pass it into another method. This method will help retrieve the user's details if available or create it if it is not available. Next, we save the user email in a session variable for easy access. In addition, we query the database and retrieve all the available rooms. These are returned with the following variables: user_data, user details, and error. 

2) createRoomHander: Firstly, it takes in an id variable; it retrieves the user token and store it in a variable. Then, we check if the token is present, then we try to get the claim and pass it into another method. This method will help retrieve the user's details if available or create it if it is not available. Using the create Room method that takes in some variables, a new room is created. A notification message is sent to the user to show that the message has been passed. The user is redirected to the main page. 

3) deleteRoomHandler:  Firstly, it takes in a roomID variable; it retrieves the user token and store it in a variable. Then, we check if the token is present, then we try to get the claim and pass it into another method. This method will help retrieve the user's details if available or create it if it is not available. Using the retrieveRoom method, we get the room to be deleted. Then we check if the room to be deleted has a booking; if it does, then we flash a message to the user that this is not possible but if there is no booking in that room. Using the delete room method, we pass in the claims and id, then delete the room and notify the user that the room has been deleted. 

4) createBookingHander: Firstly, this takes in a roomID variable; it retrieves the user token and store it in a variable. Then, we check if the token is present, then we try to get the claim and pass it into another method. This method will help retrieve the user's details if available or create it if it is not available. Using the create new booking method, we pass in the attribute or value needed to create a booking. 
some conditions:
if the method returns -1, booking already exists in the datastore and is no longer available. A message will be flashed back to the user in that regard. However, if the method returns false, then the relevant variables will be passed into the addRoomToUser and addBookingsToRoom. 

5) edit_BookingHander: Firstly, this method takes in two variables: room ID and booking ID. It retrieves the user token and stores it in a variable. Then, we check if the token is present; if it is present, we try to get the claim and pass it into another method. This method will help retrieve the user's details if available or create it if it is not available. Using the isFound method, we check if the new values to be passed in for booking are available. If it true, then using the updated booking and update booking in room method, we will update the booking and sent a message to the user. 

6) delete_BookingHander:  Firstly, this method takes in two variables: room ID and booking ID. It retrieves the user token and stores it in a variable. Then, we check if the token is present; if it is present, we try to get the claim and pass it into another method. This method will help retrieve the user's details if available or create it if it is not available. Then using the delete booking and delete a booking in the room, the booking is deleted from the room. A message is flashed to the user.

7) showAllRoomHander: This method handles returning all the room for a particular user using the retrieveRooms method.

8) filter rooms: This returns booking id, and all information regarding that booking is retrieved and sent to the client-side.

9) dateHandler: This retrieves the start date and the end date from the client-side using the request method. Then, we check the retrieved rooms if there is a booking within the start date and end date. 




 





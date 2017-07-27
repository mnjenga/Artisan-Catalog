#Item Catalog  
This  is a map that displays technicians and artisans in Nairobi, Kenya with a their skill, Bio and a link to more details on the info display on clicking the marker.

The side bar displays a list of all the artisans and technicians and you can use the drop down on the top to filter to a specific category. Once you filter, icons on the map are filtered accordingly, and a search is on on the New York Times of articles that can help with the chosen category

The project uses Knockout js as the MVVM library which I import into the project by including a link from on of their Content Delivery Networks.

Further, the project utilises google maps api, and content from The New York Times.

Note: I have created all my projects incrementally and this is an upgrade to the item catalog by adding location capabilities to it. Below are installation instructions to run the project


#Installation

The project is written in python, using flask framework, sqlalchemy ORM, and sqlite database, while the front end uses Knockout js Library and google maps api

#Prerequisites

1) The application uses Linux-based virtual machine (VM)
2) Python 2.7 and above
3) sqlite database
4) The modules sqlalchemy, requests, oauth2client, wtforms and flask should be installed

#Installing and running

1) Download the catalog.zip file

2) Extract the catalog folder with its content and save it at the shared directory of your virtual machine

3) 1) Go to your terminal and navigate to the shared folder of your VM. Make sure your VM is up (eg for vigrant by running vagrant up, and you are conected eg by running vagrant ssh)

4) The folder already contains a database with sample data. If you wish to start a fresh, you can delete the .db file, then run python models.py from within the catalog directory from your VM on the terminal 

5) Then run python catalog.py from within catalog folder to run the website

6) Visit http://localhost:5000/ in your web browser to view the app.


#API Reference

The application has 3 JSON api end points that supply the same information available on the website version.

1) http://localhost:5000/api/v1/show/category for all categories

2) http://localhost:5000/api/v1/show/category_artisans/<int:cat_id> for all artisans in the category id cat_id

3) http://localhost:5000/api/v1/show/one_artisan/<int:art_id> artisan with the id cat_id with all the associated details


#Authors

Moses Njenga

Acknowledgments

1) Some Code snippets used from Google and Facebook oauth documentation as well the oauth implemetation on the udacity authentication flow course

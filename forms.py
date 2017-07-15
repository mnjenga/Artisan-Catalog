#!/usr/bin/env python3
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, IntegerField, validators, SelectField, TextAreaField, HiddenField

class CreateCategory(FlaskForm):
    name = StringField('Category Name', [validators.Length(min=4, max=25, message= "Category should be between 4 and 25 characters"),
                                    validators.InputRequired(message="Category Name is required")])
    
class CreateAddress(FlaskForm):
    kwetu_address = StringField('Alias', [validators.Regexp("^[a-zA-Z0-9_-]{3,12}$",flags=0,
                                                            message= "Alias should 3 and 12 characters without space"),
                                    validators.InputRequired(message="Alias is required")])
    building = StringField('Biulding', [validators.Length(min=4, max=25, message= "Biulding should be between 4 and 25 characters"),
                                    validators.InputRequired(message="Building Name is required")])
    floor = StringField('Floor', [validators.Length(min=1, max=25, message= "Floor should be between 1 and 25 characters"),
                                    validators.InputRequired(message="Floor is required")])
    house_no = StringField('House No', [validators.Length(min=1, max=25, message= "House No should be between 1 and 25 characters"),
                                    validators.InputRequired(message="House No. is required")])
    telephone = StringField('Telephone', [validators.Length(min=7, max=15, message= "Please enter a valid Phone Number"),
                                          validators.Regexp("^(\\(?\\d\\d\\d\\)?)( |-|\\.)?\\d\\d\\d( |-|\\.)?\\d{4,4}(( |-|\\.)?[ext\\.]+ ?\\d+)?$",
                                                                 flags=0, message="Please enter a valid Phone Number")])
    lat = StringField('Latitude', [validators.Length(min=9, max=25, message= "Please Click on the map for valid lat")])
    
    lng = StringField('Longitude', [validators.Length(min=9, max=25, message= "Please Click on the map for valid lng")])
    
class CreateArtisan(FlaskForm):
    name = StringField('Name', [validators.Length(min=4, max=25, message= "Name should be between 4 and 25 characters"),
                                    validators.InputRequired(message="Name is required")])
    category = SelectField(u'Categories', coerce=int)
    skill = StringField('Skill', [validators.Length(min=4, max=12, message= "Skill should be between 4 and 12 characters"),
                                    validators.InputRequired(message="Skill is required")])
    bio = StringField('Bio', [validators.Length(min=20, max=200, message= "Bio should be between 20 and 200 characters"),
                                    validators.InputRequired(message="Bio is required")])
    id_no = StringField('ID No', [validators.Regexp("^[0-9]{7,10}$",flags=0, message= "ID No. should be between 7 and 10 digits"),
                                    validators.InputRequired(message="ID No. Name is required")])

class CreatePortfolio(FlaskForm):
    title = StringField('Title', [validators.Length(min=4, max=65, message= "Title should be between 4 and 25 characters"),
                                    validators.InputRequired(message="Title is required")])
    details = TextAreaField('Details', [validators.Length(min=100, max=300, message= "Body should be between 100 and 300 characters"),
                                    validators.InputRequired(message="Details are required")])
    
class CreateEndorsement(FlaskForm):
    title = StringField('Title', [validators.Length(min=4, max=65, message= "Title should be between 4 and 25 characters"),
                                    validators.InputRequired(message="Title is required")])
    details = TextAreaField('Details', [validators.Length(min=100, max=300, message= "Body should be between 100 and 300 characters"),
                                    validators.InputRequired(message="Details are required")])
    art_id = HiddenField('art_id')
    
    
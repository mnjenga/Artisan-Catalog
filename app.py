#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
from flask import Flask, render_template, request, redirect
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import random
import string
from forms import CreateCategory, CreateAddress, CreateArtisan, CreatePortfolio

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
import httplib2
import json
from flask import make_response, url_for, flash, jsonify
import requests

catalog_engine = create_engine('sqlite:///mycatalog.db')

# create a configured "Session" class

Session = sessionmaker(bind=catalog_engine)

# create a Session

session = Session()

app = Flask(__name__)
app.secret_key = '121245llklert7763890sdDE4'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = 'Abigail'


# Displays all categories if there are, otherwise indicates there are none

@app.route('/')
@app.route('/home')
def home():
    categories = (session.query(Category))
    return render_template('location.html', cat=categories)


@app.route('/main')
def main():
    user_id = ''
    if 'username' in login_session:
        user_id = login_session['user_id']
    categories = session.query(Category)
    no_cats = ''
    if categories.first() is None:
        no_cats = 'There are no Categories to show'
    return render_template('home.html', categories=categories,
                           user_id=user_id, no_cats=no_cats)


# json api end point that returns all categories or an empty list if there
# are none

@app.route('/api/v1/show/category')
def api_category():
    categories = session.query(Category)
    return jsonify(categories=[c.serialize for c in categories])


# Allows to create categories if user is logged in, and ensures category
# name is not an empty string

@app.route('/create/category', methods=['GET', 'POST'])
def create_category():
    if 'username' in login_session:
        form = CreateCategory(request.form)
        if request.method == 'POST' and form.validate_on_submit():
            newCategory = Category(name=form.name.data,
                                   user=login_session['user_id'])
            session.add(newCategory)
            session.commit()
            flash('New Category added Successfully')
            return redirect(url_for('home'))
        return render_template('create-category.html', form=form)
    else:
        flash('Please Log in to add a Category')
        return redirect(url_for('show_login'))


# Editing a category after checking that the user is the creator

@app.route('/edit/category/<int:cat_id>', methods=['GET', 'POST'])
def edit_category(cat_id):
    editedCategory = \
        session.query(Category).filter_by(id=cat_id).first()
    if editedCategory:
        creator = getUserInfo(editedCategory.user)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            form = CreateCategory(request.form)
            if request.method == 'POST' and form.validate_on_submit():
                editedCategory.name = form.name.data
                session.add(editedCategory)
                session.commit()
                flash('The category has been updated successfuly')
                return redirect(url_for('home'))
            else:
                form.name.data = editedCategory.name
                return render_template(
                    'edit-category.html',
                    cat_id=cat_id,
                    c=editedCategory,
                    form=form)
        else:
            if 'username' in login_session:
                flash('You can only Edit entries you have created')
                return redirect(url_for('home'))
            else:
                flash('Please Log in to Edit Category')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Deleting a Category after confirming the user is the creator

@app.route('/delete/category/<int:cat_id>', methods=['GET', 'POST'])
def delete_category(cat_id):
    deleteCategory = \
        session.query(Category).filter_by(id=cat_id).first()
    if deleteCategory:
        creator = getUserInfo(deleteCategory.user)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST':
                session.delete(deleteCategory)
                session.commit()
                return redirect(url_for('home'))
            else:
                return render_template('delete-category.html',
                                       cat_id=cat_id, c=deleteCategory)
        else:
            if 'username' in login_session:
                flash('You can only Delete entries you have created')
                return redirect(url_for('home'))
            else:
                flash('Please Log in to Delete a Category')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Open a category and show the items in it

@app.route('/show/category/<int:cat_id>')
def artisan(cat_id):
    user_id = ''
    if 'username' in login_session:
        user_id = login_session['user_id']
    artisans = session.query(Artisan)
    categories = session.query(Category)
    cat = []
    no_art = ''
    for a in artisans:
        cat.append(a.category)
    if cat_id not in cat:
        no_art = 'No artisans to show in this category'

    return render_template(
        'artisan.html',
        artisans=artisans,
        c=categories,
        cat_id=cat_id,
        user_id=user_id,
        no_art=no_art,
    )


# Json api endpoint that returns all the times in a category

@app.route('/api/v1/show/category_artisans/<int:cat_id>')
def api_artisans(cat_id):
    artisans = session.query(Artisan).filter_by(category=cat_id)
    return jsonify(artisans=[a.serialize for a in artisans])


# Create an artisan, my item in a category, if user is logged in ensuring
# all values are not empty strings

@app.route('/create/artisan', methods=['GET', 'POST'])
def create_artisan():
    cat_id = request.args.get('cat_id', None)
    if 'username' in login_session:
        categories = session.query(Category)
        form = CreateArtisan(request.form)
        form.category.choices = [(c.id, c.name)
                                 for c in categories.order_by('name')]
        if request.method == 'POST' and form.validate_on_submit():
            cat_id = form.category.data
            newArtisan = Artisan(name=form.name.data,
                                 skill=form.skill.data,
                                 bio=form.bio.data,
                                 user=login_session['user_id'],
                                 category=form.category.data,
                                 id_no=form.id_no.data)
            session.add(newArtisan)
            session.commit()
            flash('The Artisan has been Added successfuly')
            return redirect(url_for('artisan', cat_id=cat_id))
        return render_template('create-artisan.html', c=categories,
                               cat_id=cat_id, form=form)
    else:
        flash('Please Log in to add a Artisan')
        return redirect(url_for('show_login'))


# Open an item (in my case an artisan) in a particular  category to show
# details, in my case his portfolio, addresses and endorsement

@app.route('/show/artisan/<int:art_id>', methods=['GET'])
def show_artisan(art_id):
    showArtisan = session.query(Artisan).filter_by(id=art_id).first()
    cat_id = request.args.get('cat_id', None)
    user_id = ''
    if 'username' in login_session:
        user_id = login_session['user_id']
    if showArtisan:
        portfolios = session.query(Portfolio).filter_by(artisan=art_id)
        no_port = ''
        if portfolios.first() is None:
            no_port = 'There are no Portfolios to show for ' \
                + showArtisan.name
        my_endorsements = \
            session.query(Endorsements).filter_by(artisan=art_id)
        no_end = ''
        if my_endorsements.first() is None:
            no_end = 'There is no endorsement to show for ' \
                + showArtisan.name
        addresses = session.query(Address).filter_by(artisan=art_id)
        no_add = ''
        if addresses.first() is None:
            no_add = 'There are no addresses to show for ' \
                + showArtisan.name
        categories = session.query(Category)
        return render_template(
            'show-artisan.html',
            a=showArtisan,
            p=portfolios,
            e=my_endorsements,
            add=addresses,
            c=categories,
            user_id=user_id,
            no_port=no_port,
            no_end=no_end,
            no_add=no_add,
        )
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Json api endpoint that returns a particular item in a category, in my
# case, an artisan with related details

@app.route('/api/v1/show/one_artisan/<int:art_id>')
def api_show_artisan(art_id):
    showArtisan = session.query(Artisan).filter_by(id=art_id).first()
    if showArtisan:
        portfolios = session.query(Portfolio).filter_by(artisan=art_id)
        my_endorsements = \
            session.query(Endorsements).filter_by(artisan=art_id)
        addresses = session.query(Address).filter_by(artisan=art_id)
        return jsonify(
            artisan=[
                showArtisan.serialize], Related_portfolio=[
                p.serialize for p in portfolios], Related_endorsement=[
                e.serialize for e in my_endorsements], Related_addresses=[
                    a.serialize for a in addresses])
    else:
        return jsonify('The entry requested was not found')


# Edit an artisan after confirming the user is the creator

@app.route('/edit/artisan/<int:art_id>', methods=['GET', 'POST'])
def edit_artisan(art_id):
    editedArtisan = session.query(Artisan).filter_by(id=art_id).first()
    cat_id = request.args.get('cat_id', None)
    categories = session.query(Category)
    form = CreateArtisan(request.form)
    form.category.choices = [(c.id, c.name)
                             for c in categories.order_by('name')]
    if editedArtisan:
        creator = getUserInfo(editedArtisan.user)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST' and form.validate_on_submit():
                cat_id = form.category.data
                editedArtisan.name = form.name.data
                editedArtisan.skill = form.skill.data
                editedArtisan.bio = form.bio.data
                editedArtisan.category = form.category.data
                editedArtisan.id_no = form.id_no.data
                session.add(editedArtisan)
                session.commit()
                flash('Artisan has been Updated Successfully')
                return redirect(url_for('artisan', cat_id=cat_id))
            else:
                form.name.data = editedArtisan.name
                form.skill.data = editedArtisan.skill
                form.bio.data = editedArtisan.bio
                form.id_no.data = editedArtisan.id_no
                return render_template(
                    'edit-artisan.html',
                    art_id=art_id,
                    a=editedArtisan,
                    c=categories, form=form)
        else:
            if 'username' in login_session:
                flash('You can Only Edit Artisans you Manage')
                return redirect(url_for('artisan', cat_id=cat_id))
            else:
                flash('Please log in to Edit this Artisan')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Delete an artisan after confirming the user is the  creator

@app.route('/delete/artisan/<int:art_id>', methods=['GET', 'POST'])
def delete_artisan(art_id):
    deleteArtisan = session.query(Artisan).filter_by(id=art_id).first()
    cat_id = request.args.get('cat_id', None)
    if deleteArtisan:
        creator = getUserInfo(deleteArtisan.user)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST':
                session.delete(deleteArtisan)
                session.commit()
                return redirect(url_for('artisan', cat_id=cat_id))
            else:
                return render_template('delete-artisan.html',
                                       art_id=art_id, a=deleteArtisan)
        else:
            if 'username' in login_session:
                flash('You can Only Delete Artisans you Manage')
                return redirect(url_for('artisan', cat_id=cat_id))
            else:
                flash('Please log in to Delete this Artisan')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Create a portfolio, part of Artisan Details attached to a specific
# artisan after confirming user is logged in and is the creator of the
# artisan

@app.route('/create/portfolio', methods=['GET', 'POST'])
def create_portfolio():
    art_id = request.args.get('art_id', None)
    art = session.query(Artisan).filter_by(id=art_id).first()
    form = CreatePortfolio(request.form)
    if art:
        creator = getUserInfo(art.user)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST' and form.validate_on_submit():
                newWork = Portfolio(title=form.title.data,
                                    details=form.details.data,
                                    artisan=request.args.get(
                                        'art_id',
                                        None),
                                    user=login_session['user_id'])
                session.add(newWork)
                session.commit()
                flash('Portfolio added Successfuly')
                return redirect(url_for('show_artisan',
                                        art_id=art_id))

            return render_template('portfolio.html', art_id=art_id, form=form)
        else:
            if 'username' in login_session:
                flash('You can Only create a protfolio in Artisans you manage'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Add Portfolio')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Edit a portfolio after confirming the user is the creator of the portfolio

@app.route('/edit/portfolio/<int:port_id>', methods=['GET', 'POST'])
def edit_portfolio(port_id):
    editedPortfolio = \
        session.query(Portfolio).filter_by(id=port_id).first()
    form = CreatePortfolio(request.form)
    if editedPortfolio:
        creator = getUserInfo(editedPortfolio.user)
        art_id = request.args.get('art_id', None)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST' and form.validate_on_submit():
                editedPortfolio.title = form.title.data
                editedPortfolio.details = form.details.data
                session.add(editedPortfolio)
                session.commit()
                flash('Portfolio Updated Successfuly')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                form.title.data = editedPortfolio.title
                form.details.data = editedPortfolio.details
                return render_template(
                    'edit-portfolio.html',
                    port_id=port_id,
                    p=editedPortfolio,
                    form=form)
        else:
            if 'username' in login_session:
                flash('You can Only edit a portfolio in Artisans you manage'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Edit Portfolio')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Delete a portfolio after confirming the user is the creator of the portfolio

@app.route('/delete/portfolio/<int:port_id>', methods=['GET', 'POST'])
def delete_portfolio(port_id):
    deletePortfolio = \
        session.query(Portfolio).filter_by(id=port_id).first()
    if deletePortfolio:
        creator = getUserInfo(deletePortfolio.user)
        art_id = request.args.get('art_id', None)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST':
                session.delete(deletePortfolio)
                session.commit()
                flash('Portfolio Deleted Successfuly')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                return render_template('delete-portfolio.html',
                                       port_id=port_id, p=deletePortfolio)
        else:
            if 'username' in login_session:
                flash('You can Only Delete a portfolio in Artisans you manage'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Delete Portfolio')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Create and endorsement, part of artisan details, after confirming the
# user is logged in and is not endorsing himself, ie he is not the creator
# of the artisan

@app.route('/create/endorsement', methods=['GET', 'POST'])
def create_endorsement():
    art_id = request.args.get('art_id', None)
    art = session.query(Artisan).filter_by(id=art_id).first()
    form = CreatePortfolio(request.form)
    if art:
        creator = getUserInfo(art.user)
        if 'username' in login_session and creator.id \
                != login_session['user_id']:
            if request.method == 'POST' and form.validate_on_submit():
                newEndorsement = Endorsements(title=form.title.data,
                                              details=form.details.data,
                                              artisan=request.args.get(
                                                  'art_id',
                                                  None),
                                              user=login_session['user_id'])
                session.add(newEndorsement)
                session.commit()
                flash('Endorsement Added Successfully')
                return redirect(url_for('show_artisan',
                                        art_id=art_id))

            return render_template(
                'endorsement.html', art_id=art_id, form=form)
        else:
            if 'username' in login_session:
                flash('You can not Endorse Artisans you Manage')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Add an Endorsement')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Editing an endorsement after confirming the user is the creator of the
# endorsement

@app.route('/edit/endorsement/<int:end_id>', methods=['GET', 'POST'])
def edit_endorsement(end_id):
    editedEndorsement = \
        session.query(Endorsements).filter_by(id=end_id).first()
    form = CreatePortfolio(request.form)
    if editedEndorsement:
        creator = getUserInfo(editedEndorsement.user)
        art_id = request.args.get('art_id', None)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST' and form.validate_on_submit():
                editedEndorsement.title = form.title.data
                editedEndorsement.details = form.details.data
                session.add(editedEndorsement)
                session.commit()
                flash('You have successfuly Endorsed this Artisan')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                form.title.data = editedEndorsement.title
                form.details.data = editedEndorsement.details
                return render_template(
                    'edit-endorsement.html',
                    end_id=end_id,
                    e=editedEndorsement,
                    form=form)
        else:
            if 'username' in login_session:
                flash('You can only edit Entries you have created')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Edit this Endorsement')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Deleting an endorsement after confirming the user is the creator of the
# endorsement

@app.route('/delete/endorsement/<int:end_id>', methods=['GET', 'POST'])
def delete_endorsement(end_id):
    deleteEndorsement = \
        session.query(Endorsements).filter_by(id=end_id).first()
    if deleteEndorsement:
        creator = getUserInfo(deleteEndorsement.user)
        art_id = request.args.get('art_id', None)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST':
                session.delete(deleteEndorsement)
                session.commit()
                flash('You have successfully deleted endorsement'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                return render_template('delete-endorsement.html',
                                       end_id=end_id, e=deleteEndorsement)
        else:
            if 'username' in login_session:
                flash('You can only Delete Entries you have created')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Delete this Endorsement')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Create address, part of Artisan details, after confirming the user is
# logged in and is the creator of the Artisan and validating user input

@app.route('/create/address', methods=['GET', 'POST'])
def create_address():
    art_id = request.args.get('art_id', None)
    art = session.query(Artisan).filter_by(id=art_id).first()
    if art:
        creator = getUserInfo(art.user)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            form = CreateAddress(request.form)
            if request.method == 'POST' and form.validate_on_submit():
                newAddress = Address(
                    kwetu_address=form.kwetu_address.data,
                    building=form.building.data,
                    floor=form.floor.data,
                    house_no=form.house_no.data,
                    telephone=form.telephone.data,
                    lat=form.lat.data,
                    lng=form.lng.data,
                    artisan=request.args.get(
                        'art_id',
                        None),
                    user=login_session['user_id'])
                session.add(newAddress)
                session.commit()
                flash('You have successfuly added a new Address')
                return redirect(url_for('show_artisan',
                                        art_id=art_id))
            return render_template('address.html', art_id=art_id, form=form)
        else:
            if 'username' in login_session:
                flash('You can only add addresses on Artisans you Manage'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to Add an Address')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Edit address after confirming the user is the creator of the address

@app.route('/edit/address/<int:add_id>', methods=['GET', 'POST'])
def edit_address(add_id):
    editedAddress = session.query(Address).filter_by(id=add_id).first()
    if editedAddress:
        creator = getUserInfo(editedAddress.user)
        art_id = request.args.get('art_id', None)
        form = CreateAddress(request.form)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST' and form.validate_on_submit():
                editedAddress.kwetu_address = form.kwetu_address.data
                editedAddress.building = form.building.data
                editedAddress.floor = form.floor.data
                editedAddress.house_no = form.house_no.data
                editedAddress.telephone = form.telephone.data
                editedAddress.lat = form.lat.data
                editedAddress.lng = form.lng.data
                session.add(editedAddress)
                session.commit()
                flash('You have successfuly updated Address')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                form.kwetu_address.data = editedAddress.kwetu_address
                form.building.data = editedAddress.building
                form.floor.data = editedAddress.floor
                form.house_no.data = editedAddress.house_no
                form.telephone.data = editedAddress.telephone
                form.lat.data = editedAddress.lat
                form.lng.data = editedAddress.lng
                return render_template(
                    'edit-address.html',
                    add_id=add_id,
                    a=editedAddress,
                    form=form)
        else:
            if 'username' in login_session:
                flash('You can only edit addresses on Artisans you Manage'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to edit an Address')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Delete an address after confirming the user is the creator of the address

@app.route('/delete/address/<int:add_id>', methods=['GET', 'POST'])
def delete_address(add_id):
    deleteAddress = session.query(Address).filter_by(id=add_id).first()
    if deleteAddress:
        creator = getUserInfo(deleteAddress.user)
        art_id = request.args.get('art_id', None)
        if 'username' in login_session and creator.id \
                == login_session['user_id']:
            if request.method == 'POST':
                session.delete(deleteAddress)
                session.commit()
                flash('You have successfuly deleted Address')
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                return render_template('delete-address.html',
                                       add_id=add_id, a=deleteAddress)
        else:
            if 'username' in login_session:
                flash('You can only delete addresses on Artisans you Manage'
                      )
                return redirect(url_for('show_artisan', art_id=art_id))
            else:
                flash('Please log in to delete an Address')
                return redirect(url_for('show_login'))
    else:
        flash('The Entry requested was not found')
        return redirect(url_for('home'))


# Render login page that displays Facebook and Google sign in passing
# state, unique string in the session

@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/loc', methods=['GET', 'POST'])
def loc():
    categories = (session.query(Category))
    cats = []
    for c in categories:
        cat = {"id": c.id, "name": c.name}
        cats.append(cat)

    my_artisans = (session.query(Artisan))
    my_addresses = (session.query(Address)
                    .join(Artisan, Artisan.id == Address.artisan))
    these_addresses = []
    for art in my_artisans:
        art_id = art.id
        for add in my_addresses:
            if art_id == add.artisan:
                grouped_address = {
                    "id": art.id,
                    "bio": art.bio,
                    "cat": art.category,
                    "name": art.name,
                    "skill": art.skill,
                    "lat": add.lat,
                    "lng": add.lng}
                these_addresses.append(grouped_address)
    return jsonify({'Addresses': these_addresses, 'Categories': cats})


# Define a function to create user to be used in the fb and google
# authentication

def createUser(login_session):
    newUser = Users(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email'
                                                              ]).one()
    return user.id


# Define a function to get a stored user by id

def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).first()
    return user


# Define function to get stored user by email

def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# Google Authentication

@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'
                                            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token's client ID does not match app's."
                                     ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'
                                     ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += \
        ' " style = "width: 300px; height: 300px;border-radius: 150px;\
        -webkit-border-radius:150px;-moz-border-radius: 150px;"> '
    flash('You are now logged in as %s' % login_session['username'])
    return output


# Define function to google sign off

def gdisconnect():
    access_token = login_session['credentials']
    if access_token is None:
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 405)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    app_id = json.loads(open('fb_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.9/me"
    # strip expire tag from access token
    token_dict = json.loads(result)
    token = token_dict['access_token']

    url = 'https://graph.facebook.com/v2.9/me?access_token=%s&fields=name,id,email' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.9/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
              -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("You are now logged in as %s" % login_session['username'])
    return output

# Logging off from facebook


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]


# Route to log out from both authentication providers

@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfuly logged out')
        return redirect(url_for('home'))
    else:
        flash('You were not logged in')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

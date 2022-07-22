#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from sre_parse import State
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, session, jsonify, abort
#from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import date
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
#moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    shows = db.relationship('Show', backref='venues', lazy=True)
    venues_genres = db.relationship('VenueGenre', backref='venues', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    shows = db.relationship('Show', backref='artists', lazy=True)
    artists_genres = db.relationship('ArtistGenre', backref='artists', lazy=True)

class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    state = db.Column(db.String(120))
    venue = db.relationship('Venue', backref='cities', lazy=True)
    artist = db.relationship('Artist', backref='cities', lazy=True)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime)

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    artists_genres = db.relationship('ArtistGenre', backref='genres', lazy=True)
    venues_genres = db.relationship('VenueGenre', backref='genres', lazy=True)

class ArtistGenre(db.Model):
    __tablename__ = 'artists_genres'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))

class VenueGenre(db.Model):
    __tablename__ = 'venues_genres'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))


db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Show all venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cities = City.query.order_by('id').all()
  
  for city in cities:
    city.city = city.name
    city.venues = Venue.query.filter_by(city_id=city.id).order_by('id').all()

    for venue in city.venues:
      venue.num_upcoming_shows = len(Show.query.filter_by(
        venue_id=venue.id
        ### TODO: fix this line
        #start_time > datetime.now().strftime('%Y-%m-%d%H:%M:%S')
      ).order_by('id').all())

  return render_template('pages/venues.html', areas=cities);

#  Search Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # shows the list of venues that matches the search term
  search_term = request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  response = {}
  response['count'] = len(venues)
  response['data'] = []

  for venue in venues:
    # TODO add date filter
    upcomingShows = len(Show.query.filter_by(venue_id=venue.id).all())

    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcomingShows
    })
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  Create selected Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first()

  venue.website = venue.website_link
  
  city = City.query.filter_by(id=venue.city_id).first()
  venue.city = city.name
  venue.state = city.state

  genres = VenueGenre.query.filter_by(venue_id=venue.id).all()
  venue.genres = []
  for genre in genres:
    venue.genres.append(Genre.query.filter_by(id = genre.genre_id).first().name)
  
  shows = Show.query.join('venues').filter_by(id = venue_id)

  # TODO: fix this
  pastShows = shows.filter_by(start_time < date.today).all()
  #pastShows = shows.all()

  venue.past_shows_count = len(pastShows)

  if (venue.past_shows_count > 0):
    venue.past_shows = []

    for show in pastShows:
      venue.past_shows.append({
        "artist_id": show.artists.id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": '2019-06-15T23:00:00.000Z'# TODO show.start_time
      })

  # TODO: fix this
  #upcomingShows = shows.filter_by(start_time > date.today).all()
  upcomingShows = shows.all()

  venue.upcoming_shows_count = len(upcomingShows)

  if (venue.upcoming_shows_count > 0):
    venue.upcoming_shows = []

    for show in upcomingShows:
      venue.upcoming_shows.append({
        "artist_id": show.artists.id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": '2019-06-15T23:00:00.000Z'# TODO show.start_time
      })


  return render_template('pages/show_venue.html', venue=venue)

#  Create a Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  cityCreated = False
  
  cityError = False
  venueError = False
  genreError = False
  
  if (len(City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).all()) > 0):
    city = City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).first()
    cityId = city.id
  else:
    try:
      city = City(name=request.form['city'],state=request.form['state'])
      db.session.add(city)
      db.session.commit()
      cityId = city.id
      cityCreated = True
    except:
      db.session.rollback()
      cityError=True
      print(sys.exc_info())
    finally:
      db.session.close()

  if (not cityError):
    try:
      if(request.form['seeking_talent'] == 'y'):
        seekingTalent = True
    except:
      seekingTalent = False
    
    seekingDescription = ''

    if (seekingTalent):
      seekingDescription = request.form['seeking_description']

    try:
      venue = Venue(
        name = request.form['name'],
        address = request.form['address'],
        phone = request.form['phone'],
        image_link = request.form['image_link'],
        facebook_link = request.form['facebook_link'],
        website_link = request.form['website_link'],
        seeking_talent = seekingTalent,
        seeking_description = seekingDescription,
        city_id = cityId
      )
      db.session.add(venue)
      db.session.commit()
      venueId = venue.id
    except:
      db.session.rollback()
      venueError=True
      print(sys.exc_info())
    finally:
      db.session.close()
      
  if (not venueError):
    try:
      genres = Genre.query.filter(Genre.name.in_(request.form.getlist('genres'))).all()
      for genre in genres:
        venueGenre = VenueGenre(
          venue_id = venueId,
          genre_id = genre.id
        )
        db.session.add(venueGenre)
      db.session.commit()
    except:
      db.session.rollback()
      genreError=True
      print(sys.exc_info())
    finally:
      db.session.close()
  
  if(genreError or venueError or cityError):
    if (cityError or venueError):
      if (cityCreated):
        City.query.filter_by(id=cityId).delete()
      if (venueError):
        Venue.query.filter_by(id=venueId).delete()
      db.session.commit()
      db.session.close()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  Updated a Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  
  city = City.query.filter_by(id=venue.city_id).first()

  genres = VenueGenre.query.filter_by(venue_id=venue.id).all()
  venue.genres = []
  for genre in genres:
    venue.genres.append(Genre.query.filter_by(id = genre.genre_id).first().name)

  form = VenueForm(
    name=venue.name,
    city=city.name,
    state=city.state,
    address=venue.address,
    phone=venue.phone,
    genres=venue.genres,
    facebook_link=venue.facebook_link,
    image_link=venue.image_link,
    website_link=venue.website_link,
    seeking_description=venue.seeking_description
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  cityCreated = False
  
  cityError = False
  venueError = False
  genreError = False

  venue = Venue.query.filter_by(id=venue_id).first()

  currentCity = City.query.filter_by(id=venue.city_id).first()

  if (currentCity.name != request.form['city'] or currentCity.state != request.form['state']):
    if (len(City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).all()) > 0):
      city = City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).first()
      cityId = city.id
    else:
      try:
        city = City(name=request.form['city'],state=request.form['state'])
        db.session.add(city)
        db.session.commit()
        cityId = city.id
        cityCreated = True
      except:
        db.session.rollback()
        cityError=True
        print(sys.exc_info())

  if (not cityError):
    try:
      VenueGenre.query.filter_by(venue_id=venue_id).delete()
      genres = Genre.query.filter(Genre.name.in_(request.form.getlist('genres'))).all()
      for genre in genres:
        venueGenre = VenueGenre(
          venue_id = venue_id,
          genre_id = genre.id
        )
        db.session.add(venueGenre)
      db.session.commit()
    except:
      db.session.rollback()
      genreError=True
      print(sys.exc_info())

  if (not cityError and not genreError):
    try:
      venue.name = request.form['name']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      venue.facebook_link = request.form['facebook_link']
      venue.image_link = request.form['image_link']
      venue.website_link = request.form['website_link']
      venue.seeking_description = request.form['seeking_description']
      try:
        if(request.form['seeking_talent'] == 'y'):
          venue.seeking_talent = True
      except:
        venue.seeking_talent = False
      if(cityCreated):
        venue.city_id = cityId
      db.session.commit()
    except:
      db.session.rollback()
      venueError=True
      print(sys.exc_info())
    finally:
      db.session.close()

  if(venueError or cityError or genreError):
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    # on successful db insert, flash success
    flash('This venue was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete a Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  
  try:
      Show.query.filter_by(venue_id=venue_id).delete()
      VenueGenre.query.filter_by(venue_id=venue_id).delete()
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()
  
  if (not error):
      return jsonify({ 'success': True })
  else:
      abort(400)

#  Show all artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # shows the list of artists that matches the search term
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  response = {}
  response['count'] = len(artists)
  response['data'] = []

  for artist in artists:
    # TODO add date filter
    upcomingShows = len(Show.query.filter_by(artist_id=artist.id).all())

    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": upcomingShows
    })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Show an artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id 
  artist = Artist.query.filter_by(id=artist_id).first()

  artist.website = artist.website_link

  city = City.query.filter_by(id=artist.city_id).first()
  artist.city = city.name
  artist.state = city.state

  genres = ArtistGenre.query.filter_by(artist_id=artist.id).all()
  artist.genres = []
  for genre in genres:
    artist.genres.append(Genre.query.filter_by(id = genre.genre_id).first().name)
  
  shows = Show.query.join('artists').filter_by(id = artist_id)
  
  # TODO: fix this
  #pastShows = shows.filter_by(start_time < date.today).all()
  pastShows = shows.all()

  artist.past_shows_count = len(pastShows)

  if (artist.past_shows_count > 0):
    artist.past_shows = []

    for show in pastShows:
      artist.past_shows.append({
        "venue_id": show.venues.id,
        "venue_name": show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": '2019-06-15T23:00:00.000Z'# TODO show.start_time
      })
  
  # TODO: fix this
  #upcomingShows = shows.filter_by(start_time > date.today).all()
  upcomingShows = shows.all()

  artist.upcoming_shows_count = len(upcomingShows)

  if (artist.upcoming_shows_count > 0):
    artist.upcoming_shows = []

    for show in upcomingShows:
      artist.upcoming_shows.append({
        "venue_id": show.venues.id,
        "venue_name": show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": '2019-06-15T23:00:00.000Z'# TODO show.start_time
      })

  return render_template('pages/show_artist.html', artist=artist)

#  Update a artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # shows the artist page with the given artist_id 
  artist = Artist.query.filter_by(id=artist_id).first()

  city = City.query.filter_by(id=artist.city_id).first()

  genres = ArtistGenre.query.filter_by(artist_id=artist.id).all()
  artist.genres = []
  for genre in genres:
    artist.genres.append(Genre.query.filter_by(id = genre.genre_id).first().name)

  form = ArtistForm(
    name=artist.name,
    city=city.name,
    state=city.state,
    phone=artist.phone,
    genres=artist.genres,
    facebook_link=artist.facebook_link,
    image_link=artist.image_link,
    website_link=artist.website_link,
    seeking_description=artist.seeking_description
  )
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):  
  cityCreated = False
  
  cityError = False
  artistError = False
  genreError = False

  artist = Artist.query.filter_by(id=artist_id).first()

  currentCity = City.query.filter_by(id=artist.city_id).first()

  if (currentCity.name != request.form['city'] or currentCity.state != request.form['state']):
    if (len(City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).all()) > 0):
      city = City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).first()
      cityId = city.id
    else:
      try:
        city = City(name=request.form['city'],state=request.form['state'])
        db.session.add(city)
        db.session.commit()
        cityId = city.id
        cityCreated = True
      except:
        db.session.rollback()
        cityError=True
        print(sys.exc_info())
  
  if (not cityError):
    try:
      ArtistGenre.query.filter_by(artist_id=artist_id).delete()
      genres = Genre.query.filter(Genre.name.in_(request.form.getlist('genres'))).all()
      for genre in genres:
        artistGenre = ArtistGenre(
          artist_id = artist_id,
          genre_id = genre.id
        )
        db.session.add(artistGenre)
      db.session.commit()
    except:
      db.session.rollback()
      genreError=True
      print(sys.exc_info())
      
  if (not cityError and not genreError):
    try:
      artist.name = request.form['name']
      artist.phone = request.form['phone']
      artist.facebook_link = request.form['facebook_link']
      artist.image_link = request.form['image_link']
      artist.website_link = request.form['website_link']
      artist.seeking_description = request.form['seeking_description']
      try:
        if(request.form['seeking_venue'] == 'y'):
          artist.seeking_venue = True
      except:
        artist.seeking_venue = False
      if(cityCreated):
        artist.city_id = cityId
      db.session.commit()
    except:
      db.session.rollback()
      artistError=True
      print(sys.exc_info())
    finally:
      db.session.close()
      
  if(artistError or cityError or genreError):
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    # on successful db insert, flash success
    flash('This artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create a artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  cityCreated = False

  cityError = False
  artistError = False
  genreError = False
  
  if (len(City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).all()) > 0):
    city = City.query.filter(City.name.ilike('%' + request.form['city'] + '%')).first()
    cityId = city.id
  else:
    try:
      city = City(name=request.form['city'],state=request.form['state'])
      db.session.add(city)
      db.session.commit()
      cityId = city.id
      cityCreated = True
    except:
      db.session.rollback()
      cityError=True
      print(sys.exc_info())
    finally:
      db.session.close()

  if (not cityError):
    try:
      if(request.form['seeking_venue'] == 'y'):
        seekingVenue = True
    except:
      seekingVenue = False
    
    seekingDescription = ''

    if (seekingVenue):
      seekingDescription = request.form['seeking_description']

    try:
      artist = Artist(
        name = request.form['name'],
        phone = request.form['phone'],
        image_link = request.form['image_link'],
        facebook_link = request.form['facebook_link'],
        website_link = request.form['website_link'],
        seeking_venue = seekingVenue,
        seeking_description = seekingDescription,
        city_id = cityId
      )
      db.session.add(artist)
      db.session.commit()
      artistId = artist.id
    except:
      db.session.rollback()
      artistError=True
      print(sys.exc_info())
    finally:
      db.session.close()
      
  if (not artistError):
    try:
      genres = Genre.query.filter(Genre.name.in_(request.form.getlist('genres'))).all()
      for genre in genres:
        artistGenre = ArtistGenre(
          artist_id = artistId,
          genre_id = genre.id
        )
        db.session.add(artistGenre)
      db.session.commit()
    except:
      db.session.rollback()
      genreError=True
      print(sys.exc_info())
    finally:
      db.session.close()
  
  if(genreError or artistError or cityError):
    if (cityError or artistError):
      if (cityCreated):
        City.query.filter_by(id=cityId).delete()
      if (artistError):
        Artist.query.filter_by(id=artistId).delete()
      db.session.commit()
      db.session.close()

    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  Delete a artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  
  try:
      Show.query.filter_by(artist_id=artist_id).delete()
      ArtistGenre.query.filter_by(artist_id=artist_id).delete()
      Artist.query.filter_by(id=artist_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()
  
  if (not error):
      return jsonify({ 'success': True })
  else:
      abort(400)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  query = Show.query.join('artists').join('venues').all()
  
  data = []
  
  for row in query:
    data.append({
      "venue_id": row.venues.id,
      "venue_name": row.venues.name,
      "artist_id": row.artists.id,
      "artist_name": row.artists.name,
      "artist_image_link": row.artists.image_link,
      "start_time": row.start_time.strftime("%m-%d-%Y %H:%M:%S")
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form  
  artistError = False
  venueError = False
  showError = False

  artistId = None
  venueId = None

  try:
    artistId = Artist.query.filter_by(id=request.form['artist_id']).first().id
  except:
    artistError = True

  try:
    venueId = Venue.query.filter_by(id=request.form['venue_id']).first().id
  except:
    venueError = True
  
  if (artistError):
    flash('An error occurred. Artist not found.')
  if (venueError):
    flash('An error occurred. Venue not found.')
  
  if (not artistError and not venueError):
    print(request.form['start_time'])
    try:
      show = Show(
        artist_id = artistId,
        venue_id = venueId,
        start_time = request.form['start_time']
      )
      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
      showError=True
      print(sys.exc_info())
    finally:
      db.session.close()

  if (showError):
    flash('An error occurred. Show could not be listed.')
  elif (not showError and not artistError and not venueError):
    flash('Show was successfully listed!')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
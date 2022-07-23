from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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

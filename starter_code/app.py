#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import desc

#from flask_wtf.csrf import CSRFProtect
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
#csrf = CSRFProtect()
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#csrf.init_app(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#i chose many to many relationship between genre and artist and venue
# and one to many between show and artist and venue
#added missing fields
venueGenres = db.Table('venueGenres',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)
artistGenres = db.Table('artistGenres',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)
class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship('Genre', secondary=venueGenres,
      backref=db.backref('Venue', lazy=True))
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)
    genres = db.relationship('Genre', secondary=artistGenres,
      backref=db.backref('Artist', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime())

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
# a list of genres and to get their id without sending a request to the db
genreDict={
            1:'Alternative' ,
            2: 'Blues' ,
            3: 'Classical' ,
            4: 'Country' ,
            5: 'Electronic' ,
            6: 'Folk' ,
            7: 'Funk' ,
            8: 'Hip-Hop' ,
            9: 'Heavy Metal' ,
            10:'Instrumental' ,
            11: 'Jazz' ,
            12: 'Musical Theatre' ,
            13: 'Pop' ,
            14: 'Punk' ,
            15: 'R&B' ,
            16: 'Reggae' ,
            17: 'Rock n Roll' ,
            18: 'Soul' ,
            19: 'Other' 
}

def getKeys(dictOfElements, values):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
      for value in values:      
        if item[1] == value:
            listOfKeys.append(item[0])    
    return  listOfKeys


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  #get a list of unique city/state
  venues_in = Venue.query.all()
  city_list = Venue.query.distinct(Venue.city, Venue.state).order_by(desc(Venue.state))
  current_time = datetime.now() 
  #loop over locations and check if a venue had an upcoming show and add to the list
  for locat in city_list:
    venues_filterd = []
    for venue in venues_in:   
      if(venue.city == locat.city) and (venue.state == locat.state):
        num_upcoming_show = 0
        venueShows = Show.query.filter_by(venue_id=venue.id).all()
        for show in venueShows:
          if show.start_time > current_time:
            num_upcoming_show += 1

        venues_filterd.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_show
        })
    #after that i just append it to the data list    
    data.append({
      "city": locat.city,
      "state": locat.state,
      "venues": venues_filterd
    })  
        
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  search_term = request.form.get('search_term').strip()
  #i filter out the list of venues using the input and match in any position and is case insensitive
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  for venue in venues:
     data.append({
            "id": venue.id,
            "name": venue.name,
        })
  response = {
        "count": len(venues),
        "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #i get the venue data for db
  venue_in = Venue.query.get(venue_id)
  #i check if the db returned a value or none and send and error if it wasn't found
  if not venue_in:
    flash('An error occurred. the venue that was requested was not found.')
    return redirect(url_for('create_venue_submission')) 
  else:
    #i prepare empty list to fill them up
    genres = []
    current_time = datetime.now()
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0  
    #convert the genre into a list
    for genre in venue_in.genres:
      genres.append(genre.name)
    #list of shows and a count of past and upcoming shows
    for show in venue_in.shows:
      if show.start_time >= current_time:
        upcoming_shows_count += 1
        upcoming_shows.append({
          "artist_id":show.artist_id,
          "artist_name":show.artist.name,
          "start_time":format_datetime(str(show.start_time)),
          "artist_image_link":show.artist.image_link
        })
      elif show.start_time < current_time:
        past_shows_count += 1
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "start_time": format_datetime(str(show.start_time)),
          "artist_image_link": show.artist.image_link
        })  
    data = {
            "id": venue_in.id,
            "name": venue_in.name,
            "city": venue_in.city,
            "state": venue_in.state,          
            "address": venue_in.address,
            "phone": venue_in.phone,
            "image_link": venue_in.image_link,
            "facebook_link": venue_in.facebook_link,
            "website": venue_in.website,
            "seeking_talent": venue_in.seeking_talent,
            "seeking_description": venue_in.seeking_description,
            "genres": genres,
            "past_shows": past_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count          
    }  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  #i get the data from the form 
    form = VenueForm()
    name = request.form.get('name').strip()
    city = request.form.get('city').strip()
    state = request.form.get('state').strip()
    address = request.form.get('address').strip()
    phone = request.form.get('phone').strip()
    image_link = request.form.get('image_link').strip()
    facebook_link = request.form.get('facebook_link').strip()
    website = request.form.get('website').strip()
    # i convert the input into a bool
    if request.form.get('seeking_talent') == 'yes':
      seeking_talent = True
    elif request.form.get('seeking_talent') == 'no':
      seeking_talent = False  
    seeking_description = request.form.get('seeking_description').strip()
    #get a list of ids of genres from the dict i put above
    genres = getKeys(genreDict,request.form.getlist('genres'))
    #check if the form is vaild and if not the flash the error of missing or wrong fields
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_venue_submission'))
  
    else:
      #
        try: 
          #i add all the data to db as new entry
            new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
                  image_link=image_link,facebook_link=facebook_link,website=website, \
                  seeking_talent=seeking_talent, seeking_description=seeking_description)
            #here i check for genres id's if they exist in the db if not i add them      
            for genre in genres: 
              genre_in = Genre.query.filter_by(id = genre).one_or_none()
              if genre_in:
                new_venue.genres.append(genre_in)
              else:
                new_genre = Genre(name=genreDict[genre])
                db.session.add(new_genre)
                new_venue.genres.append(new_genre)
            db.session.add(new_venue)
            db.session.commit()
            flash( request.form['name'] + ' was successfully listed!')
            

        except Exception as e:
            err = True
            print(f'Exception "{e}"  in creating a new venue')
            db.session.rollback()
            flash('An error occurred.' + request.form['name'] + ' was unsuccessfully listed please retry.')
            return redirect(url_for('create_venue_submission'))  
        finally:
            db.session.close()        
            return render_template('pages/home.html')
        
            

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #check if there is a record to delete if not redirect to home page
  venue = Venue.query.get(venue_id)
  if not venue:
    flash('Does not exsit.')
    return redirect(url_for('index'))
  else:
    venueName= venue.name
    try:
      db.session.delete(venue)
      db.session.commit()
    except:
        db.session.rollback()
        flash(f' error occurred while deleting venue {venue_name}.')
    finally:
        db.session.close()
        flash(f'Successfully deleted {venue_name}')
        return render_template('pages/home.html')



  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()  
    
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  #the same code as search_venue
  data = []
  search_term = request.form.get('search_term').strip()
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  for artist in artists:
     data.append({
            "id": artist.id,
            "name": artist.name,
        })
  response = {
        "count": len(artists),
        "data": data
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #same code as show_venue
  artist_in = Artist.query.get(artist_id)
  if not artist_in:
    flash('An error occurred. the artist that was requested was not found.')
    return redirect(url_for('create_artist_submission')) 
  else:
    genres = []
    current_time = datetime.now()
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0  
    for genre in artist_in.genres:
      genres.append(genre.name)

    for show in artist_in.shows:
      if show.start_time >= current_time:
        upcoming_shows_count += 1
        upcoming_shows.append({
          "artist_id":show.artist_id,
          "artist_name":show.artist.name,
          "start_time":format_datetime(str(show.start_time)),
          "artist_image_link":show.artist.image_link
        })
      elif show.start_time < current_time:
        past_shows_count += 1
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "start_time": format_datetime(str(show.start_time)),
          "artist_image_link": show.artist.image_link
        })  
    data = {
            "id": artist_in.id,
            "name": artist_in.name,
            "city": artist_in.city,
            "state": artist_in.state,          
            "phone": artist_in.phone,
            "image_link": artist_in.image_link,
            "facebook_link": artist_in.facebook_link,
            "website": artist_in.website,
            "seeking_venue": artist_in.seeking_venue,
            "seeking_description": artist_in.seeking_description,
            "genres": genres,
            "past_shows": past_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count          
    }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  genres = []
  # i get the requested record and if it doesn't exist i redirect to create a new artist page
  artist_in = Artist.query.get(artist_id)
  if not artist_in:
    flash('An error occurred. the artist that was requested was not found.')
    return redirect(url_for('create_artist_submission')) 
  else:
    form = ArtistForm(obj=artist_in)
    #i loop over to convert into a list 
    for genre in artist_in.genres:
        genres.append(genre.name)

    artist = {
             "id": artist_in.id,
            "name": artist_in.name,
            "city": artist_in.city,
            "state": artist_in.state,          
            "phone": artist_in.phone,
            "image_link": artist_in.image_link,
            "facebook_link": artist_in.facebook_link,
            "website": artist_in.website,
            "seeking_venue": artist_in.seeking_venue,
            "seeking_description": artist_in.seeking_description,
            "genres": genres         
      }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #same code from create_venue execpt i empty the genre of the artist and fill it with the new data
  form = ArtistForm()
  name = request.form.get('name').strip()
  city = request.form.get('city').strip()
  state = request.form.get('state').strip()
  phone = request.form.get('phone').strip()
  image_link = request.form.get('image_link').strip()
  facebook_link = request.form.get('facebook_link').strip()
  website = request.form.get('website').strip()
  if request.form.get('seeking_venue') == 'yes':
    seeking_venue = True
  elif request.form.get('seeking_venue') == 'no':
    seeking_venue = False  
  seeking_description = request.form.get('seeking_description').strip()
  genres = getKeys(genreDict,request.form.getlist('genres'))
  if not form.validate():
      flash( form.errors )
      return redirect(url_for('edit_artist_submission', artist_id=artist_id))
  
  else:
      #
      try: 
          edit_artist = Artist.query.get(artist_id)
          #here i empty the genres 
          edit_artist.genres = []
          db.session.commit()
          edit_artist.name=name
          edit_artist.city=city
          edit_artist.state=state
          edit_artist.phone=phone
          edit_artist.image_link=image_link
          edit_artist.facebook_link=facebook_link
          edit_artist.website=website
          edit_artist.seeking_venue=seeking_venue
          edit_artist.seeking_description=seeking_description

          for genre in genres: 
            genre_in = Genre.query.filter_by(id = genre).one_or_none()
            if genre_in:
              edit_artist.genres.append(genre_in)
            else:
              new_genre = Genre(name=genreDict[genre])
              db.session.add(new_genre)
              edit_artist.genres.append(new_genre)  

          db.session.commit()
            

      except Exception as e:
          db.session.rollback()
          flash('An error occurred. Artist ' + request.form['name'] + ' was unsuccessfully listed please retry.')
          return redirect(url_for('edit_artist_submission', artist_id=artist_id))  
      finally:
          db.session.close()
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
          return redirect(url_for('show_artist', artist_id=artist_id))

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  #same as edit artist
  genres = []
  venue_in = Venue.query.get(venue_id)
  if not venue_in:
    flash('An error occurred. the venue that was requested was not found.')
    return redirect(url_for('create_venue_submission')) 
  else:
    form = VenueForm(obj=venue_in)
    for genre in venue_in.genres:
        genres.append(genre.name)

    venue = {
             "id": venue_in.id,
            "name": venue_in.name,
            "city": venue_in.city,
            "state": venue_in.state,          
            "address": venue_in.address,
            "phone": venue_in.phone,
            "image_link": venue_in.image_link,
            "facebook_link": venue_in.facebook_link,
            "website": venue_in.website,
            "seeking_talent": venue_in.seeking_talent,
            "seeking_description": venue_in.seeking_description,
            "genres": genres         
      }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  #same as edit_artist
  form = VenueForm()
  name = request.form.get('name').strip()
  city = request.form.get('city').strip()
  state = request.form.get('state').strip()
  address = request.form.get('address').strip()
  phone = request.form.get('phone').strip()
  image_link = request.form.get('image_link').strip()
  facebook_link = request.form.get('facebook_link').strip()
  website = request.form.get('website').strip()
  if request.form.get('seeking_talent') == 'yes':
    seeking_talent = True
  elif request.form.get('seeking_talent') == 'no':
    seeking_talent = False  
  seeking_description = request.form.get('seeking_description').strip()
  genres = getKeys(genreDict,request.form.getlist('genres'))
  if not form.validate():
      flash( form.errors )
      return redirect(url_for('edit_venue_submission', venue_id=venue_id))
  
  else:
    #
      try:

          edit_venue = Venue.query.get(venue_id)    
          edit_venue.genres = []
          db.session.commit()
          edit_venue.name=name
          edit_venue.city=city
          edit_venue.state=state
          edit_venue.address=address
          edit_venue.phone=phone
          edit_venue.image_link=image_link
          edit_venue.facebook_link=facebook_link
          edit_venue.website=website,
          edit_venue.seeking_talent=seeking_talent
          edit_venue.seeking_description=seeking_description        
           
          for genre in genres: 
            genre_in = Genre.query.filter_by(id = genre).one_or_none()
            if genre_in:
              edit_venue.genres.append(genre_in)
            
          db.session.commit()
          flash( request.form['name'] + ' was successfully updated!')           
      except Exception as e:
            err = True
            print(f'there was an error-> Exception "{e}"  in updating a new venue')
            db.session.rollback()
            flash('An error occurred. '+ request.form['name'] + ' was unsuccessfully updated please retry.')
            return redirect(url_for('edit_venue_submission', venue_id=venue_id))  
      finally:
            db.session.close()        
            return redirect(url_for('show_venue', venue_id=venue_id))



 

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  #same as venue_create

    form = ArtistForm()
    name = request.form.get('name').strip()
    city = request.form.get('city').strip()
    state = request.form.get('state').strip()
    phone = request.form.get('phone').strip()
    image_link = request.form.get('image_link').strip()
    facebook_link = request.form.get('facebook_link').strip()
    website = request.form.get('website').strip()
    if request.form.get('seeking_venue') == 'yes':
      seeking_venue = True
    elif request.form.get('seeking_venue') == 'no':
      seeking_venue = False  
    seeking_description = request.form.get('seeking_description').strip()
    genres = getKeys(genreDict,request.form.getlist('genres'))
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_artist_submission'))
  
    else:
      #
        try: 
            new_artist = Artist(name=name, city=city, state=state, phone=phone, \
                  image_link=image_link,facebook_link=facebook_link,website=website, \
                  seeking_venue=seeking_venue, seeking_description=seeking_description)
            for genre in genres: 
              genre_in = Genre.query.filter_by(id = genre).one_or_none()
              if genre_in:
                new_artist.genres.append(genre_in)
              else:
                new_genre = Genre(name=genreDict[genre])
                db.session.add(new_genre)
                new_artist.genres.append(new_genre)  

            db.session.add(new_artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')

        except Exception as e:          
            print(f'Exception "{e}"  in creating a new artist')
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' was unsuccessfully listed please retry.')
            return redirect(url_for('create_artist_submission'))  
        finally:
            db.session.close()
                   

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
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
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  try:
    new_show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. The Show was unsuccessfully listed please retry.')
    return redirect(url_for('create_show_submission'))
  finally:
    db.session.close()  


  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

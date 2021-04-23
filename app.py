from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from base64 import b64encode


#APP

API_URL = 'https://tarea2-cross3.herokuapp.com'


flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:ross1963@localhost/iic3103_tarea2'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

# TABLES

db = SQLAlchemy(flask_app)
ma = Marshmallow(flask_app)


def get_id(name, parent_id=None):
  if parent_id:
    string = "%s:%s" % (name, parent_id)
  else:
    string = name
  id = b64encode(string.encode()).decode('utf-8')
  return id[:22]


class ArtistSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'age', 'albums', 'tracks', 'self_url')


class AlbumSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'genre', 'artist', 'tracks', 'self_url')


class TrackSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'duration', 'times_played', 'artist', 'album', 'self_url')


artist_schema = ArtistSchema()
artists_schema = ArtistSchema(many=True)

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)

track_schema = TrackSchema()
tracks_schema = TrackSchema(many=True)


class Artist(db.Model):
  id = db.Column(db.String(22), primary_key=True)
  name = db.Column(db.String(50))
  age = db.Column(db.Integer)
  albums = db.Column(db.String(200))
  tracks = db.Column(db.String(200))
  self_url = db.Column(db.String(200))

  def __init__(self, name, age):
    self.id = get_id(name) 
    self.name = name
    self.age = int(age)
    self.albums = "%s/artists/%s/albums" % (API_URL, self.id)
    self.tracks = "%s/artists/%s/tracks" % (API_URL, self.id)
    self.self_url = "%s/artists/%s" % (API_URL, self.id)

class Album(db.Model):
  id = db.Column(db.String(22), primary_key=True)
  name = db.Column(db.String(50))
  genre = db.Column(db.String(50))
  artist = db.Column(db.String(200))
  tracks = db.Column(db.String(200))
  self_url = db.Column(db.String(200))

  def __init__(self, name, genre, artist_id):
    self.id = get_id(name, artist_id)
    self.name = name
    self.genre = genre
    self.artist = "%s/artists/%s" % (API_URL, artist_id)
    self.tracks = "%s/albums/%s/tracks" % (API_URL, self.id)
    self.self_url = "%s/albums/%s" % (API_URL, self.id)


class Track(db.Model):
  id = db.Column(db.String(22), primary_key=True)
  name = db.Column(db.String(50))
  duration = db.Column(db.Float)
  times_played = db.Column(db.Integer)
  artist = db.Column(db.String(200))
  album = db.Column(db.String(200))
  self_url = db.Column(db.String(200))

  def __init__(self, name, duration, album_id):
    self.id = get_id(name, album_id)
    self.name = name
    self.duration = float(duration)
    self.times_played = 0
    self.artist = Album.query.get(album_id).artist
    self.album = "%s/albums/%s" % (API_URL, album_id)
    self.self_url = "%s/tracks/%s" % (API_URL, self.id)


db.create_all()


# ROUTES
@flask_app.route('/', methods=['GET'])
def hello():
  response = {"Title": "Tarea 2 de Taller de Integración", "Author": "Clemente Ross"}
  return jsonify(response), 200

# GET

# ARTISTS
@flask_app.route('/artists', methods=['GET'])
def get_all_artists():
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_artists = Artist.query.all()
  result = artists_schema.dump(all_artists)
  
  return artists_schema.jsonify(result), 200

@flask_app.route('/artists/<artist_id>', methods=['GET'])
def get_artist_by_id(artist_id):
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  artist = Artist.query.get(artist_id)

  return artist_schema.jsonify(artist), 200

@flask_app.route('/artists/<artist_id>/albums', methods=['GET'])
def get_albums_by_artist_id(artist_id):
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_albums = Album.query.all()
  albums_filter = [album for album in all_albums if '%s/artists/%s' % (API_URL, artist_id) == album.artist]
  result = albums_schema.dump(albums_filter)

  return albums_schema.jsonify(result), 200

@flask_app.route('/artists/<artist_id>/tracks', methods=['GET'])
def get_tracks_by_artist_id(artist_id):
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/artists/%s' % (API_URL, artist_id) == track.artist]
  result = tracks_schema.dump(tracks_filter)

  return tracks_schema.jsonify(result), 200

# ALBUMS
@flask_app.route('/albums', methods=['GET'])
def get_all_albums():
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_albums = Album.query.all()
  result = albums_schema.dump(all_albums)

  return albums_schema.jsonify(result), 200

@flask_app.route('/albums/<album_id>', methods=['GET'])
def get_album_by_id(album_id):
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  album = Album.query.get(album_id)

  return album_schema.jsonify(album), 200

@flask_app.route('/albums/<album_id>/tracks', methods=['GET'])
def get_tracks_by_album_id(album_id):
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/albums/%s' % (API_URL, album_id) == track.album]
  result = tracks_schema.dump(tracks_filter)

  return tracks_schema.jsonify(result), 200

# TRACKS
@flask_app.route('/tracks', methods=['GET'])
def get_all_tracks():
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_tracks = Track.query.all()
  result = tracks_schema.dump(all_tracks)

  return tracks_schema.jsonify(result), 200

@flask_app.route('/tracks/<track_id>', methods=['GET'])
def get_track_by_id(track_id):
  if request.method != 'GET':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  track = Track.query.get(track_id)

  return track_schema.jsonify(track), 200


# POST

# ARTIST
@flask_app.route('/artists', methods=['POST'])
def create_artist():
  if request.method != 'POST':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  try:
    name = request.json['name']
    age = request.json['age']
    new_artist = Artist(name, age)
  except:
    response = {"Error message": "Bad Request"}
    return jsonify(response), 400

  all_artists = Artist.query.all()
  for artist in all_artists:
    if artist.id == new_artist.id:
      return artist_schema.jsonify(artist), 409
  
  db.session.add(new_artist)
  db.session.commit()

  return artist_schema.jsonify(new_artist), 201

# ALBUM
@flask_app.route('/artists/<artist_id>/albums', methods=['POST'])
def create_album(artist_id):
  if request.method != 'POST':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_artists = Artist.query.all()
  found = False
  for artist in all_artists:
    if artist.id == artist_id:
      found = True
      break
  
  if not found:
    response = {"Error message": "Artist ID not found"}
    return jsonify(response), 422

  try:
    name = request.json['name']
    genre = request.json['genre']
    new_album = Album(name, genre, artist_id)
  except:
    response = {"Error message": "Bad Request"}
    return jsonify(response), 400

  all_albums = Album.query.all()
  for album in all_albums:
    if album.id == new_album.id:
      return album_schema.jsonify(album), 409

  db.session.add(new_album)
  db.session.commit()

  return album_schema.jsonify(new_album), 201

# TRACK
@flask_app.route('/albums/<album_id>/tracks', methods=['POST'])
def create_track(album_id):
  if request.method != 'POST':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_albums = Album.query.all()
  found = False
  for album in all_albums:
    if album.id == album_id:
      found = True
      break
  
  if not found:
    response = {"Error message": "Album ID not found"}
    return jsonify(response), 422

  try:
    name = request.json['name']
    duration = request.json['duration']
    new_track = Track(name, duration, album_id)
  except:
    response = {"Error message": "Bad Request"}
    return jsonify(response), 400

  all_tracks = Track.query.all()
  for track in all_tracks:
    if track.id == new_track.id:
      return track_schema.jsonify(track), 409

  db.session.add(new_track)
  db.session.commit()

  return track_schema.jsonify(new_track), 201


# PUT

# ARTIST
@flask_app.route('/artists/<artist_id>/albums/play', methods=['PUT'])
def play_all_tracks_by_artist_id(artist_id):
  if request.method != 'PUT':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_artists = Artist.query.all()
  found = False
  for artist in all_artists:
    if artist.id == artist_id:
      found = True
      break
  
  if not found:
    response = {"Error message": "Artist ID not found"}
    return jsonify(response), 404

  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/artists/%s' % (API_URL, artist_id) == track.artist]
  for track in tracks_filter:
    track.times_played += 1
  db.session.commit()

  result = tracks_schema.dump(tracks_filter)
  return tracks_schema.jsonify(result), 200

# ALBUM
@flask_app.route('/albums/<album_id>/tracks/play', methods=['PUT'])
def play_all_tracks_by_album_id(album_id):
  if request.method != 'PUT':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_albums = Album.query.all()
  found = False
  for album in all_albums:
    if album.id == album_id:
      found = True
      break
  
  if not found:
    response = {"Error message": "Album ID not found"}
    return jsonify(response), 404

  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/albums/%s' % (API_URL, album_id) == track.album]
  for track in tracks_filter:
    track.times_played += 1
  db.session.commit()

  result = tracks_schema.dump(tracks_filter)
  return tracks_schema.jsonify(result), 200

# TRACK
@flask_app.route('/tracks/<track_id>/play', methods=['PUT'])
def play_track_by_id(track_id):
  if request.method != 'PUT':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  track = Track.query.get(track_id)
  if not track:
    response = {"Error message": "Track ID not found"}
    return jsonfy(response), 404
  
  track.times_played += 1
  db.session.commit()

  return track_schema.jsonify(track), 200


# DELETE

# ARTIST
@flask_app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  if request.method != 'DELETE':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_albums = Album.query.all()
  albums_filter = [album for album in all_albums if '%s/artists/%s' % (API_URL, artist_id) == album.artist]
  for album in albums_filter:
    db.session.delete(album)
  
  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/artists/%s' % (API_URL, artist_id) == track.artist]
  for track in tracks_filter:
    db.session.delete(track)

  artist = Artist.query.get(artist_id)
  db.session.delete(artist)
  db.session.commit()

  return artist_schema.jsonify(artist), 204

@flask_app.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(album_id):
  if request.method != 'DELETE':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/albums/%s' % (API_URL, album_id) == track.album]
  for track in tracks_filter:
    db.session.delete(track)

  album = Album.query.get(album_id)
  db.session.delte(album)
  db.session.commit()

  return album_schema.jsonify(album), 204

@flask_app.route('/tracks/<track_id>', methods=['DELETE'])
def delete_track(track_id):
  if request.method != 'DELETE':
    response = {"Error message": "Method Not Allowed"}
    return jsonify(response), 405

  track = Track.query.get(id)
  db.session.delete(track)
  db.session.commit()

  return track_schema.jsonify(track), 204


if __name__ == '__main__':
    flask_app.run(debug=True, port=8000)

from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from base64 import b64encode
import json


#APP

API_URL = 'https://tarea2-cross3.herokuapp.com'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://fhvzicwnvvpgoe:7c0f9dedd7dbc78f6bf63e7be2a0213cf70dabdd49c53af645d7dd879f4156ec@ec2-54-90-211-192.compute-1.amazonaws.com:5432/d734kvsp6ihc0e'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

# TABLES

db = SQLAlchemy(app)
ma = Marshmallow(app)


def get_id(name, parent_id=None):
  if parent_id:
    string = "%s:%s" % (name, parent_id)
  else:
    string = name
  id = b64encode(string.encode()).decode('utf-8')
  return id[:22]


class ArtistSchema(ma.Schema):
  class Meta:
    fields = ('name', 'age', 'albums', 'tracks', 'self')


class AlbumSchema(ma.Schema):
  class Meta:
    fields = ('name', 'genre', 'artist', 'tracks', 'self')


class TrackSchema(ma.Schema):
  class Meta:
    fields = ('name', 'duration', 'times_played', 'artist', 'album', 'self')


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


# db.create_all()


# ROUTES
@app.route('/', methods=['GET'])
def hello():
  response = {"Title": "Tarea 2 de Taller de Integracion", "Author": "Clemente Ross"}
  return jsonify(response), 200

# GET

# ARTISTS
@app.route('/artists', methods=['GET'])
def get_all_artists():
  all_artists = Artist.query.all()
  result = []
  for artist in all_artists:
    dic = {'name': artist.name, 'age': artist.age, 'albums': artist.albums, 'tracks': arist.tracks, 'self': artist.self_url}
    result.append(dic)
  
  return json.dumps(result), 200

@app.route('/artists/<artist_id>', methods=['GET'])
def get_artist_by_id(artist_id):
  artist = Artist.query.get(artist_id)
  
  if artist:
    return artist_schema.jsonify(artist), 200
  
  response = {"Error Message": "Arist ID not found"}
  return jsonify(response), 404

@app.route('/artists/<artist_id>/albums', methods=['GET'])
def get_albums_by_artist_id(artist_id):
  all_albums = Album.query.all()
  albums_filter = [album for album in all_albums if '%s/artists/%s' % (API_URL, artist_id) == album.artist]
  
  if albums_filter:
    result = albums_schema.dump(albums_filter)
    return albums_schema.jsonify(result), 200
  
  response = {"Error Message": "Artist ID not found"}
  return jsonify(response), 404

@app.route('/artists/<artist_id>/tracks', methods=['GET'])
def get_tracks_by_artist_id(artist_id):
  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/artists/%s' % (API_URL, artist_id) == track.artist]

  if tracks_filter:
    result = tracks_schema.dump(tracks_filter)
    return tracks_schema.jsonify(result), 200
  
  response = {"Error Message": "Artist ID not found"}
  return jsonify(response), 404

# ALBUMS
@app.route('/albums', methods=['GET'])
def get_all_albums():
  all_albums = Album.query.all()
  result = albums_schema.dump(all_albums)

  return albums_schema.jsonify(result), 200

@app.route('/albums/<album_id>', methods=['GET'])
def get_album_by_id(album_id):
  album = Album.query.get(album_id)

  if album:
    return album_schema.jsonify(album), 200
  
  response = {"Error Message": "Album ID not found"}
  return jsonify(response), 404

@app.route('/albums/<album_id>/tracks', methods=['GET'])
def get_tracks_by_album_id(album_id):
  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/albums/%s' % (API_URL, album_id) == track.album]

  if tracks_filter:
    result = tracks_schema.dump(tracks_filter)
    return tracks_schema.jsonify(result), 200
  
  response = {"Error Message": "Album ID not found"}
  return jsonify(response), 404

# TRACKS
@app.route('/tracks', methods=['GET'])
def get_all_tracks():
  all_tracks = Track.query.all()
  result = tracks_schema.dump(all_tracks)

  return tracks_schema.jsonify(result), 200

@app.route('/tracks/<track_id>', methods=['GET'])
def get_track_by_id(track_id):
  track = Track.query.get(track_id)

  if track:
    return track_schema.jsonify(track), 200
  
  response = {"Error Message": "Track ID not found"}
  return jsonify(response), 404


# POST

# ARTIST
@app.route('/artists', methods=['POST'])
def create_artist():
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
@app.route('/artists/<artist_id>/albums', methods=['POST'])
def create_album(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
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
@app.route('/albums/<album_id>/tracks', methods=['POST'])
def create_track(album_id):
  album = Album.query.get(album_id)
  if not album:
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
@app.route('/artists/<artist_id>/albums/play', methods=['PUT'])
def play_all_tracks_by_artist_id(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
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
@app.route('/albums/<album_id>/tracks/play', methods=['PUT'])
def play_all_tracks_by_album_id(album_id):
  album = Album.query.get(album_id)
  if not album:
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
@app.route('/tracks/<track_id>/play', methods=['PUT'])
def play_track_by_id(track_id):
  track = Track.query.get(track_id)
  if not track:
    response = {"Error message": "Track ID not found"}
    return jsonfy(response), 404
  
  track.times_played += 1
  db.session.commit()

  return track_schema.jsonify(track), 200


# DELETE

# ARTIST
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
    response = {"Error Message": "Artist ID not found"}
    return jsonify(response), 404
  
  db.session.delete(artist)

  all_albums = Album.query.all()
  albums_filter = [album for album in all_albums if '%s/artists/%s' % (API_URL, artist_id) == album.artist]
  for album in albums_filter:
    db.session.delete(album)
  
  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/artists/%s' % (API_URL, artist_id) == track.artist]
  for track in tracks_filter:
    db.session.delete(track)

  db.session.commit()

  return None, 204

@app.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(album_id):
  album = Album.query.get(album_id)
  if not album:
    response = {"Error Message": "Album ID not found"}
    return jsonify(response), 404
  
  db.session.delete(album)

  all_tracks = Track.query.all()
  tracks_filter = [track for track in all_tracks if '%s/albums/%s' % (API_URL, album_id) == track.album]
  for track in tracks_filter:
    db.session.delete(track)

  db.session.commit()

  return None, 204

@app.route('/tracks/<track_id>', methods=['DELETE'])
def delete_track(track_id):
  track = Track.query.get(id)
  if not track:
    response = {"Error Message": "Track ID not found"}
    return jsonify(response), 404
  
  db.session.delete(track)
  db.session.commit()

  return None, 204


# NOT ALLOWED METHODS

@app.route('/artists', methods=['PUT', 'PATCH', 'DELETE'])
def not_allowed_1():
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/artists/<artist_id>', methods=['POST', 'PUT', 'PATCH'])
def not_allowed_2(artist_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/artists/<artist_id>/albums', methods=['PUT', 'PATCH', 'DELETE'])
def not_allowed_3(artist_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/artists/<artist_id>/tracks', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
def not_allowed_4(artist_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/albums', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
def not_allowed_5():
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/albums/<album_id>', methods=['POST', 'PUT', 'PATCH'])
def not_allowed_6(album_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/albums/<album_id>/tracks', methods=['PUT', 'PATCH', 'DELETE'])
def not_allowed_7(album_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/tracks', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
def not_allowed_8():
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/tracks/<track_id>', methods=['POST', 'PUT', 'PATCH'])
def not_allowed_9(track_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/artists/<artist_id>/albums/play', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def not_allowed_10(artist_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/artists/<artist_id>/tracks/play', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def not_allowed_11(artist_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405

@app.route('/tracks/<track_id>/play', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def not_allowed_12(artist_id):
  response = {"Error Message": "Method Not Allowed"}
  return jsonify(response), 405


if __name__ == '__main__':
    app.run(debug=True)

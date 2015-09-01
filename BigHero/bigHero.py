#!flask/bin/python
from flask import Flask, request, abort, jsonify
from Kensing import Kensing
import sys
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/big_hero/v1/photos', methods=['POST', 'GET'])
def photos():
	k = Kensing()
	if not request.json:
		# We could default to a GET here
		new_photo = []
		index = 0
		all_photos = []
		for photo in k.get_all_photos():
			for value in photo:
				if index == 1:
					new_photo.append(repr(str(value)))
				else:
					new_photo.append(value)
				index = index + 1
			all_photos.append(new_photo)
		return jsonify({'photos': all_photos}), 200
	elif not 'photo_data' in request.json:
		#This is where we posted json but we aren't sending any data
		abort(400)
	else:
		#POST
		photo_data = request.json['photo_data']
		photo_date = request.json['photo_date']
		rating = 0
		if 'rating' in request.json:
			rating = request.json['rating']
		album = request.json['album_name']
		if k.insert_new_photo(photo_data, photo_date, rating, album):
			return 201
		else:
			abort(400)

if __name__ == '__main__':
    app.run(debug=True)
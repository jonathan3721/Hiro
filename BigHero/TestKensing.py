#!flask/bin/python
from Kensing import Kensing
import time
import cStringIO
import sqlite3
k = Kensing()
picture = open('/Users/jonathanlong/Desktop/IMG_8788.JPG', 'rb')
picture_data = picture.read()
current_time = time.strftime("%d/%m/%Y-%H:%M:%S")

# k.insert_new_album("Yosemite")
# print k.album_id_for_name('Yos')
picture_buffer = sqlite3.Binary(picture_data)
# print picture_buffer.__hash__()

# k.rate_photo(picture_buffer, 5)
k.insert_new_photo(picture_buffer, current_time)
# k.add_photo_data_to_album(picture_buffer, 'Zion')
# k.add_photo_data_to_album(picture_buffer, 'Disney')
# k.add_photo_data_to_album(picture_buffer, 'Yosemite')
# k.insert_new_photo(buffer(picture_data), current_time, "Yosemite")
# k.insert_new_photo(buffer(picture_data), current_time, "Yosemite")

zion_album = k.get_all_photos()
new_photo = []
index = 0
for photo in zion_album:
	for value in photo:
		if index == 1:
			print "HERE"
			new_photo.append(repr(str(value)))
		else:
			new_photo.append(value)
		index = index + 1

print new_photo
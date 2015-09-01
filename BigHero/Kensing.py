
import sqlite3
from JELPrettyPrint import JELPrettyPrint as printer
from datetime import datetime

class Kensing(object):
	#############
	#Table Names#
	#############
	PHOTOS_TABLE = "Photos"
	ALBUMS_TABLE = "Albums"
	PHOTOSALBUMS_TABLE = "PhotosAlbums"
	DB_NAME = "Kensing.db"

	#################
	#Photo Properties#
	#################
	photo_properties = ['id', 'data', 'date', 'data_hash', 'rating']
	photo_qualifiers = ['INTEGER PRIMARY KEY ASC AUTOINCREMENT', 'BLOB NOT NULL UNIQUE', 'TEXT NOT NULL', 'TEXT NOT NULL', 'INTEGER']
	album_properties = ['id', 'name']
	album_qualifiers = ['INTEGER PRIMARY KEY ASC AUTOINCREMENT', 'TEXT NOT NULL UNIQUE']
	photosalbums_properties = ['id', 'photoID', 'albumID']
	photosalbums_qualifiers = ['INTEGER PRIMARY KEY ASC AUTOINCREMENT', 'INTEGER', 'INTEGER', 'FOREIGN KEY(photoID) REFERENCES Photos(id)', 'FOREIGN KEY(albumID) REFERENCES Album(id)']

	def __init__(self):
		db = sqlite3.connect(self.DB_NAME)
		cursor = db.cursor()
		create_PHOTOS_TABLE_command = Kensing.create_table_command_with_properites_and_qualifiers(self.PHOTOS_TABLE, self.photo_properties, self.photo_qualifiers)
		create_ALBUMS_TABLE_command = Kensing.create_table_command_with_properites_and_qualifiers(self.ALBUMS_TABLE, self.album_properties, self.album_qualifiers)
		create_PHOTOSALBUMS_TABLE_command = Kensing.create_table_command_with_properites_and_qualifiers(self.PHOTOSALBUMS_TABLE, self.photosalbums_properties, self.photosalbums_qualifiers)
		printer.pretty_print('Creating Photos Table with command: ' + create_PHOTOS_TABLE_command)
		printer.pretty_print('Creating Albums Table with command: ' + create_ALBUMS_TABLE_command)
		printer.pretty_print('Creating PHOTOSAlbums Table with command: ' + create_PHOTOSALBUMS_TABLE_command)
		cursor.execute(create_PHOTOS_TABLE_command)
		cursor.execute(create_ALBUMS_TABLE_command)
		cursor.execute(create_PHOTOSALBUMS_TABLE_command)
		db.commit()

	@staticmethod
	def create_table_command_with_properites_and_qualifiers(table_name, properties, qualifiers):
		command = 'CREATE TABLE IF NOT EXISTS ' + table_name + '('

		property_index = 0
		for qualifier in qualifiers:
			# Index is less than properties and qualifiers - we have more of each
			if property_index == len(properties) - 1 and property_index == len(qualifiers) - 1:
				the_property = properties[property_index]
				command = command + ' ' + the_property + ' ' + qualifier
			elif property_index < len(properties) and property_index < len(qualifiers):
				the_property = properties[property_index]
				command = command + ' ' + the_property + ' ' + qualifier + ','
			elif property_index == len(qualifiers) - 1: # We only have more qualifiers
				command = command + ' ' + qualifier
			else: # We don't have any more of either
				command = command + ' ' + qualifier + ','
			property_index = property_index + 1
		return command + ')'
	
	@staticmethod
	def insert_statement(table_name, properties):
		insert = 'INSERT into ' + table_name + '('
		last_insert = '('
		property_index = 0
		for prop in properties:
			if property_index < len(properties) - 1:
				insert = insert + prop + ", "
				last_insert = last_insert + '?, '
			else:
				insert = insert + prop + ')'
				last_insert = last_insert + '?) '
				break
			property_index = property_index + 1

		return insert + ' values ' + last_insert

	##############
	### PHOTOS ###
	##############
	def insert_photos_statement(self):
		return Kensing.insert_statement(self.PHOTOS_TABLE, self.photo_properties)

	def insert_new_photo(self, photo_data, photo_date, rating=0, album_name=None):
		insert = self.insert_photos_statement()
		album_id = self.album_id_for_name(album_name)
		printer.pretty_print(insert)
		data_hash = photo_data.__hash__()
		photo_id = self.number_of_photos() + 1
		many_to_many = self.insert_photosalbums_statement()
		printer.pretty_print_positive(many_to_many)
		try:
			if album_id:
				self.__commit(many_to_many, (photo_id, album_id))
			self.__commit(insert, (photo_id, photo_data, str(photo_date), data_hash, rating))
			return True
		except Exception, e:
			printer.pretty_print_error(str(e))
			return False
		

	def id_for_photo_data(self, photo_data):
		select = 'SELECT id from ' + self.PHOTOS_TABLE +' where data_hash=' + str(photo_data.__hash__())
		result = self.__execute(select)
		photo_id = result.fetchone()
		if photo_id:
			return photo_id[0]
		else:
			return None

	def photos_for_album(self, album_name):
		album_id = self.album_id_for_name(album_name)
		if album_id:
			select = 'SELECT * from ' + self.PHOTOS_TABLE + ' LEFT JOIN ' + self.PHOTOSALBUMS_TABLE + ' pa on pa.photoID= ' + self.PHOTOS_TABLE +'.id' + ' WHERE pa.albumID=' + str(album_id)
			printer.pretty_print_positive(select)
			photos = self.__execute(select)
			return photos.fetchall()

	def add_photo_data_to_album(self, photo_data, album_name):
		photo_id = self.id_for_photo_data(photo_data)
		if photo_id:
			return self.add_photo_to_album(photo_id, album_name)
		return False


	def add_photo_to_album(self, photo_id, album_name):
		album_id = self.album_id_for_name(album_name)
		if album_id:
			# update_statement = 'INSERT ' + self.PHOTOSALBUMS_TABLE + ' SET albumID=? WHERE photoID=?'
			insert_statement = self.insert_photosalbums_statement()
			next_id = self.number_of_photosalbums() + 1
			values = (next_id, photo_id, album_id)
			printer.pretty_print_positive(insert_statement)
			printer.pretty_print_positive(str(values))
			self.__commit(insert_statement, values)
			return True
		else:
			self.insert_new_album(album_name)
			self.add_photo_to_album(photo_id, album_name)
		return False

	def number_of_photos(self):
		select = 'SELECT COUNT(*) from ' + self.PHOTOS_TABLE
		return self.__execute(select).fetchone()[0]

	def rate_photo(self, photo_data, rating):
		photo_id = self.id_for_photo_data(photo_data)
		if photo_id:
			return self.rate_photo_id(photo_id, rating)
		return False

	def rate_photo_id(self, photo_id, rating):
		update = 'UPDATE ' + self.PHOTOS_TABLE + ' SET rating=? WHERE id=?'
		values = (rating, photo_id)
		self.__commit(update, values)

	def get_all_photos(self):
		select = 'SELECT * from '+ self.PHOTOS_TABLE
		result = self.__execute(select)
		return result.fetchall()
	
	##########################
	### photos <--> albums ###
	##########################
	
	def number_of_photosalbums(self):
		select = 'SELECT COUNT(*) from ' + self.PHOTOSALBUMS_TABLE
		return self.__execute(select).fetchone()[0]

	def insert_photosalbums_statement(self):
		return Kensing.insert_statement(self.PHOTOSALBUMS_TABLE, self.photosalbums_properties)
	
	##############
	### ALBUMS ###
	##############

	def insert_new_album(self, album_name):
		insert = self.insert_album_statement()
		self.__commit(insert, (self.number_of_albums() + 1, album_name))

	def number_of_albums(self):
		select = 'SELECT COUNT(*) from ' + self.ALBUMS_TABLE
		return self.__execute(select).fetchone()[0]		

	def insert_album_statement(self):
		return Kensing.insert_statement(self.ALBUMS_TABLE, self.album_properties)

	def album_id_for_name(self, album_name):
		if album_name:
			select = 'SELECT * from ' + self.ALBUMS_TABLE + ' where name=' + '\'' + album_name + '\''
			result = self.__execute(select)
			album = result.fetchone()
			if album != None:
				return album[0]
		return None

# Convenience Methods

	def __execute(self, statement):
		db = sqlite3.connect(self.DB_NAME)
		cursor = db.cursor()
		executed = cursor.execute(statement)
		printer.pretty_print("Executed: " + str(statement))
		return executed

	def __commit(self, statement, values):
		db = sqlite3.connect(self.DB_NAME)
		cursor = db.cursor()
		committed = cursor.execute(statement, values)
		db.commit()
		printer.pretty_print("committed: " + str(statement))
		return committed
		

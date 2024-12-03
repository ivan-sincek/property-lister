#!/usr/bin/env python3

from . import directory, file, general, plist, sql

import binascii, biplist, enum, os, re

class Extension(enum.Enum):
	"""
	Enum containing file extensions.
	"""
	TEXT      = ".txt"
	BLOB      = ".blob"
	PLIST     = ".plist"
	XML       = ".xml"
	PLIST_XML = ".plist.xml"

class PropertyLister:

	def __init__(
		self,
		databases          : list[general.File],
		property_lists     : list[general.File],
		out                : str,
		directory_structure: bool
	):
		"""
		Class for extracting property list files.
		"""
		self.__databases           = databases
		self.__property_lists      = property_lists
		self.__out                 = out
		self.__directory_structure = directory_structure
		self.__flags               = re.MULTILINE | re.IGNORECASE

	def run(self):
		"""
		Start the extraction.
		"""
		print(general.get_timestamp("Extracting..."))
		if self.__databases:
			self.__dump_and_extract()
		elif self.__property_lists:
			for path in self.__property_lists:
				self.__extract(path, internal = False)
		return directory.count_files(self.__out)
	
	def __get_out(self, relative_directory: str):
		"""
		Get the output directory.
		"""
		directory = self.__out
		if self.__directory_structure and relative_directory:
			directory = os.path.join(self.__out, relative_directory)
			os.makedirs(directory, exist_ok = True)
		return directory

	def __dump_and_extract(self):
		"""
		Extract property list files from database files.
		"""
		for db in self.__databases:
			count = 0
			data, error = sql.read(db.path)
			if not error and data:
				out = self.__get_out(db.relative_directory)
				new_db = file.build(out, db.path, Extension.TEXT)
				file.write_silent(data, new_db)
				general.print_green(new_db)
				for blob in re.findall(r"(?<=,X')[\w\d]+", data, flags = self.__flags):
					count += 1
					new_blob = file.build(out, new_db, Extension.BLOB, str(count))
					file.write_binary_silent(binascii.unhexlify(blob), new_blob)
					self.__extract(general.File(new_blob, db.relative_directory), internal = True)

	def __extract(self, path: general.File, internal: bool = False):
		"""
		Extract property list files from property list files.
		"""
		data, error = plist.run(path.path)
		if not error and re.search(rb"\<plist[\s\S]+\<\/plist\>", data, flags = self.__flags):
			out = self.__get_out(path.relative_directory)
			new_plist_xml = file.build(out, path.path, Extension.PLIST_XML) if internal else file.build(out, file.build(out, path.path, Extension.PLIST), Extension.XML)
			file.write_binary_silent(data, new_plist_xml)
			general.print_yellow(new_plist_xml)
			try:
				data = biplist.readPlist(path.path)
				if isinstance(data, dict):
					count = 0
					for value in data.values():
						if isinstance(value, biplist.Data):
							string = biplist.readPlistFromString(value) # extract a property list file from a property list file
							if string:
								count += 1
								new_plist = file.build(out, path.path, Extension.PLIST, str(count))
								biplist.writePlist(string, new_plist)
								self.__extract(general.File(new_plist, path.relative_directory), internal = True)
			except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
				pass
			if internal:
				os.remove(path.path)

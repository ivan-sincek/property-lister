#!/usr/bin/env python3

from . import config, directory, file, general

import argparse, sys

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print(f"Property Lister {config.APP_VERSION} ( github.com/ivan-sincek/property-lister )")
		print("")
		print("--- Extract from an SQLite database file ---")
		print("Usage:   property-lister -db database -o out")
		print("Example: property-lister -db Cache.db -o results_db")
		print("")
		print("--- Extract from a property list file ---")
		print("Usage:   property-lister -pl property-list -o out")
		print("Example: property-lister -pl Info.plist    -o results_pl")
		print("")
		print("DESCRIPTION")
		print("    Extract and convert property list files")
		print("DATABASE")
		print("    SQLite database file, or directory containing multiple files")
		print("    -db, --database = Cache.db | databases | etc.")
		print("PROPERTY LIST")
		print("    Property list file, or directory containing multiple files")
		print("    -pl, --property-list = Info.plist | plists | etc.")
		print("OUT")
		print("    Output directory")
		print("    All extracted propery list files will be saved in this directory")
		print("    -o, --out = results | etc.")
		print("DIRECTORY STRUCTURE")
		print("    Preserve the directory structure within the output directory")
		print("    -ds, --directory-structure")

	def error(self, message):
		if len(sys.argv) > 1:
			print("Missing a mandatory option (-db, -o) or (-pl, -o) and/or optional (-ds)")
			print("Use -h or --help for more info")
		else:
			self.print_help()
		exit()

class Validate:

	def __init__(self):
		"""
		Class for validating and managing CLI arguments.
		"""
		self.__parser = MyArgParser()
		group = self.__parser.add_mutually_exclusive_group(         required = True                                         )
		group.add_argument(        "-db" , "--database"           , required = False, type   = str         , default = ""   )
		group.add_argument(        "-pl" , "--property-list"      , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-o"  , "--out"                , required = True , type   = str         , default = ""   )
		self.__parser.add_argument("-ds" , "--directory-structure", required = False, action = "store_true", default = False)

	def validate_args(self):
		"""
		Validate and return the CLI arguments.
		"""
		self.__success = True
		self.__args = self.__parser.parse_args()
		self.__validate_database()
		self.__validate_property_list()
		self.__validate_out()
		return self.__success, self.__args

	def __error(self, message: str):
		"""
		Set the success flag to 'False' to prevent the main task from executing, and print an error message.
		"""
		self.__success = False
		general.print_error(message)

	# ------------------------------------

	def __validate_database(self):
		tmp = []
		if self.__args.database:
			self.__args.database = directory.abspath(self.__args.database)
			if not directory.exists(self.__args.database):
				self.__error(f"\"{self.__args.database}\" does not exist")
			elif directory.is_directory(self.__args.database):
				success, message = directory.validate(self.__args.database)
				if not success:
					self.__error(message)
				else:
					for path in directory.list_files(self.__args.database):
						tmp.append(general.File(path, directory.dirname(path).lstrip(self.__args.database)))
					if not tmp:
						self.__error(f"No valid files were found in \"{self.__args.database}\"")
			else:
				success, message = file.validate(self.__args.database)
				if not success:
					self.__error(message)
				else:
					self.__args.directory_structure = False
					tmp = [general.File(self.__args.database)]
		self.__args.database = tmp


	def __validate_property_list(self):
		tmp = []
		if self.__args.property_list:
			self.__args.property_list = directory.abspath(self.__args.property_list)
			if not directory.exists(self.__args.property_list):
				self.__error(f"\"{self.__args.property_list}\" does not exist")
			elif directory.is_directory(self.__args.property_list):
				success, message = directory.validate(self.__args.property_list)
				if not success:
					self.__error(message)
				else:
					for path in directory.list_files(self.__args.property_list):
						tmp.append(general.File(path, directory.dirname(path).lstrip(self.__args.property_list)))
					if not tmp:
						self.__error(f"No valid files were found in \"{self.__args.property_list}\"")
			else:
				success, message = file.validate(self.__args.property_list)
				if not success:
					self.__error(message)
				else:
					self.__args.directory_structure = False
					tmp = [general.File(self.__args.property_list)]
		self.__args.property_list = tmp

	def __validate_out(self):
		if self.__success:
			self.__args.out = directory.abspath(self.__args.out)
			success, message = directory.overwrite(self.__args.out)
			if not success:
				self.__error(message)

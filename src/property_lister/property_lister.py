#!/usr/bin/env python3

import argparse, binascii, biplist, datetime, os, re, shutil, sqlite3, subprocess, sys

# ----------------------------------------

class Stopwatch:

	def __init__(self):
		self.__start = datetime.datetime.now()

	def stop(self):
		self.__end = datetime.datetime.now()
		print(("Script has finished in {0}").format(self.__end - self.__start))

stopwatch = Stopwatch()

# ----------------------------------------

def check_duplicate(file):
	array = os.path.splitext(file)
	count = 0
	filename = file
	while os.path.exists(filename):
		count += 1
		filename = ("{0} ({1}){2}").format(array[0], count, array[1])
	return filename

def build(out, file, ext, replace = False, count = None):
	if out:
		file = os.path.join(out, os.path.basename(file))
	if ext:
		if replace or file.lower().endswith(ext):
			file = os.path.splitext(file)[0] + ext # NOTE: Normalize.
		else:
			file = file + ext # NOTE: Normalize.
	if count:
		file = os.path.splitext(file)[0] + "." + str(count) + ext
	return check_duplicate(file)

def read_database(file):
	tmp = ""
	db = None
	try:
		db = sqlite3.connect(file)
		tmp = ("\n").join(db.iterdump())
	except sqlite3.DatabaseError:
		pass
	finally:
		if db:
			db.close()
	return tmp

ext = {"txt": ".txt", "blob": ".blob", "plist": ".plist", "xml": ".plist.xml"}

# database --> full path (external)
def dump(database, out):
	for db in database:
		count = 0
		data = read_database(db)
		if data:
			db = build(out, db, ext["txt"])
			open(db, "w").write(data)
			blobs = re.findall(r"(?<=,X')[\w\d]+", data, re.MULTILINE | re.IGNORECASE)
			if blobs:
				for blob in blobs:
					count += 1
					new = build(out, db, ext["blob"], True, count)
					open(new, "wb").write(binascii.unhexlify(blob))
					extract(new, out, True)

def run(command):
	return subprocess.run((" ").join(command), shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT).stdout

# file --> full path (external/internal)
def extract(file, out, internal):
	data = run(["plistutil", "-f", "xml", "-i", ("\"{0}\"").format(file)])
	if re.search(rb"\<plist[\s\S]+\<\/plist\>", data, re.MULTILINE | re.IGNORECASE):
		open(build(out, file, ext["xml"], True) if internal else build(out, build(out, file, ext["plist"]), ext["xml"], True), "wb").write(data)
		try:
			data = biplist.readPlist(file)
			if isinstance(data, dict):
				count = 0
				for key in data:
					if isinstance(data[key], biplist.Data):
						string = biplist.readPlistFromString(data[key]) # NOTE: Extract a property list file from a property list file.
						if string:
							count += 1
							new = build(out, file, ext["plist"], internal, count)
							biplist.writePlist(string, new)
							extract(new, out, True)
		except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
			pass
		if internal:
			os.remove(file)

# ----------------------------------------

class PropertyLister:

	def __init__(self, database, property_list, out):
		self.__database      = database
		self.__property_list = property_list
		self.__out           = out

	def run (self):
		print("Extracting...")
		if self.__database:
			dump(self.__database, self.__out)
		elif self.__property_list:
			for file in self.__property_list:
				extract(file, self.__out, False)
		return len(os.listdir(self.__out))

# ----------------------------------------

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print("Property Lister v2.8 ( github.com/ivan-sincek/property-lister )")
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

	def error(self, message):
		if len(sys.argv) > 1:
			print("Missing a mandatory option (-db, -o) or (-pl, -o)")
		else:
			self.print_help()
		exit()

class Validate:

	def __init__(self):
		self.__proceed = True
		self.__parser  = MyArgParser()
		group = self.__parser.add_mutually_exclusive_group(  required = True                           )
		group.add_argument(        "-db", "--database"     , required = False, type = str, default = "")
		group.add_argument(        "-pl", "--property-list", required = False, type = str, default = "")
		self.__parser.add_argument("-o" , "--out"          , required = True , type = str, default = "")

	def run(self):
		self.__args               = self.__parser.parse_args()
		self.__args.database      = self.__parse_directory(self.__args.database)      if self.__args.database      else []
		self.__args.property_list = self.__parse_directory(self.__args.property_list) if self.__args.property_list else []
		self.__args.out           = self.__parse_out(self.__args.out)                 # required
		self.__args               = vars(self.__args)
		return self.__proceed

	def get_arg(self, key):
		return self.__args[key]

	def __error(self, msg):
		self.__proceed = False
		self.__print_error(msg)

	def __print_error(self, msg):
		print(("ERROR: {0}").format(msg))

	def __parse_directory(self, value):
		tmp = []
		if not os.path.exists(value):
			self.__error("Directory containing files, or a single file does not exists")
		elif os.path.isdir(value):
			tmp = self.__validate_directory_files(value)
			if not tmp:
				self.__error("No valid files were found")
		else:
			if not os.access(value, os.R_OK):
				self.__error("File does not have read permission")
			elif not os.stat(value).st_size > 0:
				self.__error("File is empty")
			else:
				tmp = [value]
		return tmp

	def __validate_directory_files(self, directory):
		tmp = []
		for path, dirs, files in os.walk(directory):
			for file in files:
				file = os.path.join(path, file)
				if os.path.isfile(file) and os.access(file, os.R_OK) and os.stat(file).st_size > 0:
					tmp.append(file)
		return tmp

	def __parse_out(self, value):
		if self.__proceed:
			self.__proceed = False
			overwrite = "yes"
			if os.path.exists(value):
				print(("'{0}' directory already exists").format(value))
				overwrite = input("Overwrite the output directory (yes): ")
			if overwrite.lower() == "yes" and self.remove_directory(value):
				self.__proceed = self.__create_directory(value)
		return value

	def remove_directory(self, directory):
		success = True
		try:
			if os.path.exists(directory):
				shutil.rmtree(directory)
		except Exception:
			success = False
			self.__error(("Cannot remove '{0}' related directories/subdirectories and/or files").format(directory))
		return success

	def __create_directory(self, directory):
		success = True
		try:
			if not os.path.exists(directory):
				os.mkdir(directory)
		except Exception:
			success = False
			self.__error(("Cannot create '{0}' directory").format(directory))
		return success

# ----------------------------------------

def main():
	validate = Validate()
	if validate.run():
		print("##########################################################################")
		print("#                                                                        #")
		print("#                          Property Lister v2.8                          #")
		print("#                                     by Ivan Sincek                     #")
		print("#                                                                        #")
		print("# Extract and convert property list files.                               #")
		print("# GitHub repository at github.com/ivan-sincek/property-lister.           #")
		print("# Feel free to donate ETH at 0xbc00e800f29524AD8b0968CEBEAD4cD5C5c1f105. #")
		print("#                                                                        #")
		print("##########################################################################")
		out = validate.get_arg("out")
		property_lister = PropertyLister(
			validate.get_arg("database"),
			validate.get_arg("property_list"),
			validate.get_arg("out")
		)
		length = property_lister.run()
		if length <= 0:
			print("No results")
			validate.remove_directory(out)
		else:
			print(("Created files: {0}").format(length))
		stopwatch.stop()

if __name__ == "__main__":
	main()

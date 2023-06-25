#!/usr/bin/env python3

import datetime
import sys
import os
import shutil
import sqlite3
import re
import binascii
import subprocess
import biplist

start = datetime.datetime.now()

# -------------------------- INFO --------------------------

def basic():
	global proceed
	proceed = False
	print("Property Lister v2.2 ( github.com/ivan-sincek/property-lister )")
	print("")
	print("--- Extract from an SQLite database file ---")
	print("Usage:   property-lister -db database -o out")
	print("Example: property-lister -db Cache.db -o results")
	print("")
	print("--- Extract from a property list file ---")
	print("Usage:   property-lister -pl property-list -o out")
	print("Example: property-lister -pl Info.plist    -o results")

def advanced():
	basic()
	print("")
	print("DESCRIPTION")
	print("    Extract and convert property list files")
	print("DATABASE")
	print("    SQLite database file, or directory containing multiple files")
	print("    -db <database> - Cache.db | databases | etc.")
	print("PROPERTY LIST")
	print("    Property list file, or directory containing multiple files")
	print("    -pl <property-list> - Info.plist | plists | etc.")
	print("OUT")
	print("    Output directory")
	print("    All extracted propery list files will be saved in this directory")
	print("    -o <out> - results | etc.")

# ------------------- MISCELENIOUS BEGIN -------------------

def remove_directory(directory):
	success = True
	try:
		if os.path.exists(directory):
			shutil.rmtree(directory)
	except Exception:
		success = False
		print_error(("Cannot remove '{0}' related directories/subdirectories and/or files").format(directory))
	return success

def create_directory(directory):
	success = True
	try:
		if not os.path.exists(directory):
			os.mkdir(directory)
	except Exception:
		success = False
		print_error(("Cannot create '{0}' directory").format(directory))
	return success

def check_directory(directory):
	success = False
	overwrite = "yes"
	if os.path.exists(directory):
		print(("'{0}' directory already exists").format(directory))
		overwrite = input("Overwrite the output directory (yes): ")
	if overwrite.lower() == "yes" and remove_directory(directory):
		success = create_directory(directory)
	return success

def check_directory_files(directory):
	tmp = []
	for path, dirs, files in os.walk(directory):
		for file in files:
			file = os.path.join(path, file)
			if os.path.isfile(file) and os.access(file, os.R_OK) and os.stat(file).st_size > 0:
				tmp.append(file)
	return tmp

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

def run(command):
	return subprocess.run((" ").join(command), shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT).stdout

# -------------------- MISCELENIOUS END --------------------

# -------------------- VALIDATION BEGIN --------------------

# my own validation algorithm

proceed = True

def print_error(msg):
	print(("ERROR: {0}").format(msg))

def error(msg, help = False):
	global proceed
	proceed = False
	print_error(msg)
	if help:
		print("Use -h for basic and --help for advanced info")

args = {"database": None, "plist": None, "out": None}

# TO DO: Better site validation.
def validate(key, value):
	global args
	value = value.strip()
	if len(value) > 0:
		if key == "-db" and args["database"] is None:
			args["database"] = value
			if not os.path.exists(args["database"]):
				error("Directory containing files, or a single file does not exists")
			elif os.path.isdir(args["database"]):
				args["database"] = check_directory_files(args["database"])
				if not args["database"]:
					error("No valid files were found")
			else:
				if not os.access(args["database"], os.R_OK):
					error("File does not have read permission")
				elif not os.stat(args["database"]).st_size > 0:
					error("File is empty")
				else:
					args["database"] = [args["database"]]
		elif key == "-pl" and args["plist"] is None:
			args["plist"] = value
			if not os.path.exists(args["plist"]):
				error("Directory containing files, or a single file does not exists")
			elif os.path.isdir(args["plist"]):
				args["plist"] = check_directory_files(args["plist"])
				if not args["plist"]:
					error("No valid files were found")
			else:
				if not os.access(args["plist"], os.R_OK):
					error("File does not have read permission")
				elif not os.stat(args["plist"]).st_size > 0:
					error("File is empty")
				else:
					args["plist"] = [args["plist"]]
		elif key == "-o" and args["out"] is None:
			args["out"] = os.path.abspath(value)

def check(argc, args):
	count = 0
	for key in args:
		if args[key] is not None:
			count += 1
	return argc - count == argc / 2

# --------------------- VALIDATION END ---------------------

# ----------------- GLOBAL VARIABLES BEGIN -----------------

ext = {"txt": ".txt", "blob": ".blob", "plist": ".plist", "xml": ".plist.xml"}

# ------------------ GLOBAL VARIABLES END ------------------

# ----------------------- TASK BEGIN -----------------------

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

# file --> full path (external/internal)
def extract(file, out, internal):
	data = run(["plistutil", "-f", "xml", "-i", ("'{0}'").format(file)])
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

def main():
	argc = len(sys.argv) - 1

	if argc == 0:
		advanced()
	elif argc == 1:
		if sys.argv[1] == "-h":
			basic()
		elif sys.argv[1] == "--help":
			advanced()
		else:
			error("Incorrect usage", True)
	elif argc % 2 == 0 and argc <= len(args) * 2:
		for i in range(1, argc, 2):
			validate(sys.argv[i], sys.argv[i + 1])
		if not ((args["database"] is not None and args["out"] is not None) or (args["plist"] is not None and args["out"] is not None)) or (args["database"] is not None and args["plist"] is not None) or not check(argc, args):
			error("Missing a mandatory option (-db, -o)")
			error("Missing a mandatory option (-pl, -o)", True)
	else:
		error("Incorrect usage", True)

	if proceed and check_directory(args["out"]):
		print("##########################################################################")
		print("#                                                                        #")
		print("#                          Property Lister v2.2                          #")
		print("#                                     by Ivan Sincek                     #")
		print("#                                                                        #")
		print("# Extract and convert property list files.                               #")
		print("# GitHub repository at github.com/ivan-sincek/property-lister.           #")
		print("# Feel free to donate ETH at 0xbc00e800f29524AD8b0968CEBEAD4cD5C5c1f105. #")
		print("#                                                                        #")
		print("##########################################################################")
		if args["database"]:
			dump(args["database"], args["out"])
		elif args["plist"]:
			for file in args["plist"]:
				extract(file, args["out"], False)
		length = len(os.listdir(args["out"]))
		if not length:
			print("No results")
			remove_directory(args["out"])
		else:
			print(("Created files: {0}").format(length))
		print(("Script has finished in {0}").format(datetime.datetime.now() - start))

if __name__ == "__main__":
	main()

# ------------------------ TASK END ------------------------

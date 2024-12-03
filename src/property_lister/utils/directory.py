#!/usr/bin/env python3

from . import array, file

import os, shutil

def create(directory: str):
	"""
	Create a new directory.
	"""
	success = True
	message = ""
	try:
		if not os.path.exists(directory):
			os.mkdir(directory)
	except Exception:
		success = False
		message = f"Cannot create \"{directory}\""
	return success, message

def remove(directory: str):
	"""
	Remove a directory.
	"""
	success = True
	message = ""
	try:
		if os.path.exists(directory):
			shutil.rmtree(directory)
	except Exception:
		success = False
		message = f"Cannot remove \"{directory}\""
	return success, message

def exists(path: str):
	"""
	Returns 'True' if a path exists.
	"""
	return os.path.exists(path)

def is_directory(directory: str):
	"""
	Returns 'True' if the 'directory' exists and is a regular directory.
	"""
	return os.path.isdir(directory)

def validate(directory: str):
	"""
	Validate a directory.\n
	Success flag is 'True' if the directory has a read permission and is not empty.
	"""
	success = False
	message = ""
	if not os.access(directory, os.R_OK):
		message = f"\"{directory}\" does not have a read permission"
	elif not os.stat(directory).st_size > 0:
		message = f"\"{directory}\" is empty"
	else:
		success = True
	return success, message

def abspath(path: str):
	"""
	Returns the full path to a file or directory.
	"""
	return os.path.abspath(path)

def dirname(file: str):
	"""
	Returns the directory where the specified file is located.
	"""
	return os.path.dirname(file)

def list_files(directory: str) -> list[str]:
	"""
	Get all valid files from a directory. Recursive.
	"""
	tmp = []
	for path, dirnames, filenames in os.walk(directory):
		for filename in filenames:
			full = os.path.join(path, filename)
			if file.validate_silent(full):
				tmp.append(full)
	return array.unique(tmp)

def count_files(directory):
	"""
	Count files in a directory. Recursive.
	"""
	count = 0
	for path, dirnames, filenames in os.walk(directory):
		count += len(filenames)
	return count

def overwrite(directory: str):
	"""
	If the output directory exists, prompt to overwrite it.\n
	Returns 'True' if overwrite was successful or if the directory does not exist.
	"""
	success = True
	message = ""
	confirm = "yes"
	if os.path.isdir(directory):
		print(f"'{directory}' already exists")
		confirm = input("Overwrite the output directory (yes): ")
	if confirm.lower() in ["yes", "y"]:
		success, message = remove(directory)
		if success:
			success, message = create(directory)
	return success, message

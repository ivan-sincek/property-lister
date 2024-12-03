#!/usr/bin/env python3

from . import extractor

import os

def validate(file: str):
	"""
	Validate a file.\n
	Success flag is 'True' if the file has a read permission and is not empty.
	"""
	success = False
	message = ""
	if not os.access(file, os.R_OK):
		message = f"\"{file}\" does not have a read permission"
	elif not os.stat(file).st_size > 0:
		message = f"\"{file}\" is empty"
	else:
		success = True
	return success, message

def validate_silent(file: str):
	"""
	Silently validate a file.\n
	Returns 'True' if the 'file' exists, is a regular file, has a read permission, and is not empty.
	"""
	return os.path.isfile(file) and os.access(file, os.R_OK) and os.stat(file).st_size > 0

def write_silent(content: str, out: str):
	"""
	Silently write a content to an output file.
	"""
	try:
		open(out, "w").write(content)
	except Exception:
		pass

def write_binary_silent(content: bytes, out: str):
	"""
	Silently write a binary content to an output file.
	"""
	try:
		open(out, "wb").write(content)
	except Exception:
		pass

def unique(file: str):
	"""
	If a duplicate exists, append a unique number to the filename.
	"""
	base, extension = os.path.splitext(file)
	count = 0
	filename = file
	while os.path.isfile(filename):
		count += 1
		filename = f"{base} ({count}){extension}"
	return filename

def build(out: str, file: str, ext: extractor.Extension, append = ""):
	"""
	Get the full path to a new output file.
	"""
	file = os.path.join(out, os.path.basename(file))
	# ------------------------------------
	base, extension = os.path.splitext(file)
	if not extension.lower().endswith(ext.value):
		file += ext.value
	# ------------------------------------
	if append:
		base, extension = os.path.splitext(file)
		file = base + f".{append}" + extension
	# ------------------------------------
	return unique(file)

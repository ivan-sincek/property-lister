#!/usr/bin/env python3

import subprocess

def run(file: str):
	"""
	Run 'plistutil' as a new subprocess.\n
	Returns an empty byte string and an error message on failure.
	"""
	response = b""
	message = ""
	try:
		response = subprocess.run(f"plistutil -f xml -i \"{file}\"", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT).stdout
	except Exception as ex:
		message = str(ex)
	return response, message

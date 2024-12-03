#!/usr/bin/env python3

import sqlite3

def read(file: str):
	"""
	Read an SQL file using SQLite3 connector.\n
	Returns an empty string and an error message on failure.
	"""
	tmp = ""
	message = ""
	db = None
	try:
		db = sqlite3.connect(file)
		tmp = ("\n").join(db.iterdump())
	except sqlite3.DatabaseError as ex:
		message = str(ex)
	finally:
		if db:
			db.close()
	return tmp, message

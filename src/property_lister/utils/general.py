#!/usr/bin/env python3

import colorama, dataclasses, datetime, termcolor

colorama.init(autoreset = True)

@dataclasses.dataclass
class File:
	"""
	Class for storing a file.
	"""
	path              : str
	relative_directory: str = ""

def get_timestamp(message: str):
	"""
	Get the current timestamp.
	"""
	return f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}"

def print_error(message: str):
	"""
	Print an error message.
	"""
	print(f"ERROR: {message}")

def print_green(message: str):
	"""
	Print a message in green color.
	"""
	termcolor.cprint(message, "green")

def print_yellow(message: str):
	"""
	Print a message in yellow color.
	"""
	termcolor.cprint(message, "yellow")

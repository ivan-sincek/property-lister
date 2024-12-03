#!/usr/bin/env python3

from .utils import config, directory, extractor, validate

import datetime

# ----------------------------------------

class Stopwatch:

	def __init__(self):
		self.__start = datetime.datetime.now()

	def stop(self):
		self.__end = datetime.datetime.now()
		print(f"Script has finished in {self.__end - self.__start}")

stopwatch = Stopwatch()

# ----------------------------------------

def main():
	success, args = validate.Validate().validate_args()
	if success:
		config.banner()
		tool = extractor.PropertyLister(
			args.database,
			args.property_list,
			args.out,
			args.directory_structure
		)
		length = tool.run()
		if length <= 0:
			print("No results")
			directory.remove(args.out)
		else:
			print(f"Files created: {length}")
		stopwatch.stop()

if __name__ == "__main__":
	main()

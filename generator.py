#!/usr/bin/env python3
import argparse
import collections
import datetime
import json
import os
import sys

def apply_macros(m, t):
	for key in m.keys():
		t = t.replace("!%s!" % key, m[key])
	return t

# print an error to stderr and then exit 1
def error(s):
	sys.stderr.write("%s: %s\n" % (sys.argv[0], s))
	sys.exit(1)

# safely read a file
# n
#	file name
def fileread(n):
	try:
		f = open(n)
	except FileNotFoundError as e:
		error(e)
	r = f.read()
	f.close()
	return r

# safely write a file
# n
#	file name
# c
#	content
def filewrite(n, c):
	try:
		f = open(n, "w")
	except Exception as e:
		error(e)
	f.write(c)
	f.close()

# mkdir -p {$years}/{$months}, you get the idea
def generate_directory_structure(data):
	for year in list(data["concerts"]):
		if not(os.path.exists(year)):
			try:
				os.mkdir(year)
			except Exception as e:
				error("Error generating directory structure (os.mkdir): %s" % e)
		os.chdir(year)
		for month in list(data["concerts"][year]):
			if not(os.path.exists(month)):
				try:
					os.mkdir(month)
				except Exception as e:
					error("Error generating directory structure (os.mkdir): %s" % e)
		os.chdir("..")

def generate_pages(data, template):
	for year in list(data["concerts"]):
		os.chdir(year)
		for month in list(data["concerts"][year]):
			os.chdir(month)
			for day in list(data["concerts"][year][month]):
				filewrite(
					"%s.html" % day,
					apply_macros(macros(data, [year, month, day]), template)
				)
			os.chdir("..")
		os.chdir("..")
	return

# generates macro content
# data
#	the full JSON object
# selection
#	A list of [
#		the year of the performance selected (str, len 4)
#		the month of the performance selected (str, len 2)
#		the day of the performance selected (str, len 2)
#	]
def macros(data, selection):
	year = selection[0]
	month = selection[1]
	day = selection[2]
	try:
		concert = data["concerts"][year][month][day]
	except KeyError as e:
		error("macros(): KeyError: %s" % e)

	# trivial date macros to start out
	macros = collections.OrderedDict([
		("DY", year),
		("DM", month),
		("DD", day),
		("Dp", datetime.date(int(year), int(month), int(day)).strftime("%d %B %Y"))
	])

	macros["Venue"] = concert["venue"]

	# video embed
	video = data["concerts"][year][month][day]["video"]
	if(video["type"] == "iframe"):
		macros["Embed"] = '''\
<IFRAME
ALLOWFULLSCREEN
FRAMEBORDER="0"
HEIGHT="480"
MOZALLOWFULLSCREEN="true"
SRC="%s"
WEBKITALLOWFULLSCREEN="true"
WIDTH="640"
><P><A HREF="%s">iframe</A></P></IFRAME>''' % (video["href"], video["href"])
	else:
		error("What video type is %s? (%s)"
			% (video["type"], ('data["concerts"]["%s"]["%s"]["%s"]["video"]["type"]'
				% (year, month, day))))

	# setlist ordered list
	setlist = "<OL>\n"
	for s in concert["setlist"]:
		setlist += "<LI>%s</LI>\n" % s
	setlist += "</OL>\n"
	macros["Setlist"] = setlist

	return macros

def main(argc, argv):
	try:
		data = json.loads(fileread("data.json"))
	except json.decoder.JSONDecodeError as e:
		error("Invalid JSON file. (%s)" % e)

	page_template = fileread("template-page.html")

	os.chdir("generation")

	generate_directory_structure(data)
	generate_pages(data, page_template)

	return 0;

if __name__ == "__main__":
	sys.exit(main(len(sys.argv), sys.argv))

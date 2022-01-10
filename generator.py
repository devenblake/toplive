#!/usr/bin/env python3
import argparse
import collections
import datetime
import json
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
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument('year')
	parser.add_argument('month')
	parser.add_argument('day')
	args = vars(parser.parse_args(argv[1:]))
	year, month, day = args["year"], args["month"], args["day"]

	try:
		data = json.loads(fileread("data.json"))
	except json.decoder.JSONDecodeError as e:
		error("Invalid JSON file. (%s)" % e)

	template = fileread("template-page.html")

	m = macros(data, [year, month, day])
	template = apply_macros(m, template)
	print(end=template)

	return 0;

if __name__ == "__main__":
	sys.exit(main(len(sys.argv), sys.argv))

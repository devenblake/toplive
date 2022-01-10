import datetime
import json
import sys

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
	macros = {
		"DY": year,
		"DM": month,
		"DD": day,
		"Dp": datetime.date(int(year), int(month), int(day)).strftime("%d %B %Y"),
		"Venue": data["concerts"][year][month][day]["venue"]
	}
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
	macros["setlist"] = ""
	for s in data["concerts"][year][month][day]["setlist"]:
		macros["setlist"] += "<LI>%s</LI>\n" % s
	return macros

def error(s):
	sys.stderr.write("%s\n" % s)
	sys.exit(1)

with open('data.json') as f:
	try:
		data = json.load(f)
	except json.decoder.JSONDecodeError as e:
		error("Invalid JSON file. (%s)" % e)

with open('template-page.html') as f:
	try:
		template = f.read()
	except:
		error("Error reading template.")

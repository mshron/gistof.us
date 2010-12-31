import csv
import shelve
import json
from optparse import OptionParser

usage = "usage: %prog [options] shelf_1 [shelf_2 ... shelf_n]\nFirst shelf is primary; it's keys are the final ones."
parser = OptionParser(usage=usage)
parser.add_option('-o', "--o", dest="csv_file",
                  help="output csv file", metavar="FILE")

(options, args) = parser.parse_args()

shelves = [shelve.open(sh,'r') for sh in args]
out = csv.writer(open(options.csv_file,'w'))

print "Opened files for reading and writing."

for key in shelves[0]:
    final = {}
    data = [sh.get(key) for sh in shelves]
    for d in data:
        if d:
            final.update(d)
    out.writerow([key,json.dumps(final).encode('hex')])
    print "Wrote: %s"%key

print "Done"

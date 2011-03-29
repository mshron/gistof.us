#!/usr/bin/env python
import shelve
import json
import numpy as np
from optparse import OptionParser
import sys

class JSONDecodesNumpy(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,(np.ndarray,np.float64,np.int64)):
            if len(o.shape) == 0:
                return float(o)
            else:
                return [float(x) for x in o]
        else:
            return json.JSONEncoder.default(self, o)

usage = "usage: %prog [options] shelf_1 [shelf_2 ... shelf_n] > result.json\nFirst shelf is primary; it's keys are the final ones."
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

shelves = [shelve.open(sh,'r') for sh in args]
out = {}

sys.stderr.write("Opened files for reading and writing.\n")

for key in shelves[0]:
    final = {}
    data = [sh.get(key) for sh in shelves]
    for d in data:
        if d:
            for k,v in d.iteritems():
                final.setdefault(k,{}).update(v)
    out[key] = json.dumps(final, cls=JSONDecodesNumpy)
    sys.stderr.write("Wrote: %s\n"%key)

print json.dumps(out) 

sys.stderr.write("Done\n")

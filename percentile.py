#!/usr/bin/env python

import shelve
import sys
from optparse import OptionParser

def percentile(l, n, ile=5, presort=True):
    #l is the domain of observations - l should be presorted to save on
       #resorting every time
    #n is the value to be percentiled
    #ile is the number of bins to divide the domain into

    # the function outputs a number from 1 to ile.
    # 1 = lowest percentile, ile = highest percentile
    # always in terms of absolute numbers in the data
    
    obs_count = len(l)
    if obs_count < ile:
        return False
    if obs_count==0:
        return False
    if not presort:
        l.sort()

    step = obs_count/ile
    for i in range(1,ile): 
        if n <= l[step*i]:
            return i-1
    return ile-1                    #must be top percentile if we get here

        
def histogram(l, bottom, top, bins=10):

    w = top-bottom
    binsize = float(w)/float(bins)

    #top edges of bins
    bin_edges = [top-(i*binsize) for i in reversed(range(bins))] 
    
    bin_counts = [0 for x in range(bins)]
    for d in l:
        for n in range(bins):
            if d < bin_edges[n]:
                bin_counts[n] = bin_counts[n]+1 
                break
    return {'bin_edges': bin_edges, 'bin_counts': bin_counts}

def process_scalar_targets(in_shelves, out_shelf):
    #amal: {tractid => value} for the current target stat
    amal = {}
    for t in scalar_targets:
        m = t[0] #main stat category
        s = t[1] #subcategory
        print("%s > %s" % (m, s))

        #amalgamate all the values we have
        for in_shelf in in_shelves:
            for tractid in in_shelf:
                #skip the tid for this shelf if this shelf doesn't have
                #the stat we're looking for
                if in_shelf[tractid].get(m,{}).get(s,{}) != {}: 
                    #don't overwrite a value from a prior shelf
                    #the earlier ones have precedence
                    if not amal.has_key(tractid):
                        try:
                            amal[tractid] = float(in_shelf[tractid][m][s])
                        except ValueError:
                            pass
                            

        obs_list = sorted([amal[tid] for tid in amal])
        h = histogram(obs_list, float(obs_list[0]), float(obs_list[-1]))
        global_data = out_shelf.get('global_data', {})
        global_data.setdefault(m,{}).setdefault(s,{})['histogram'] = h
        out_shelf ['global_data'] = global_data

        for i,tractid in enumerate(amal):
            ile = percentile(obs_list, amal[tractid], ile=100)
            tract = out_shelf.get(tractid, {})
            tract.setdefault(m, {})[s+'_percentile'] = ile
            out_shelf[tractid] = tract
            if (i!= 0) and ((i%100) == 0):
                out_shelf.sync()
        
        amal = {}
    out_shelf.sync()

def setup_shelf(shelf_file):
    shelf = shelve.open(shelf_file)
    return shelf

scalar_targets = [
    ('poverty', 'pct_below_100pc'),
    ('race', 'pct_white_not_latino'),
    ('veteran_status', 'pct_veteran'),
    ('hispanic_or_latino', 'pct_hispanic_or_latino')
]


def main():
    usage = "usage: %prog [options] shelf_1 [shelf_2 ... shelf_n] -o result.json\nFirst shelf is primary; its keys are the final ones."
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--out", dest="out_filename", 
                help="output percentile data to shelf named FILE", metavar="FILE")

    (options, args) = parser.parse_args()

    #open in-shelves
    in_shelves = [shelve.open(sh,'r') for sh in args]
    out = {}

    sys.stderr.write("Opened in-files for reading.\n")

    #open out-shelf
    out_shelf = setup_shelf(options.out_filename)
    sys.stderr.write("Opened out-file for writing.\n")

    #this is where the magic happens
    process_scalar_targets(in_shelves, out_shelf)

    out_shelf.close()
    
    sys.stderr.write('Done\n')

if __name__ == '__main__':
    main()

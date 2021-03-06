#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from django.utils import simplejson as json

import cPickle as cp
import random
import hashlib
import csv
import recommend

class Tract(db.Model):
    picturelist = db.ListProperty(db.Blob)
    data = db.TextProperty()
    tractid = db.StringProperty()
    order = db.IntegerProperty()
    has_pictures = db.BooleanProperty()

def prepare(tract):
    out = {}
    out['data'] = json.loads(tract.data) #TODO turn this in to pickle?
    out['summaries'] = recommend.parse(out['data'])
    out['tractid'] = tract.tractid
    out['order'] = tract.order
    out['pictures'] = map(cp.loads,tract.picturelist)
    return out

def getcontext(n, j, direction=None):
    #if not j:
        #j = random.randint(0, 2**32 - 1)
    if direction == 'left': 
        query = Tract.all().order('-order').filter('order <=', j).filter('has_pictures =', True)
    elif direction == 'right':
        query = Tract.all().order('order').filter('order >=', j).filter('has_pictures =', True)
    else:
        raise IndexError("Need a direction to know how to index")
    out = query.fetch(n)
    l = len(out)
    if l<n:
        if direction=='right':
            s = 'order'
        elif direction=='left':
            s = '-order'
        else:
            raise IndexError("Need a direction to know how to index")
        query = Tract.all().order(s)
        out.extend(query.fetch(n-l))
    return out

class Tracts(webapp.RequestHandler):
    def put(self):
        # is there one yet?
        first = False if Tract.all().count(1) > 0 else True

        tract_data = json.loads(self.request.body_file.getvalue())
        for tractid in tract_data:
            tract = Tract()
            tract.tractid = tractid
            data = tract_data[tractid]
            if first:
                rand = 2**32 - 1
                first = False
            else:
                rand = random.randint(0, 2**32 - 1)
            tract.order = rand
            tract.data = data
            tract.has_pictures = False
            tract.put()
            self.response.out.write('Put %s @ %s\n'%(tractid, rand))

    def get(self):
        # j is the order property of the tract from which we want context
        j = self.request.get('j')
        if not j:
            # if client provides no j, pick a random place to start them
            j = random.randint(0, 2**32 - 1)
        j = int(j)

        # n is the number of tracts of context desired
        n = self.request.get('n')
        if not n:
            # n has a default value
            n = 10
        n = int(n)

        # 'dir' means 'I want context starting at the Tract with order 'j' 
        # and going dir 'n' Tracts'
        # TODO: Context queries with a direction specified should NOT include
        # Tract 'j' in their results - if a client makes a directional request
        # that includes a 'j', it presumably already HAS j in its collection.
        # Note that a query which specifies j and not dir SHOULD include j since
        # this type of query indicates that the client wants to START its browsing
        # experience at j, as if a user wanted to return to a specific place
        # after having left the site and returning to a bookmark/hotlink.
        direction = self.request.get('dir')
        if not direction:
            result_right = getcontext(n+1, j, 'right')
            result_left = getcontext(n+1, j, 'left')
            result = result_left[1:][::-1] + result_right
        else:
            result = getcontext(n, j, direction)
            
        prep_result = map(prepare, result)
        out = json.dumps(prep_result)
        self.response.headers['Content-Type'] = 'application/X-JSON'
        self.response.out.write(out)
        

class Pictures(webapp.RequestHandler):
    def put(self): #patterned after addtracts
        lines = csv.reader(self.request.body_file)
        for line in lines:
            # tract, hexurl, hexauthor
            tractid = line[0]
            hexurl = line[1]
            url = hexurl.decode('hex')
            hexauthor = line[2]
            author = hexauthor.decode('hex')
            order = random.randint(0,2**16 - 1)
            metadata = {'author': author}
            photo = {'url': url, 'metadata': metadata, 'order': order}
            tract_query = db.GqlQuery("SELECT * FROM Tract WHERE tractid=:1",tractid)
            tract = tract_query.get()
            if not tract:
                self.response.out.write("Adding to %s failed\n"%tractid)
            else:
                pkl = db.Blob(cp.dumps(photo))
                tract.picturelist.append(pkl)
                tract.has_pictures = True
                tract.put()
        self.response.out.write("Finished.")

class PicturesJSON(webapp.RequestHandler):
    def put(self): # now takes json files: {'tractid': [photo1,photo2], etc.}
        _data = json.load(self.request.body_file)
        assert isinstance(_data, dict)
        for tractid,_photos in _data.iteritems():
            _picturelist = []
            for photo in _photos:
                photo['order'] = random.randint(0,2**16-1)
            tract_query = db.GqlQuery("SELECT * FROM Tract WHERE tractid=:1", tractid)
            tract = tract_query.get()
            if not tract:
                self.response.out.write("Adding to %s failed\n"%tractid)
            else:
                pkl = [db.Blob(cp.dumps(p)) for p in _photos]
                tract.picturelist.extend(pkl)
                tract.has_pictures = True
                tract.put()
                self.response.out.write("Added photos to %s.\n"%tractid)
        self.response.out.write("Finished.\n")


class OrderData(webapp.RequestHandler):
    def get(self):
       query = Tract.all().order('order') 
       for q in query:
            self.response.out.write("%s,"%q.order)

class ReadMemcache(webapp.RequestHandler):
    def get(self):
        key = self.request.get('key')
        print memcache.get(key)

def main():
    application = webapp.WSGIApplication([('/tracts', Tracts),
        ('/pictures', PicturesJSON),
        ('/photos', PicturesJSON),
        ('/orders',OrderData),
        ('/mem',ReadMemcache)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

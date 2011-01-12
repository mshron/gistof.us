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

class Tract(db.Model):
    picturelist = db.ListProperty(db.Blob)
    data = db.TextProperty()
    tractid = db.StringProperty()
    order = db.IntegerProperty()
    has_pictures = db.BooleanProperty()

def prepare(tract):
    out = {}
    out['data'] = json.loads(tract.data) #TODO turn this in to pickle?
    out['tractid'] = tract.tractid
    out['order'] = tract.order
    out['pictures'] = map(cp.loads,tract.picturelist)
    return out

def getcontext(n, j=None, direction=None):
    if not j:
        j = random.randint(0, 2**32 - 1)
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

class Context(webapp.RequestHandler):
    def get(self):
        j = self.request.get('j')
        if j:
            j = int(j)
        n = self.request.get('n')
        if not n:
            n = 10
        n = int(n)
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
        

class AddTracts(webapp.RequestHandler):
    def put(self):
        # is there one yet?
        first = False if Tract.all().count(1) > 0 else True
        lines = csv.reader(self.request.body_file)
        for line in lines:
            tract = Tract()
            tractid = line[0]
            data = line[1].decode('hex')
            tract.tractid = tractid
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

class AssociatePictures(webapp.RequestHandler):
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
    application = webapp.WSGIApplication([('/addtracts', AddTracts),
        ('/addpictures', AssociatePictures),
        ('/context',Context),
        ('/orders',OrderData),
        ('/mem',ReadMemcache)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

"""Take a dictionary NAME->rectangles and pull pictures down from flickr for those same rectangles"""
import urllib
import json

flickrcall = "http://api.flickr.com/services/rest?method=flickr.photos.search&api_key=4667108ce3ecdd5cd0438f88c76240e8&format=json&bbox=%s&min_upload_date=1000000000&nojsoncallback=1"

def call(bbox):
    b = ",".join(map(str,bbox.ravel()))
    url = flickrcall%b
    return url

def get_photos(url):
    u = urllib.urlopen(url)
    data = u.readlines()
    assert len(data) == 1
    parsed = json.loads(data[0])
    if parsed['stat'] != 'ok':
        raise IndexError
    photos = parsed['photos']['photo']
    out = {}
    for p in photos:
        out[p['id']] = p
    return out

def parse_photo_to_url(d):
    return "http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s.jpg"%d

def photolist_to_urls(l):
    out = []
    for photo in l:
        this = {}
        this['owner'] = photo['owner']
        this['title'] = photo['title']
        this['url'] =  parse_photo_to_url(photo)
        out.append(this)
    return out

def bboxes_to_photoset(rects):
    out = {}
    for r in rects:
        call_url = call(r)
        photos = get_photos(call_url)
        out.update(photos)
    return photolist_to_urls(out.values())

# example:
# nm_shp = shape_to_dict('tr35_d00.shp')
# nm_rects = find_rects(nm_shp)
# nm_pics = bboxes_to_photoset(nm_rects[k[1]][0])

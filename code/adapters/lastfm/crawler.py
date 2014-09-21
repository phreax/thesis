from models import *
import datetime
import time
import api

def parse_tags(tags):
    def functor(tag):
        return [tag["name"], tag["count"]]

    return [functor(tag) for tag in tags]

def get_artist_tags():
    ntags = 5
    artists = Artist.query().all()
    artists_count = len(artists)
    tag_set = set()
    artist_tags = {}
    t0 = time.time()
    t1 = None
    errors = []

    for i, a in enumerate(artists):
        if i % 100 == 0:
            if not t1: t1 = t0
            dt = time.time() - t1
            dt_total = time.time() - t0 
            speed = float(100)/dt
            estimated_time = (artists_count-i)/speed
            print "Elapsed time: %s"%datetime.timedelta(seconds=dt_total)
            print "Estimated time: %s"%datetime.timedelta(seconds=estimated_time)
            print "Speed %.2f requests/s"%speed
            print "Progress: %.2f"%(float(i)/artists_count)
            t1 = time.time()
        try:
            tags = api.gettoptags(a.uid)[:ntags]
            artist_tags[a.id] = parse_tags(tags)
            for t in tags:
                tag_set.add(t["name"])
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            print "Cought %s .. continue" %e
            print "artist_id = %d" % a.id
            errors.append(a.id)
            continue

    return tag_set, artist_tags, errors

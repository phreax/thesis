from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import *
import datetime
import time
import dateutil.parser 
import codecs
import api
from serialize import load_pickle
from tags import tag_set 

listen_events_dataset = 'datasets/lastfm-dataset-1K/userid-timestamp-artid-artname-traid-traname.tsv'
users_dataset = 'datasets/lastfm-dataset-1K/userid-profile.tsv'
tag_file = "db/artist_tags_normalized.pickle"

db_name = 'sqlite:///db/lastfm.sqlite'

Session = sessionmaker()

def load_all_data(total_lines=19150868):
    engine = create_engine(db_name, echo=False,encoding='utf-8')
    session = Session(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    users = parse_users(session)
    parse_listen_events(users,session,total_lines)


def load_artist_tags(filename=tag_file):
    engine = create_engine(db_name, echo=False,encoding='utf-8')
    session = Session(bind=engine)
    ArtistTag.drop()
    Tag.drop()

    Base.metadata.create_all(engine)
    artist_tags = load_pickle(filename)
    tags = sorted(tag_set(artist_tags))

    tag_ids = {}

    print "Add tags"
    for i, t in enumerate(tags):
        print "add %d: %s"%(i,t)
        tag = Tag(name=t)
        tag.id = i
        session.add(tag)
        tag_ids[t] = i
    session.commit()

    print "Add artist tags"
    for artist_id, tags in artist_tags.items():
        for t, r in tags:
            tag_id = tag_ids[t]
            artist_tag = ArtistTag(relevance=int(r))
            artist_tag.artist_id = artist_id
            artist_tag.tag_id = tag_id 
            session.add(artist_tag)

    session.commit()
   
def parse_listen_events(users,session,total_lines=19150868,chunk_size=100000):

    artists = {}
    tracks = {}
    last_artist_id = 0
    last_track_id = 0

    lines_left = total_lines

    nchunks = total_lines/chunk_size
    nlines = 0
    offset = 0
    i = 0
    line_count = 0

    t1 = time.time()
    with codecs.open(listen_events_dataset,encoding='utf-8') as infile:
        while(lines_left>0):

            infile.seek(offset)
            if(lines_left-chunk_size<0):
                nlines = lines_left
            else:
                nlines = chunk_size

            progress = 100.0*i/nchunks 
            print 'Processing chunk %s/%s  (%.2f %%)' % (i,nchunks,progress)
            i += 1
            lines_left -= nlines

            bytes_read = 0
            t2 = time.time()

            for j,line in zip(xrange(nlines),infile):
                bytes_read += len(line)
                line_count += 1

                if line[0] == '#':
                    continue
                try:
                    userid,timestamp,auid,aname,tuid,tname = line.strip('\n').split('\t')
                except:
                    continue

                if not (auid and tuid):
                    continue
                if not users.has_key(userid):
                    print "broken line %s" % (line_count)
                    print "'%s'" % line
                    continue

                artist = None
                track  = None
                if not artists.has_key(auid):
                    artists[auid] = last_artist_id
                    artist = Artist(uid=auid,
                                    name=aname
                                    )
                    artist.id = artists[auid]
                    last_artist_id += 1

                if not tracks.has_key(tuid):
                    tracks[tuid] = last_track_id
                    track = Track(uid =tuid,
                                  name=tname
                                 )
                    track.id = tracks[tuid]
                    last_track_id += 1
                    
                if track:
                    track.artist_id = artists[auid]
                    session.add(track)
                if artist:
                    artist.track_id = tracks[tuid]
                    session.add(artist)

                event = ListenEvent(
                                    track_id=tracks[tuid],
                                    user_id=users[userid],
                                    timestamp=dateutil.parser.parse(timestamp)
                                   )

                session.add(event)

            session.commit()

            offset += bytes_read

            delta_t2 = time.time()-t2
            print 'total bytes read: %s, elapsed time: %.2f' % (offset,delta_t2)

    delta_t1 = time.time()-t1
    print '\nFinished, total elapsed time: %.2f' % (delta_t1)

def parse_users(session):

    users = {}
    with codecs.open(users_dataset,encoding='utf-8') as infile:
        for i,line in enumerate(infile):
            if line[0] == '#':
                continue

            user,gender,age,country,signup =  line.split('\t')
            u = User(name=user,
                     gender = gender,
                     age =age,
                     country=country,
                     registered_at = dateutil.parser.parse(signup)
                     )
            u.id = i
            session.add(u)
            users[user] = i

    session.commit()
    return users



from models import *
from sqlalchemy.orm import joinedload
from helper import partition
from helper import split_seq_query
from collections import defaultdict

def grouped_tags():
    artist_tags = ArtistTag.query().all()
    tags = defaultdict(list)

    for at in artist_tags:
        relevance = float(at.relevance)/100.0
        tags[at.artist_id].append([at.name, relevance])

    return tags

def taglist():
    tags = Tag.query().all()
    return [t.name for t in tags]

def item_tags(item_ids):
    query = lambda seq: Track.query().filter(Track.id.in_(seq)).options(joinedload('artist'))
    items = split_seq_query(query, item_ids)

    tags = defaultdict(list)
    for item in items:
        for at in item.artist.tags.all():
            relevance = float(at.relevance)/100.0
            tags[item.id].append([at.name, relevance])
    
    return tags

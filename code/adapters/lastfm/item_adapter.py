from models import *
from sqlalchemy.orm import joinedload
from collections import defaultdict
from helper import split_seq_query

def grouped_items(item_ids):
    '''Group items (tracks) by artist'''

    query = lambda seq: Track.query().filter(Track.id.in_(seq))
    items = split_seq_query(query, item_ids)
    groups = defaultdict(list)

    for item in items: 
        groups[item.artist_id].append(item.id)

    return groups

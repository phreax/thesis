from adapters.lastfm.models import *
from collections import defaultdict
from helper import inverse_dict
from serialize import *
from random import shuffle
import random

class DataSampler(object):
    """Select a subset of data from the input dataset."""

    min_listen_count = 9
    training_ratio = 0.8
    
    is_loaded = False

    def __init__(self, ntestusers=50, log_perc=[49,50]):
        self.ntestusers = ntestusers
        self.log_perc = log_perc

        # seed pnrg to get deterministic results
        random.seed("samplingforfunandprofit")

    def load(self, force=False):
        print "Load data from database"
        if self.is_loaded and not force:
            print "Data is already loaded. Use force=True to reload data"
            return

        events = ListenEvent.query().filter(ListenEvent.percentile(*self.log_perc)).all()
        print "first timestamp: %s"%events[0].timestamp
        print "last timestamp: %s"%events[-1].timestamp
        users = User.query().filter(User.country!="").all()
        self.prepare(events, users)

        # sample random users for evaluation purpose
        self.test_users = self.sample_test_users(k=self.ntestusers)

        self.is_loaded = True

    def prepare(self, events, users):

        print "Prepare data"

        user_events = defaultdict(list)
        item_events = defaultdict(list)
        listen_count = defaultdict(int)
        valid_items = {}

        for event in events:
            listen_count[event.item_id] += 1

        for item_id, count in listen_count.items():
            if(count > self.min_listen_count):
                valid_items[item_id] = True

        for event in events:
            if(event.item_id in valid_items):
                user_events[event.user_id].append(event)

        # discard users with low listen count
        for user_id, events in user_events.items():
            if len(events) < self.min_listen_count:
                del user_events[user_id]

        # build user_events for training and testing
        user_events_train = defaultdict(list)
        user_events_test = defaultdict(list)
        item_events_train = defaultdict(list)
        item_events_test = defaultdict(list)

        for user_id, events in user_events.items():
            n = len(events)
            k = int(n*self.training_ratio)
            user_events_train[user_id] = events[:k]
            user_events_test[user_id] = events[k:]
        
        for user_id, events in user_events_test.items():
            nremoved = 0
            if len(events) == 0:
                del user_events_test[user_id]
                nremoved += 1
        
        print "#test_users = %d"%len(user_events_test)
        print "#removed users %d"%nremoved

        for user_id, events in user_events_train.items():
            for event in events:
                item_id = event.item_id
                if valid_items[item_id]:
                    item_events_train[item_id].append(event)

        for user_id, events in user_events_test.items():
            for event in events:
                item_id = event.item_id
                if valid_items[item_id]:
                    item_events_test[item_id].append(event)

        # ids of all valid items
        item_ids = {item_id:i for i,item_id in enumerate(valid_items)}
        user_ids = {user_id:i for i,user_id in enumerate(user_events.keys())}

        self.item_ids     = item_ids
        self.user_ids     = user_ids

        # user training data here
        self.user_events  = user_events_train
        self.item_events  = item_events_train

        self.user_events_test = user_events_test
        self.item_events_test = item_events_test
        
    def sample_test_users(self, k=20):

        test_users = [user_id for  user_id in self.user_events_test if user_id in self.user_events]
        shuffle(test_users)
        return test_users[:k]

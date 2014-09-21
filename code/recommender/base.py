from adapters.lastfm.models import *
from collections import defaultdict
from helper import inverse_dict
from serialize import *
from random import shuffle
from decorators import memoize
from data_sampler import DataSampler
from helper import Delegate

class Base(object):
    log_perc = [49,50]
    training_ratio = 0.8
    min_listen_count = 10

    export_attributes = ["item_ids", "user_ids", "user_events", "item_events", "user_events_test", "item_events_test"]

    is_trained = False

    def __init__(self, **options):
        self.parse_options(options)
        self.print_params()
        self.__class__.delegate_attributes()

    def load_data(self):
        self.sampler.load()

    @classmethod
    def delegate_attributes(cls):
        """delegate data access to the sampler instance"""
        attributes = ["user_ids", "item_ids", "user_events", "item_events"]
        for attr in attributes:
            delegate = Delegate('sampler',attr)
            setattr(cls,attr,delegate)
 
    def parse_options(self, options):
         
        if "sampler" in options:
            self.sampler = options["sampler"]
        else:
            self.sampler = DataSampler()

        for key, value in options.items():
            if key in self.option_desc:
                setattr(self, key, value) 

    def print_params(self):
        print "Options:"

        for name in self.option_desc.keys():
            attr = getattr(self, name)
            if type(attr) == dict:
                print "%s:"%name 
                for k,v in attr.items():
                    print "\t%s=%s"%(k,v)
            else:
                print "%s=%s"%(name,attr)

        print

    def save_model(self):
        data = {name: getattr(self, name) for name in self.export_attributes if hasattr(self, name)}
        filename = self.file_prefix+'data.pickle'
        save_pickle(filename, data)

    def load_model(self):
        filename = self.file_prefix+'data.pickle'
        data = load_pickle(filename)
        for name, value in data.items():
            setattr(self, name, value)

    def user_id_to_index(self, user_id):
        """Give internal index for a user_id"""
        return self.user_ids[user_id]

    def index_to_user_id(self, user_index):

        if not hasattr(self, "user_ids_inverse"):
            self.user_ids_inverse = inverse_dict(self.user_ids)

        return self.user_ids_inverse[user_index]

    def item_id_to_index(self, item_id):
        """Give internal index for a item_id"""
        return self.item_ids[item_id]

    def index_to_item_id(self, item_index):
        if not hasattr(self, "item_ids_inverse"):
            self.item_ids_inverse = inverse_dict(self.item_ids)

        return self.item_ids_inverse[item_index]

    def hit_ratio(self, k, user_id, **kwargs):
        """Calculate hit ratio for evaluation."""
        raise Exception("Not Implemented")

    def build_model(self):
        """Build prediction model."""
        raise Exception("Not Implemented")

    def top_k_recommendations(self, user, k=5, **kwargs):
        raise Exception("Not Implemented")

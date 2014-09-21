from collections import defaultdict
from helper import Delegate
from recommender.graph_cars import GraphCARS
from recommender.usercf import UserCF
from recommender.usercf_cars import ReductionUserCF
from data_sampler import DataSampler
import time

class Evaluator(object):

    user_events_test  = Delegate("sampler","user_events_test")
    test_users = Delegate("sampler","test_users")

    def __init__(self, recommender, sampler, ctxabs=None):
        self.recommender = recommender
        self.sampler = sampler
        if ctxabs:
            self.ctxabs = ctxabs
        elif hasattr(recommender,"ctxabs"):
            self.ctxabs = recommender.ctxabs
            
    def hit_ratio(self, k, user_id, **kwargs):
        """Compute the hit-ratio for a single user""" 

        events = self.user_events_test[user_id]
        recommendations = self.recommender.top_k_recommendations(user_id, k)

        item_counts = self.count_items(events)
        hits = len([True for r,item_id in recommendations if item_id in item_counts])

        hr = 0
        if len(item_counts) > 0:
                hr = float(hits)/float(len(item_counts))

        # print "hr@%d for user %s = %0.4f"%(k, user_id, hr)
        return hr

    def count_items(self, events):
        """Count the occurency of each item in the log"""

        item_counts = defaultdict(int)
        for e in events:
            item_counts[e.item_id] += 1

        return item_counts

    def count_items_context(self, events):
        """Count the occurency of each item in the log"""
        item_counts = {}
        for c in self.ctxabs.values():
            item_counts[c] = defaultdict(int)

        for e in events:
            c = self.ctxabs.retrieve_context(e.local_timestamp)
            item_counts[c][e.item_id] += 1

        return item_counts

    def hit_ratio_context(self, k, user_id, **kwargs):

        events = self.user_events_test[user_id]
        item_counts = self.count_items_context(events)
        hr = 0
        
        ctxabs = self.ctxabs
        nsets = 0

        for c in ctxabs.values():
            recommendations = self.recommender.top_k_recommendations(user_id, k, context=c)

            hits = len([True for r, item in recommendations if item in item_counts[c]])
            if len(item_counts[c]) > 0:
                hr += float(hits)/float(len(item_counts[c]))
                nsets += 1

        # print "#sets = %d"%nsets
        hr /= float(nsets)
        # print "hr@%d for user %s = %0.4f"%(k, user_id, hr)
        return hr

    def hit_ratio_total(self, k, **kwargs):
        """Calculate hit ratio for evaluation."""

        if "use_context" in kwargs and kwargs["use_context"] == True:
            print "context aware evaluation" 
            eval_method = self.hit_ratio_context
        else:
            eval_method = self.hit_ratio

        hr = sum(eval_method(k, user_id, **kwargs) for user_id in self.test_users)
        hr /= float(len(self.test_users))

        print "-------------------------------------------------"
        print
        print "mean hit ratio @%d: %.2f"%(k,hr)
        print
        return hr

def eval_algorithm(sampler, algorithm_cls=GraphCARS, **params):

    nvalues = [5,10,15,30]
    params["sampler"] =sampler
    recommender = algorithm_cls(**params)
    recommender.build_model()

    use_context = recommender.is_context_aware

    if "use_context" in params:
        use_context = params["use_context"]

    evaluator = Evaluator(recommender, sampler)

    results = []

    for n in nvalues:
        t1 = time.time()
        hrn = evaluator.hit_ratio_total(n, use_context=use_context)
        results.append(hrn)
        print "elapsed time %.2fmin"%(float(time.time()-t1)/60.)
    print results

def do_evaluation(sampler):

    eval_algorithm(sampler, algorithm_cls=UserCF)

    params = {
        "use_dow" : True,
        "use_tod" : False
    }
    eval_algorithm(sampler, algorithm_cls=ReductionUserCF, **params)

if __name__=="__main__":

    sampler = DataSampler(log_perc=[25,25])
    sampler.load()

    do_evaluation(sampler)

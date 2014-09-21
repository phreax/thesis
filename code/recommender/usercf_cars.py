from adapters.lastfm.models import *
from collections import defaultdict
import numpy as np
import math
from math import sqrt
import operator as op
from serialize import *
from numeric import *
from recommender.usercf import UserCF
from context import ContextAbstractor
from itertools import izip
from numpy import sum
from numeric import *

class ReductionUserCF(UserCF):
    file_prefix = 'db/reduct_usercf_'

    # default params 
    use_tod = True
    use_dow = True
    include_known = False 
    option_desc = {
           "use_tod":           "Use time of day context", 
           "use_dow":           "Use day of week context",
           "include_known":     "Include known tracks in recommendation", 
    }

    is_context_aware = True

    def __init__(self, **options):
        super(UserCF, self).__init__(**options)
        self.ctxabs = ContextAbstractor(use_tod=self.use_tod, use_dow=self.use_dow)

    def compute_ratings(self,events):
        nc = self.ctxabs.dim
        ratings = defaultdict(int)

        for event in events:
            ctx = self.ctxabs.retrieve_context(event.local_timestamp)
            item_id = event.item_id
            if not (item_id in ratings):
                ratings[item_id] = np.zeros(nc)
            ratings[item_id][ctx] += 1

        return ratings

    def build_rating_matrix(self, user_ids, user_events, item_ids):
        nc = self.ctxabs.dim

        # build rating matrix (tensor)
        user_item_matrix = np.zeros((len(user_ids),len(item_ids),nc),dtype=np.float32)

        for user_id, i in user_ids.items():
            ratings = self.compute_ratings(user_events[user_id])

            for item_id, j in item_ids.items():
                user_item_matrix[i][j][:] = ratings[item_id]

        # # normalize rows
        # user_item_matrix = normalize_rows(user_item_matrix)

        return user_item_matrix

    def get_k_neighbors(self, user, k, context):
        neighbors = self.weight_matrix[user, :, context].argsort().tolist()
        del neighbors[neighbors.index(user)]
        return neighbors[-k:]

    def predict_ratings(self, user, context, include_known=False):
        X = self.user_item_matrix
        W = self.weight_matrix

        nusers,nitems,nc = X.shape
        predictions = []
        neighbors = self.get_k_neighbors(user, self.k_neighbors, context)

        avg_rating = np.mean(np.apply_along_axis(sum,1,X[user]))

        for item in xrange(nitems):

            sum_weighted_var = 0
            sum_weights = 0

            # only predict unrated items
            if(X[user][item][context]) and not include_known:
                continue
            for neighbor in neighbors:
                user_rating = X[neighbor][item][context]
                if not user_rating:
                    continue
                avg_rating_neighbor = np.mean(np.apply_along_axis(sum,1,X[neighbor]))
                sum_weighted_var += (user_rating-avg_rating_neighbor)*W[user][neighbor][context]
                sum_weights += abs(W[user][neighbor][context])

            pred = avg_rating
            if sum_weights:
                pred += sum_weighted_var/sum_weights
                item_id = self.index_to_item_id(item)
                predictions.append((pred,item_id))

        predictions.sort(reverse=True)
        return predictions

    def top_k_recommendations(self, user_id, k=5, **kwargs):
        """Interface for generating recommendations"""

        if not self.is_trained:
            print """recommender is not trained yet. please run build_model first"""
        context = None
        if "context" in kwargs:
            context = kwargs["context"]
        else:
            timestamp = kwargs["timestamp"]
            context = self.ctxabs.retrieve_context(timestamp)

        include_known = self.include_known
        if "include_known" in kwargs:
            include_known = kwargs["include_known"]

        user_index = self.user_id_to_index(user_id)

        predictions = self.predict_ratings(user_index, context, include_known=include_known)
        predictions.sort(reverse=True)
        return predictions[:k]

    def compute_weights(self, user_item_matrix,dist_fun=cosine_sim):
        M = user_item_matrix
        nusers = M.shape[0]
        nctx   = M.shape[2]
        W = np.zeros((nusers, nusers, nctx))

        for c in self.ctxabs.values():
            W[:,:,c] = super(self.__class__,self).compute_weights(M[:,:,c],dist_fun)
        return W

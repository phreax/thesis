from adapters.lastfm.models import *
from collections import defaultdict
from recommender.base import Base
import numpy as np
import math
import operator as op
from serialize import *
import pickle
from numeric import *

class UserCF(Base):
    file_prefix = 'db/usercf_'
    k_neighbors = 5

    export_attributes = ["item_ids", "user_ids", "user_events", "item_events", "user_events_test", "item_events_test", "user_item_matrix", "weight_matrix"]
    # default params 
    include_known = False 
    option_desc = {
            "include_known":     "Include known tracks in recommendation", 
    }

    is_context_aware = False

    def __init__(self, **options):
        super(self.__class__, self).__init__(**options)

    def build_model(self):

        print "Building rating matrix"
        self.user_item_matrix = self.build_rating_matrix(self.user_ids, self.user_events, self.item_ids)
        print "Computing weight matrix"
        self.weight_matrix = self.compute_weights(self.user_item_matrix)

        self.is_trained = True

    def build_rating_matrix(self, user_ids, user_events, item_ids):
        # build rating matrix
        user_item_matrix = np.zeros((len(user_ids),len(item_ids)),dtype=np.float32)

        for user_id, i in user_ids.items():
            ratings = self.compute_ratings(user_events[user_id])

            for item_id, j in item_ids.items():
                user_item_matrix[i][j] = ratings[item_id]

        # normalize rows
        user_item_matrix = normalize_rows(user_item_matrix)

        return user_item_matrix

    def predict_ratings(self, user, include_known=False):
        X = self.user_item_matrix
        W = self.weight_matrix

        nusers,nitems = X.shape
        predictions = []
        neighbors = self.get_k_neighbors(user, self.k_neighbors)

        for item in xrange(nitems):
            avg_rating = np.mean(X[user])

            sum_weighted_var = 0
            sum_weights = 0

            # only predict unrated items
            if(X[user][item]) and not self.include_known:
                continue
            for neighbor in neighbors:
                user_rating = X[neighbor][item]
                if not user_rating:
                    continue
                avg_rating_neighbor = np.mean(X[neighbor])
                sum_weighted_var += (user_rating-avg_rating_neighbor)*W[user][neighbor]
                sum_weights += abs(W[user][neighbor])

            pred = avg_rating
            if sum_weights:
                pred += sum_weighted_var/sum_weights
                item_id = self.index_to_item_id(item)
                predictions.append((pred,item_id))

        predictions.sort(reverse=True)
        return predictions

    def get_k_neighbors(self, user, k=None):
        neighbors = self.weight_matrix[user].argsort().tolist()
        del neighbors[neighbors.index(user)]

        return neighbors[-k:]

    def top_k_recommendations(self, user_id, k=5, **kwargs):
        """Interface for generating recommendations"""

        if not self.is_trained:
            print """recommender is not trained yet. please run build_model first"""

        user_index = self.user_id_to_index(user_id)
        predictions = self.predict_ratings(user_index)
        predictions.sort(reverse=True)
        return predictions[:k]

    # def top_recommendations(self,user, k=5):
    #     neighbors = self.get_k_neighbors(user,k)
    #     user_weights = self.weight_matrix[user][neighbors]
    #     items = defaultdict(int)
    #     for neighbor,weight in zip(neighbors,user_weights):
    #         for item,rating in enumerate(self.user_item_matrix[neighbor]):
    #             if rating and not self.user_item_matrix[user][item]:
    #                 items[item] += rating*weight

    #     recommendations = sorted([(r,i) for i,r in items.items()], reverse=True)
    #     return recommendations

    def compute_ratings(self,events):

        ratings = defaultdict(int)
        for event in events:
            ratings[event.item_id] += 1

        return ratings

    def compute_weights(self, M, dist_fun=cosine_sim):
        nrows = M.shape[0]
        W = np.zeros((nrows,nrows))
        M = M

        for i in xrange(nrows):
            for j in xrange(i,nrows):
                if i == j:
                    W[i][j] = 1
                else:
                    d =  dist_fun(M[i], M[j])
                    W[i][j] = W[j][i] = d

            if i%10 == 0:
                print "progress: %d%%" % (100.0*i/nrows)

        return W

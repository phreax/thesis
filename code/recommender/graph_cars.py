from adapters.lastfm.models import *
import adapters.lastfm.item_adapter as item_adapter
import adapters.lastfm.tag_adapter as tag_adapter
from recommender.base import Base
from collections import defaultdict
import numpy as np
import math
import operator as op
import tags as taghelper
from serialize import *
from context import *
from numeric import *
from random_walk import *
from helper import *
import pickle
import networkx as nx
import itertools

class GraphCARS(Base):
    file_prefix = 'db/graph_cars'

    # default params
    query_weights = {
            "user": 0.5,
            "context": 0.5
    }

    factor_weights = {
            "user": 0.5,
            "user-context": 0.5,
            "tag": 0.0
    }

    include_known = False
    use_tod = True
    use_dow = True
    use_item_groups = False
    use_tags = False
    use_tag_relations = False
    use_context = True

    is_context_aware = True

    option_desc = {
            "use_tod":           "Use time of day context",
            "use_dow":           "Use day of week context",
            "use_item_groups":   "Use Artist to connect tracks",
            "use_tags":          "Use Artist Tags",
            "include_known":     "Include known tracks in recommendation",
            "query_weights":     "Query Weights",
            "factor_weights":    "Factor Wights",
            "use_tag_relations": "Include Tag Correlation Matrix",
            "use_context":       "Use Context"
    }

    def __init__(self, **options):
        super(self.__class__, self).__init__(**options)
        self.ctxabs = ContextAbstractor(use_tod=self.use_tod, use_dow=self.use_dow)

    def build_model(self):
        self.graph = self.build_graph(self.item_ids, self.user_ids, self.user_events, self.item_events)
        self.matrix = self.transition_matrix(self.graph)

    def build_graph(self, item_ids, user_ids, user_events, item_events):

        print "Building graph"
        print "#users: %d"%len(user_ids)
        print "#items: %d"%len(item_ids)
        print "#contexts: %d"%(self.ctxabs.dim)

        counter = itertools.count()

        graph = nx.DiGraph()
        user_nodes = {}
        item_nodes = {}
        user_context_nodes = defaultdict(dict)

        # add user nodes
        for user_id in user_ids:
            node = counter.next()
            graph.add_node(node, type="user", id=user_id)
            user_nodes[user_id] = node

        # add items nodes
        for item_id in item_ids:
            node = counter.next()
            graph.add_node(node, type="item", id=item_id)
            item_nodes[item_id] = node


        ncontextnodes = 0 
        if self.use_context:
            # add user-context nodes
            for user_id in user_ids:
                for event in user_events[user_id]:
                    ctx  = self.ctxabs.retrieve_context(event.local_timestamp)
                    if ctx not in user_context_nodes[user_id]:
                        node = counter.next()
                        user_context_nodes[user_id][ctx] = node
                        ncontextnodes+=1
                        graph.add_node(node, type="user_context", value=[user_id,ctx])
                    
        # outgoing user edges
        for user_id in user_ids:
            item_count = defaultdict(int)
            context_count = defaultdict(int)
            item_context_count = defaultdict(lambda: defaultdict(int))
            for event in user_events[user_id]:
                item_id = event.item_id
                item_count[item_id] += 1
                ctx  = self.ctxabs.retrieve_context(event.local_timestamp)
                item_context_count[item_id][ctx] += 1

            total_count = sum(item_count.values())
            user_node = user_nodes[user_id]

            # add user - item edges
            for item_id, count in item_count.items():
                item_node = item_nodes[item_id]
                weight = 0.0
                if total_count > 0:
                    weight = (float(count)/float(total_count))
                graph.add_edge(user_node, item_node, weight=weight)

            if self.use_context:
                # add item-item_context edges
                for item_id, context_count in item_context_count.items():
                    total_count = sum(count for count in context_count.values())
                    for ctx, count in context_count.items():
                        ctx_node = user_context_nodes[user_id][ctx]
                        weight = 0.0
                        if total_count > 0:
                            weight = (float(count)/float(total_count))
                        graph.add_edge(ctx_node, item_node, weight=weight)

        # outgoing item edges
        for item_id in item_ids:
            user_count = defaultdict(int)
            user_context_count = defaultdict(lambda: defaultdict(int))
            for event in item_events[item_id]:
                user_id = event.user_id
                user_count[user_id] += 1
                ctx  = self.ctxabs.retrieve_context(event.local_timestamp)
                user_context_count[user_id][ctx] += 1

            item_node = item_nodes[item_id]

            total_count = sum(user_count.values())

            # add item-user edges
            for user_id, count in user_count.items():
                user_node = user_nodes[user_id]
                weight = 0.0
                if total_count > 0:
                    weight = (float(count)/float(total_count))
                    weight *= self.factor_weights["user"]
                graph.add_edge(item_node, user_node, weight=weight)

            if self.use_context:
                # add item-user_context edges
                for user_id, context_count in user_context_count.items():
                    total_count = sum(count for count in context_count.values())
                    for ctx, count in context_count.items():
                        ctx_node = user_context_nodes[user_id][ctx]
                        weight = 0.0
                        if total_count > 0:
                            weight = (float(count)/float(total_count))
                        weight *= self.factor_weights["user-context"]
                        graph.add_edge(item_node, ctx_node, weight=weight)

        if self.use_item_groups:
            self.connect_item_groups(graph, item_nodes)

        if self.use_tags:
            self.add_tags(graph, item_nodes, counter)

        # map ids to nodes
        self.user_nodes  = user_nodes
        self.item_nodes = item_nodes
        self.user_context_nodes = user_context_nodes

        # map nodes to ids
        self.node_items = inverse_dict(item_nodes)
        self.node_users  = inverse_dict(user_nodes)

        print "#usercontextnodes: %d"%ncontextnodes

        return graph

    def add_tags(self, graph, item_nodes, counter):
        print "add tag nodes"
        taglist = tag_adapter.taglist()
        taggroups = tag_adapter.grouped_tags()
        item_tags = tag_adapter.item_tags(item_nodes.keys())

        tag_nodes = {}

        # add tag nodes
        for tag in taglist:
            node = counter.next()
            graph.add_node(node, type="tag", id=tag)
            tag_nodes[tag] = node

        # add item - tag relation
        for item_id, tags in item_tags.items():
            for tag, r in tags:
                item_node = item_nodes[item_id]
                tag_node = tag_nodes[tag]
                weight = r
                out_weight = r * self.factor_weights["tag"]
                graph.add_edge(tag_node, item_node, weight=weight)
                graph.add_edge(item_node, tag_node, weight=out_weight)


        
        print "#tagnodes = %d"%(len(tag_nodes))
        if self.use_tag_relations:
            nrelatedtags = 0
            C = taghelper.correlation_matrix(taggroups, taglist)
            M = taghelper.semantic_matrix(C, thres=0.3)


            for t1, t2 in itertools.combinations(xrange(len(taglist)), 2):
                tag_node1 = tag_nodes[taglist[t1]]
                tag_node2 = tag_nodes[taglist[t2]]

                weight = M[t1,t2]
                if weight > 0.0:
                    nrelatedtags += 1
                    graph.add_edge(tag_node1, tag_node2, weight=weight)
            print "#relatedtags = %d"%(nrelatedtags)

        self.tag_nodes = tag_nodes
        self.node_tags = inverse_dict(tag_nodes)

    def connect_item_groups(self, graph, item_nodes):
        print "connect item groups"
        item_ids = item_nodes.keys()
        grouped_items =  item_adapter.grouped_items(item_ids)
        for group in grouped_items.values():
            for item1 in group:
                for item2 in group:
                    if item1 != item2:
                        node1 = item_nodes[item1]
                        node2 = item_nodes[item2]
                        graph.add_edge(node1, node2, weight=1.0)
                        graph.add_edge(node2, node1, weight=1.0)

    def build_query_vector(self, user_id, context=None):
        """Initial vector for personalized PageRank.
           It gives higher probability to selected
           starting nodes.
        """
        n = self.matrix.shape[0]
        v = np.zeros((n,1))

        user_node = self.user_nodes[user_id]

        v[user_node] = self.query_weights["user"]

        if context:
            context_node = self.get_user_context_node(user_id, context)
            if context_node:
                v[context_node] = self.query_weights["context"]
                # print "user_index: %d\ncontext_index: %d"%(user_node, context_node)
        # else:
            # print "user_index: %d"%(user_node)

        return v

    def get_user_context_node(self, user_id, ctx):
        if user_id in self.user_context_nodes:
            if ctx in self.user_context_nodes[user_id]:
                return self.user_context_nodes[user_id][ctx]

        return None

    def item_scores(self, user_id, context, **kwargs):
        """get recommended items"""

        p = self.build_query_vector(user_id, context)

        pagerank_vector = pagerank_power(self.matrix, p)
        return self.select_items(pagerank_vector, user_id, **kwargs)

    def top_k_recommendations(self, user_id, k=5, **kwargs):
        """Interface for generating recommendations"""

        context = None
        if "context" in kwargs:
            context = kwargs["context"]
        elif "timestamp" in kwargs:
            timestamp = kwargs["timestamp"]
            context = self.ctxabs.retrieve_context(timestamp)

        include_known = self.include_known
        if "include_known" in kwargs:
            include_known = kwargs["include_known"]

        rankings = self.item_scores(user_id, context, include_known=include_known)
        rankings.sort(reverse=True)
        return rankings[:k]

    def select_items(self, pagerank_vector, user_id, include_known=False):
        user_node = self.user_nodes[user_id]

        items_to_select = set(self.item_nodes.values())
        min_value = 1.0/self.matrix.shape[0]
        if not include_known:
            items_to_select = [node for node in items_to_select if self.matrix[user_node, node] > min_value]
            # print "remove known items %d"%(len(self.item_nodes) - len(items_to_select))

        rankings = sorted([(pagerank_vector[node,0], item_id) for item_id, node in self.item_nodes.items() if node in items_to_select], reverse=True)


        return rankings

    def transition_matrix(self, graph):
        matrix = nx.to_numpy_matrix(graph)
        matrix = normalize_col_stochastic(matrix)
        return matrix

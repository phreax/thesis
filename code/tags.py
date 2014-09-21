from collections import defaultdict
import numpy as np
from numeric import normalize_rows
import networkx as nx
import pylab

def prepare_tags(item_tags):
    tags = tag_set(item_tags)
    mapping = normalize_tags(tags)
    item_tags = rename_tags(item_tags, mapping)
    item_tags = remove_unrelevant(item_tags)

    return item_tags

def correlation_matrix(item_tags, taglist):
    tag_indices = {t:i for i,t in enumerate(taglist)}
    tag_indices_inv = {i:t for i,t in enumerate(taglist)}

    n = len(taglist)
    print n
    R = np.zeros((n,n))
    freq = np.zeros(n)

    for tags in item_tags.values():
        for ti in tags:
            i = tag_indices[ti[0]]
            freq[i] += 1.0
            for tj in tags:
                if ti == tj:
                    continue
                j = tag_indices[tj[0]]
                R[i,j] += 1.0
                R[j,i] += 1.0

    # Jaccard distance
    C = R/freq
    return normalize_rows(C)

def semantic_matrix(correlations, thres=0.8):
    C = correlations.copy()
    n = C.shape[0]

    # remove all 
    for i in xrange(n):
        for j in xrange(n):
            v = C[i,j]
            C[i,j] = v if v >= thres else 0.0
    
    return C

def draw_semantic_graph(M, taglist):
    G = nx.from_numpy_matrix(M)

    pylab.figure()
    node_labels = dict(enumerate(taglist))
    G = nx.relabel_nodes(G,node_labels)
    edge_labels={(u,v):"%.2f"%(e['weight']*100.0)
                 for u,v,e in G.edges(data=True)}

    pos = nx.spring_layout(G)

    # nx.draw_networkx
    nx.draw_networkx_labels(G,pos,font_color="g", font_size=7)
    nx.draw_networkx_edges(G,pos)
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels, font_size=8)

    return G

def tag_set(item_tags):
    tags = set()
    process_tags(item_tags, lambda t: tags.add(t))
    return tags

def normalize_tags(tags):
    mapping = {}

    for t in tags:
        if t not in mapping:
            tnew = t.strip().lower().replace("-", " ")
            if t != tnew:
                mapping[t] = tnew

    return mapping

def process_tags(item_tags, func):
    """
        iterate over all item tags and change them using func.
        if func return a false value, it will be discarded.
    """
    item_tags_new = {}
    for item, tags in item_tags.items():
        tags_new = []
        used_tags = set()
        for t, r in tags:
            r = int(r)
            tnew = func(t)
            if tnew and tnew not in used_tags:
                tags_new.append([tnew,r])
                used_tags.add(tnew)
        item_tags_new[item] = tags_new

    return item_tags_new

def rename_tags(item_tags, mapping):
    def rename_func(t):
        if t in mapping:
            return mapping[t]
        return t
    return process_tags(item_tags, rename_func)

def tag_history(item_tags):

    history = defaultdict(int)
    for item, tags in item_tags.items():
        for t, r in tags:
            history[t] += 1

    return history

def remove_unrelevant(item_tags, thres = 2):
    history = tag_history(item_tags)

    unrelevant_tags = set(["under 2000 listeners", "all"])

    def discard_func(t):
        if t in unrelevant_tags:
            return
        if history[t] >= thres:
            return t

    return process_tags(item_tags, discard_func)


def make_graph_from_tags(item_tags, corr_thres=0.5):
    tag_names = tag_set(item_tags)

    C = correlation_matrix(item_tags, tag_names)
    M = semantic_matrix(C, corr_thres)
    return draw_semantic_graph(M, tag_names)

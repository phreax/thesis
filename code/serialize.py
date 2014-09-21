import json
import pickle

def save_json(filename, obj):
    s = json.dumps(obj)
    f = open(filename,'w')
    f.write(s+'\n')
    f.close()

def load_json(filename):
    f = open(filename,'r')
    obj = json.loads(f.read())
    f.close()
    return obj

def save_pickle(filename,obj):
    f = open(filename,'w')
    pickle.dump(obj,f)
    f.close()

def load_pickle(filename):
    f = open(filename, 'r')
    obj = pickle.load(f)
    f.close()
    return obj

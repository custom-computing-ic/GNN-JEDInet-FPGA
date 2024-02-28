from heterograph import *

# check HGraph code:
#   https://github.com/custom-computing-ic/heterograph/blob/main/heterograph/hgraph.py#L273

g = HGraph()  # create graph

# create graph
g.add_vx(4)
g.add_edge(0, [1, 2])
g.add_edge([1,2], 3)

def label_id(i):
    return chr(ord('a') + i)

# Record/MRecord shape:
# https://renenyffenegger.ch/notes/tools/Graphviz/elems/node/main-types/record-based
g.vstyle['shape'] = 'Mrecord' # default, no need to specify it.
g.vstyle['label'] = lambda g, v: "%d | { %s |  { %s | %s } } " % (v, label_id(v), str(g.in_vx(v)), str(g.out_vx(v)))

g.view()
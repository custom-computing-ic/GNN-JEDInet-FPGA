from heterograph import *

# check HGraph code:
#   https://github.com/custom-computing-ic/heterograph/blob/main/heterograph/hgraph.py#L273

g = HGraph()  # create graph

# create graph
g.add_vx(3)
g.add_edge(0, [1, 2])

# dynamic attributes: just specify a lambda that returns a string for attributes that change

# example: v is the vertex id, convert number to alpha: 0=>a, 1=>b, etc.
def label_id(i):
    return chr(ord('a') + i)

g.vstyle['fillcolor'] = 'green' # constant for all nodes
# label changes with each node
g.vstyle['label'] = lambda g, v: label_id(v)
# edge changes with each node
g.estyle['label'] = lambda g, e: f"[{label_id(e[0])} :: {label_id(e[1])}]"

g.view()
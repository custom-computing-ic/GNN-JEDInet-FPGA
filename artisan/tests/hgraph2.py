from heterograph import *

# check HGraph code:
#   https://github.com/custom-computing-ic/heterograph/blob/main/heterograph/hgraph.py#L273

g = HGraph()  # create graph

# create graph
g.add_vx(2)
g.add_edge(0, 1)

# print default graph/vertex/edge style:

# graph attributes: https://graphviz.org/docs/graph/
print(g.style)

# node attributes: https://graphviz.org/docs/nodes/
print(g.vstyle)

# edge attributes: https://graphviz.org/docs/edges/
print(g.estyle)

# the following sets *static* style attributes
# note: we always update attribute values.
# To clear all attributes: g.[v|e]style=None.

# note attribute values must be string
g.vstyle = {'fillcolor': '#660000', 'fontcolor': '#FFFFFF', 'shape': 'rectangle', 'label': 'node'}
g.estyle = {'style': 'dashed', 'penwidth': '4', 'label': 'edge'}

g.view()
from heterograph import *

# check HGraph code:
#   https://github.com/custom-computing-ic/heterograph/blob/main/heterograph/hgraph.py#L273

g = HGraph()  # create graph

# every vertex has an identifier, which is an integer

id = g.add_vx() # add one vertex
print(id)  
ids = g.add_vx(2) # add two more vertices
print(ids)

g.add_vx(2)

g.add_edge(0, [1,2])
g.add_edge([1,2], 3)
g.add_edge(3, 4)
# g.rm_vx(4)
# g.rm_edge((2, 3))
g.view()


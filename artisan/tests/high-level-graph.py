import artisan as art
import heterograph as hgr
import sys

def build_graph(main_func):
  g = hgr.HGraph()
  calls = main_func.query('call{CallExpr}', where = lambda call: len(call.children) > 0)
  # print(calls)

  ids = []
  for i, row in enumerate(calls):
    id = g.add_vx()
    g.pmap[id]['func'] = row.call
    ids.append(id)

    if i > 0:
      g.add_edge(ids[i-1], id)
  return g
  
  
def get_array_args(graph):
  for vx in graph.vertices:
    call = graph.pmap[vx]['func']
    print(call.name)
    print([arg.unparse() for arg in call.args])
    """
    Pseudocode:
    1. collect all arrays in a list
    2. Figure out cyclic factors for all of them (len of second dimension)
    3. If only one dim, or lower than a threshold size, use complete
    4. Insert pragmas
    """

name_main_func = "jedi"
if len(sys.argv) > 1:
  name_main_func = sys.argv[1]

# include: relative path to jedi50p_baseline_u1/ (workdir)
ast = art.Ast("../../jedi50p_baseline_u1/jedi.cpp -I ../artisan/include")

main_fn = ast.query('fn{FunctionDecl}', where=lambda fn: fn.name == name_main_func)

graph = build_graph(main_fn[0].fn)
get_array_args(graph)

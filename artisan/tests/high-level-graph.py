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
  
  


name_main_func = "jedi"
if len(sys.argv) > 1:
  name_main_func = sys.argv[1]

# include: relative path to jedi50p_baseline_u1/ (workdir)
ast = art.Ast("../../jedi50p_baseline_u1/jedi.cpp -I ../artisan/include")

main_fn = ast.query('fn{FunctionDecl}', where=lambda fn: fn.name == name_main_func)

build_graph(main_fn[0].fn)

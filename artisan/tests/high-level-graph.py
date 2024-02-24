import artisan as art
import heterograph as hgr
import sys
import yaml

ASSUME = 'assume'
TASKS = 'tasks'
INPUTS = 'inputs'
OUTPUTS = 'outputs'

DATAFLOW = 'dataflow'

def build_graph(main_func, tasks):
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

def _check_dataflow(ast):  
  ast.parse_pragmas(rules=[lambda pragma: "node"])
  table = ast.query("node{node}", where=lambda node: node.pragmas is not None)

  for row in table:    
    for pragma in row.node.pragmas:
      words = pragma[0]      
      if len(words) > 1 and DATAFLOW.casefold() == words[1].casefold():
        return True
  return False

def build_dataflow_graph(config_file, name_main_fn, ast, main_func):
  with open(config_file, 'r') as file:
    config = yaml.safe_load(file)
    if name_main_fn in config:
      main_config = config[name_main_fn]

      assumptions = main_config[ASSUME]
      for assumption in assumptions:
        if assumption == DATAFLOW:
          if (not _check_dataflow(ast)):
            print(f"[Info] No dataflow design found. Exiting graph generation.")
            return None
      
      tasks = main_config[TASKS]
      graph = build_graph(main_func, tasks)

    else:
      print(f"[Error] '{name_main_fn}' not found in config file {config_file}")
    
  
  
def get_array_args(graph):
  arrays = set()
  # arrays used in function calls
  for vx in graph.vertices:
    call = graph.pmap[vx]['func']
    # print(call.name)
    # print([arg.unparse() for arg in call.args])
    for arg in call.args:
      arrays.add(arg.unparse())

  return arrays

def filter_array_defined(main_func, arrays):

  def is_array(shape):        
    return shape.dim is not None
  
  decls = main_func.query('decl{DeclStmt}={1}>var{VarDecl}')
  defined = set()
  for row in decls:   
    name =  row.var.name        
    if name in arrays and is_array(row.var.shape):
      defined.add(row.var.name)
  print(defined)
  return defined

  # arrays declared in this scope

  """
  Pseudocode:
  1. collect all arrays in a list
  2. Figure out cyclic factors for all of them (len of second dimension)
  3. If only one dim, or lower than a threshold size, use complete
  4. Insert pragmas
  """

name_main_func = "jedi"
config = "config.yml"
if len(sys.argv) > 1:
  name_main_func = sys.argv[1]

if len(sys.argv) > 2:
  config = sys.argv[2]

# include: relative path to jedi50p_baseline_u1/ (workdir)
ast = art.Ast("../../jedi50p_baseline_u1/jedi.cpp -I ../artisan/include")

main_fn = ast.query('fn{FunctionDecl}', where=lambda fn: fn.name == name_main_func)

df_graph = build_dataflow_graph(config, name_main_func, ast, main_fn[0].fn)

graph = build_graph(main_fn[0].fn)
arrays = filter_array_defined(main_fn[0].fn, get_array_args(graph))



import artisan as art
import heterograph as hgr
import sys
import yaml
import parseTaskData as parse
import matplotlib.pyplot as plt
import matplotlib.colors as clrs

ASSUME = 'assume'
TASKS = 'tasks'
INPUTS = 'inputs'
OUTPUTS = 'outputs'

DATAFLOW = 'dataflow'

keysToReplicas = {}
def _gen_next_name(name):
  if name in keysToReplicas:
    keysToReplicas[name] += 1
    return f"{name} {keysToReplicas[name]}"
  keysToReplicas[name] = 2
  return f"{name} 2"

def _float_to_color(number, min=0, max=1):
  color_map = plt.get_cmap('coolwarm')
  if max - min == 0:
    float_value = number
  else:
    float_value = number / (max - min)  
  rgba = color_map(float_value)  
  hsv = clrs.rgb_to_hsv(rgba[:3])  
  return tuple(hsv)

NAME = 'name'
FUNC = 'func'
REPORT = 'report'
MAXES = 'maxes'
MINS = 'mins'
TOTAL = 'total'
II = 'interval_max'
LATENCY = 'worst_case_latency'

def _set_style_for_metric(g, metric):
  g.vstyle['label'] = lambda gr, v_id: "%s | { %s } " % (gr.pmap[v_id][NAME], gr.pmap[v_id][REPORT][metric])
  g.style['label'] = metric
  g.vstyle['fillcolor'] = lambda gr, v_id: "%f %f %f" % _float_to_color(int(gr.pmap[v_id][REPORT][metric]), gr.pmap[MINS][metric], gr.pmap[MAXES][metric])

def _set_style_for_all_metrics(g, metric=LATENCY):
  g.vstyle['label'] = lambda gr, v_id: "%s | { lat: %s | ii: %s | DSP: %s | FF: %s | LUT: %s} " % (gr.pmap[v_id][NAME], gr.pmap[v_id][REPORT]['average_case_latency'],
                                                                                         gr.pmap[v_id][REPORT]['interval_max'], gr.pmap[v_id][REPORT]['DSP48E'],
                                                                                         gr.pmap[v_id][REPORT]['FF'], gr.pmap[v_id][REPORT]['LUT'])
  g.style['label'] = lambda gr: f"Tot. II: {gr.pmap[TOTAL][II]}\nTot. Latency: {gr.pmap[TOTAL][LATENCY]}"
  g.vstyle['fillcolor'] = lambda gr, v_id: "%f %f %f" % _float_to_color(int(gr.pmap[v_id][REPORT][metric]), gr.pmap[MINS][metric], gr.pmap[MAXES][metric])

def _create_graph_for_all_metrics(g, folder="graphs"):
  metrics = g.pmap[MAXES].keys()
  for metric in metrics:
    _set_style_for_metric(g, metric)
    g.render(filename=f"{folder}/{metric}")

def build_graph(main_func, name_main_fn, tasks, report_dir):  

  g = hgr.HGraph()  
  _set_style_for_all_metrics(g)
  # g.vstyle['label'] = lambda gr, v_id: gr.pmap[v_id][NAME] 
  calls = main_func.query('call{CallExpr}', where = lambda call: len(call.children) > 0)    

  keysToIds = {}
  for task in tasks:
    for k in task:
      key = k
      if k in keysToIds:
        # duplicate use of the same task
        key = _gen_next_name(k)
      keysToIds[key] = id = g.add_vx()
      g.pmap[id][NAME] = key   
      g.pmap[id][INPUTS] = task[k][INPUTS]
      g.pmap[id][OUTPUTS] = task[k][OUTPUTS]
        
  used = {}
  reports, maxes, mins = parse.parseReportForTasks(keysToIds.keys(), name_main_fn, report_dir)

  g.pmap[TOTAL] = parse.parseOverallReport(name_main_fn, report_dir)
  
  g.pmap[MAXES] = maxes
  g.pmap[MINS] = mins
  for key in keysToIds.keys():    
    used[key] = False

  for i, row in enumerate(calls):
    assigned = False
    assignedName = ""    
    for name in keysToIds.keys():
      if not used[name] and row.call.name in name:
        used[name] = True
        assigned = True
        assignedName = name
        id = keysToIds[name]
        g.pmap[id][FUNC] = row.call
        g.pmap[id][REPORT] = reports[name]
        break
    if not assigned:      
      print(f"[Warning] Function '{row.call.unparse()}' not found in config. " + 
      "It will not be added to the dataflow graph.")
      continue   
    
    id = keysToIds[assignedName]
    outputs = g.pmap[id][OUTPUTS]
    for output in outputs:
      for other_id in keysToIds.values():
        if output in g.pmap[other_id][INPUTS]:
          g.add_edge(id, other_id)

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

def build_dataflow_graph(config_file, name_main_fn, ast, main_func, report_dir):
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
      graph = build_graph(main_func, name_main_fn, tasks, report_dir)
      return graph

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
  # print(defined)
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
# ast = art.Ast("../../jedi50p_baseline_u1/jedi.cpp -I ../artisan/include")
# report_dir = "/mnt/ccnas2/bdp/ad4220/GNN-JEDInet-FPGA/jedi_folded_2/prj_cmd01/jedi_prj/solution1/syn/report"

path = "/mnt/ccnas2/bdp/ad4220/hls4ml-tutorial/model1/hls4ml_prj_df/firmware/"
report_dir = "/mnt/ccnas2/bdp/ad4220/hls4ml-tutorial/model1/hls4ml_prj_df/myproject_prj/solution1/syn/report"
ast = art.Ast(f"{path}myproject.cpp -I {path}ap_types/")

main_fn = ast.query('fn{FunctionDecl}', where=lambda fn: fn.name == name_main_func)

df_graph = build_dataflow_graph(config, name_main_func, ast, main_fn[0].fn, report_dir)

# graph = build_graph(main_fn[0].fn, [])
# df_graph.render()
# _create_graph_for_all_metrics(df_graph)
df_graph.view()
# graph.view()
# arrays = filter_array_defined(main_fn[0].fn, get_array_args(graph))


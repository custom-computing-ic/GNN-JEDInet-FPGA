import sys
from xmltodict import parse
from typing import Dict, List, Optional
from os import listdir
import matplotlib.pyplot as plt

CSYNTH = "_csynth"

def parseTask(name, report_dir, filename):  

  if filename is None:
    print(f"Report not found for task '{name}'")
    return None

  with open(f'{report_dir}/{filename}', 'r') as file:
            layer_report = parse(file.read())['profile']

            latency_report = layer_report["PerformanceEstimates"]["SummaryOfOverallLatency"]
            available_report = layer_report["AreaEstimates"]["AvailableResources"]
            output_report =  {
                "best_case_latency": latency_report["Best-caseLatency"],
                "average_case_latency": latency_report["Average-caseLatency"],
                "worst_case_latency": latency_report["Worst-caseLatency"],
                "interval_min": latency_report["Interval-min"],
                "interval_max": latency_report["Interval-max"],
                "available_BRAM_18K": available_report["BRAM_18K"],
                "available_DSP48E": available_report["DSP48E"],
                "available_FF": available_report["FF"],
                "available_LUT": available_report["LUT"]
            }

            resource_report = dict(layer_report["AreaEstimates"]["Resources"])
            output_report.update(resource_report)

            return output_report


def parseReportForTasks(tasks, project_name, report_dir):
  modules = parseModuleList(project_name, report_dir)  
  filenames = _matchModules(tasks, modules)  
  reports = {}
  maxes = {}
  mins = {}
  for task in tasks:
    
    report = parseTask(task, report_dir, f"{filenames[task]}{CSYNTH}.xml")
    if report is None:
      continue
    reports[task] = report

    for metric in report.keys():
      val = float(report[metric].split()[0])
      if metric not in maxes:
        maxes[metric] = val
        mins[metric] = val
        continue

      if maxes[metric] < val:
        maxes[metric] = val
      if mins[metric] > val:
        mins[metric] = val

  return reports, maxes, mins

def _matchModules(tasks, modules):
  filenames = {}
  for task in tasks:
    mods = [module for module in modules if task in module]
    if len(mods) == 0:
      continue
    mods = sorted(mods, key=_moduleRank)
    relevant_tasks = [t for t in tasks if task in t]
    name = task
    for i, mod in enumerate(mods):
      filenames[relevant_tasks[i]] = mod
      
  return filenames

def _moduleRank(module):
  parts = module.split("_")
  # Not sure if this is correct, need to test
  config = parts[-2]
  num_start = 0
  for c in config:
    if c.isdigit():
      break
    num_start += 1
  if len(config) == num_start:
    return -1
  return int(config[num_start:])

def _extractModule(line):  
  parts = line.split("|")    
  # to extract the name under the 'Module' column in the report
  return parts[2].strip()

def parseModuleList(project_name, report_dir):  
  START = 39
  report = f"{report_dir}/{project_name}{CSYNTH}.rpt"
  with open(report, 'r') as report_file:
    start = ""
    modules = []
    for pos, line in enumerate(report_file):
      if pos < START:
        continue
      if pos == START:
        start = line
        continue
      if line == start:
        return modules
      modules.append(_extractModule(line))


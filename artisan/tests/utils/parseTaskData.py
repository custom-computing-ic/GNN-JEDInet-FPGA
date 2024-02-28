import sys
from xmltodict import parse
from typing import Dict, List, Optional
from os import listdir
import matplotlib.pyplot as plt

def parseTask(name, report_dir):
  files = listdir(report_dir)
  files = [file for file in files if file[-4:] == ".xml"]

  filename = None
  for file in files:
    if name in file:
      filename = file
      break

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


def parseReportForTasks(tasks, report_dir):
  reports = {}
  for task in tasks:
    report = parseTask(task, report_dir)
    if report is not None:
      reports[task] = report
  return report

"""Reproducible traversal-only benchmark; no results are assumed in advance."""
import json, platform, statistics, time
from pathlib import Path
import networkx as nx
from graph_validation.tracing import trace_downstream_with_metrics
ROOT=Path(__file__).resolve().parents[1]
raw=json.loads((ROOT/'photon_sprint1_graph_data.json').read_text(encoding='utf-8'))
g=nx.DiGraph()
for cat in ('suppliers','parts','products','orders'):
    for n in raw['nodes'][cat]: g.add_node(n['id'],**n)
for cat in ('supplies','used_in','fulfills'):
    for e in raw['edges'][cat]: g.add_edge(e['source'],e['target'],**e)
source='SUP-01'; iterations=1000; warmups=100; threshold=10.0
for _ in range(warmups): trace_downstream_with_metrics(g,source,threshold)
times=[trace_downstream_with_metrics(g,source,threshold)['traversal_elapsed_ms'] for _ in range(iterations)]
sorted_times=sorted(times); p95=sorted_times[min(len(times)-1, int(.95*len(times)))]
report={'measurement':'NetworkX descendants traversal only; excludes graph loading, validation, HTTP and rendering','python_version':platform.python_version(),'platform':platform.platform(),'networkx_version':nx.__version__,'node_count':g.number_of_nodes(),'edge_count':g.number_of_edges(),'source_node':source,'iterations':iterations,'warmup_iterations':warmups,'threshold_ms':threshold,'mean_ms':statistics.mean(times),'median_ms':statistics.median(times),'min_ms':min(times),'max_ms':max(times),'p95_ms':p95,'median_under_10ms':statistics.median(times)<threshold,'all_iterations_under_10ms':max(times)<threshold}
out=ROOT/'reports'/'tracing_benchmark_report.json'; out.write_text(json.dumps(report,indent=2)+'\\n',encoding='utf-8')
print(json.dumps(report,indent=2)); print(f'Report: {out}')

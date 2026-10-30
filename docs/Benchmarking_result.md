Graph loaded: 19 nodes, 21 edges.
Running benchmark on nodes: ['SUP-01', 'SUP-02']
Warmup runs: 50 | Measured runs: 1000 | Threshold: < 10.0 ms

============================================================================
  TEAM PHOTON — DOWNSTREAM TRACING BENCHMARK RESULTS
============================================================================
  Overall Status : [PASS]
  Target Nodes   : SUP-01, SUP-02
  Total Runs     : 2000
  Threshold      : < 10.0 ms (Criterion: p95 <= 10.0 ms)
----------------------------------------------------------------------------
  Min Latency    :   0.0119 ms
  Mean Latency   :   0.0198 ms
  Median (p50)   :   0.0235 ms
  90th Percentile:   0.0254 ms
  95th Percentile:   0.0265 ms  (Target: < 10.0 ms)
  99th Percentile:   0.0450 ms
  Max Latency    :   0.0952 ms
----------------------------------------------------------------------------
  Node SUP-01   | p95: 0.0276 ms | mean: 0.0145 ms | [PASS] (descendants: 10)
  Node SUP-02   | p95: 0.0264 ms | mean: 0.0251 ms | [PASS] (descendants: 15)
============================================================================
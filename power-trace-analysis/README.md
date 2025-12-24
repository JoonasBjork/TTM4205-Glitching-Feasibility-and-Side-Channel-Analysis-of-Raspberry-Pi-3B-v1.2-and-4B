# Power Trace Analysis

## Compare Sleep and Heavy Computation

This directory contains the code for analyzing differences between sections of heavy computation and sleeping in traces. The `extract-trace-periods.py` script extracts computation periods and metrics for each computation period within traces. `compare-trace-features.ipynb` uses these extracted metrics and performs statistical tests on the data to find differences between periods of computation.
#!/usr/bin/env python3
import glob
import numpy as np
from scipy.signal import hilbert, welch
from scipy.stats import entropy
import csv

def split_traces_into_sections(traces, threshold, cluster_max_len=500):
    first_sections, second_sections, third_sections, fourth_sections, fifth_sections = [], [], [], [], []
    ignored_traces = 0

    for trace_idx, t in enumerate(traces):
        N = len(t)
        i = 0
        trigger_clusters = []

        while i < N:
            if abs(t[i]) > threshold:
                cluster_end = i
                for j in range(i, min(i + cluster_max_len, N)):
                    if abs(t[j]) > threshold:
                        cluster_end = j
                trigger_clusters.append((i, cluster_end))
                i = cluster_end + 1
            else:
                i += 1

        if len(trigger_clusters) != 6:
            print(f"Trace {trace_idx} has {len(trigger_clusters)} trigger clusters (expected 6). Skipping.")
            ignored_traces += 1
            continue

        sec1_start = trigger_clusters[0][1] + 1
        sec1_end   = trigger_clusters[1][0]
        sec2_start = trigger_clusters[1][1] + 1
        sec2_end   = trigger_clusters[2][0]
        sec3_start = trigger_clusters[2][1] + 1
        sec3_end   = trigger_clusters[3][0]
        sec4_start = trigger_clusters[3][1] + 1
        sec4_end   = trigger_clusters[4][0]
        sec5_start = trigger_clusters[4][1] + 1
        sec5_end   = trigger_clusters[5][0]

        first_sections.append(t[sec1_start:sec1_end])
        second_sections.append(t[sec2_start:sec2_end])
        third_sections.append(t[sec3_start:sec3_end])
        fourth_sections.append(t[sec4_start:sec4_end])
        fifth_sections.append(t[sec5_start:sec5_end])

    print(f"In total, ignored {ignored_traces} traces")
    return first_sections, second_sections, third_sections, fourth_sections, fifth_sections

def mad_sigma(x):
    return 1.4826 * np.median(np.abs(x - np.median(x)))

def rolling_rms(x, W):
    c = np.convolve(x*x, np.ones(W), mode='valid') / W
    return np.sqrt(c)

def analyze_traces(traces, W_samples=500, trace_freq=200e6):
    """Compute metrics for an array of traces (N x L)"""
    N, L = traces.shape
    pre = traces[:, :max(1, L//20)]
    baseline = pre.mean(axis=1, keepdims=True)
    X = traces - baseline
    sigmas = np.array([mad_sigma(x[:L//20]) for x in X])
    thr = 4 * sigmas

    metrics = {}

    # A bunch of AI-gnerated metrics! These have been selected in a trial-and-error fashion i.e. take many metrics and try to see if there is a difference between heavy computation and sleep. If there is, try to explain why. 

    # Indicates how much "activity" there is in the trace
    metrics['rms_mean']    = np.array([rolling_rms(x, W_samples).mean() for x in X]) # average signal energy

    # How large the oscillations in the signal are over time
    metrics['env_mean']    = np.array([np.abs(hilbert(x)).mean() for x in X]) # average signal envelope (amplitude)

    # Number of samples that surpass a dynamic threshold (uses median absolute deviation)
    metrics['peak_count']  = np.array([np.sum(np.abs(x) > t) for x,t in zip(X, sigmas*4)]) # number of large deviations

    # Mean is not meaningful
    metrics['mean']        = np.mean(X, axis=1)

    # Median indicates if the normal value is higher or lower
    metrics['median']      = np.median(X, axis=1) # robust central tendency

    # Measure of variability (More robust than standard deviation)
    metrics['mad']         = np.array([mad_sigma(x) for x in X]) # robust variability, less sensitive to spikes

    # Measures how fast the signal changes from one sample to the next
    metrics['rms_diff']    = np.array([np.sqrt(np.mean(np.diff(x)**2)) for x in X]) # high-frequency activity proxy

    # Measures how wide the middle 50% of the data is (i.e. discards outliers)
    metrics['iqr']         = np.array([np.percentile(x, 75) - np.percentile(x, 25) for x in X]) # interquartile range for robust spread

    # Measures if there are more extreme values on the positive or negative side
    metrics['skew']        = np.array([np.mean((x - np.mean(x))**3)/np.std(x)**3 for x in X]) # asymmetry of fluctuations

    # The tailedness of the distribution
    metrics['kurtosis']    = np.array([np.mean((x - np.mean(x))**4)/np.std(x)**4 - 3 for x in X]) # peakedness of distribution

    # How many times zero is crossed, indicates noise and randomness
    metrics['zero_crossing'] = np.array([np.sum(np.diff(np.sign(x)) != 0) for x in X]) # frequency of small fluctuations

    # Average absolute difference between consecutive samples 
    metrics['mean_abs_diff'] = np.array([np.mean(np.abs(np.diff(x))) for x in X]) # average step-to-step change

    # PSD-based metrics
    psd_freqs, psd_vals = zip(*[welch(x, fs=trace_freq, nperseg=min(1024, len(x))) for x in X])
    psd_vals = np.array(psd_vals)
    metrics['psd_mean'] = psd_vals.mean(axis=1)                 # overall spectral energy
    metrics['psd_high_ratio'] = np.array([np.sum(p[f>trace_freq/4])/np.sum(p) for p,f in zip(psd_vals, psd_freqs)])  # high-frequency content ratio

    # Entropy-based metrics
    metrics['shannon_entropy'] = np.array([entropy(np.histogram(x, bins=50, density=True)[0] + 1e-12) for x in X])  # signal complexity

    return metrics

def convert_to_builtin(obj):
    if isinstance(obj, dict):
        return {k: convert_to_builtin(v) for k,v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_builtin(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj

# ----------------------------
# Main Processing
# ----------------------------

def process_directory(path_pattern, threshold):
    trace_files = sorted(glob.glob(path_pattern))
    if len(trace_files) == 0:
        return None

    traces = np.array([np.loadtxt(f) for f in trace_files])

    first, second, third, fourth, fifth = split_traces_into_sections(traces, threshold)
    if len(first) == 0:
        return None

    # Trim to minimum section length
    first_min = min(len(t) for t in first)
    second_min = min(len(t) for t in second)
    third_min = min(len(t) for t in third)
    fourth_min = min(len(t) for t in fourth)
    fifth_min = min(len(t) for t in fifth)

    cutoff = min(first_min, second_min, third_min, fourth_min, fifth_min)

    print(f"Min samples in each: {first_min}, {second_min}, {third_min}, {fourth_min}, {fifth_min}\nTaking {cutoff} elements from first, second, third, fourth, and fifth")

    first_array = np.array([t[:cutoff] for t in first])
    second_array = np.array([t[:cutoff] for t in second])
    third_array = np.array([t[:cutoff] for t in third])
    fourth_array = np.array([t[:cutoff] for t in fourth])
    fifth_array = np.array([t[:cutoff] for t in fifth])

    # Analyze traces
    metrics_first = analyze_traces(first_array)
    metrics_second = analyze_traces(second_array)
    metrics_third = analyze_traces(third_array)
    metrics_fourth = analyze_traces(fourth_array)
    metrics_fifth = analyze_traces(fifth_array)

    # Prepare per-trace dictionary
    per_trace = {}
    for metric_name in metrics_first.keys():
        per_trace[metric_name] = {
            "heavy_1": metrics_first[metric_name].tolist(),
            "sleep_1": metrics_second[metric_name].tolist(),
            "heavy_2": metrics_third[metric_name].tolist(),
            "sleep_2": metrics_fourth[metric_name].tolist(),
            "heavy_3": metrics_fifth[metric_name].tolist()
        }

    # Prepare aggregated dictionary
    aggregated = {}
    for metric_name in metrics_first.keys():
        aggregated[metric_name] = {
            "mean": {
                "heavy_1": float(np.mean(metrics_first[metric_name])),
                "sleep_1": float(np.mean(metrics_second[metric_name])),
                "heavy_2": float(np.mean(metrics_third[metric_name])),
                "sleep_2": float(np.mean(metrics_fourth[metric_name])),
                "heavy_3": float(np.mean(metrics_fifth[metric_name]))
            },
            # Remove the other metrics to simplify comparisons. May still be useful for the future.

            # "median": {
            #     "first": float(np.median(metrics_first[metric_name])),
            #     "second": float(np.median(metrics_second[metric_name])),
            #     "third": float(np.median(metrics_third[metric_name]))
            # },
            # "std": {
            #     "first": float(np.std(metrics_first[metric_name])),
            #     "second": float(np.std(metrics_second[metric_name])),
            #     "third": float(np.std(metrics_third[metric_name]))
            # },
            # "min": {
            #     "first": float(np.min(metrics_first[metric_name])),
            #     "second": float(np.min(metrics_second[metric_name])),
            #     "third": float(np.min(metrics_third[metric_name]))
            # },
            # "max": {
            #     "first": float(np.max(metrics_first[metric_name])),
            #     "second": float(np.max(metrics_second[metric_name])),
            #     "third": float(np.max(metrics_third[metric_name]))
            # }
        }

    return aggregated, per_trace

def main(directory_patterns):
    all_aggregated = {}
    all_per_trace = {}
    for idx, pattern in enumerate(directory_patterns):
        print(f"{idx}/{len(directory_patterns)} Processing: {pattern[0]}")
        aggregated, per_trace = process_directory(pattern[0], pattern[1])
        if aggregated is not None:
            all_aggregated[pattern[0]] = aggregated
            all_per_trace[pattern[0]] = per_trace
    return all_aggregated, all_per_trace


if __name__ == "__main__":
    # Contains the filename, threshold per file, and the capacitor's category
    directories = [
        # Category 1
        ("../../new-traces/sleep-computation-comparison/C14/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C15/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C16/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C18/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C21/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C29/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C31/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C33/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C42/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C43/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C45/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C48/trace_*.csv", 0.4, "category_1"),
        ("../../new-traces/sleep-computation-comparison/C53/trace_*.csv", 0.4, "category_1"),

        # Category 2
        ("../../new-traces/sleep-computation-comparison/C19/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C20/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C23/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C30/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C32/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C34/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C35/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C44/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C46/trace_*.csv", 0.035, "category_2"),
        ("../../new-traces/sleep-computation-comparison/C47/trace_*.csv", 0.035, "category_2"),

        # outlier
        ("../../new-traces/sleep-computation-comparison/C22/trace_*.csv", 0.2, "category_3")
    ]

    aggregated_metrics, per_trace_metrics = main(directories)

    aggregated_metrics_rows = []
    for filename, file_data in aggregated_metrics.items():
        category = list(filter(lambda x: x[0] == filename, directories))[0][2]
        for per_trace_metric_name, per_trace_metric_data in file_data.items():
            for combined_metric_name, combined_metric_data in per_trace_metric_data.items():
                for section_name, section_data in combined_metric_data.items():
                    aggregated_metrics_rows.append([
                        filename, 
                        filename.split("sleep-computation-comparison/")[1].split("/")[0],
                        combined_metric_name, 
                        per_trace_metric_name, 
                        section_name, 
                        section_data,
                        category
                    ])

    with open("data/aggregated_metrics.csv", "w") as f:
        writer = csv.writer(
            f
        )
        writer.writerow([
            'filename', 
            'capacitor_name', 
            'combined_metric', 
            'per_trace_metric', 
            'trace_section', 
            'value', 
            'category'
        ])
        writer.writerows(aggregated_metrics_rows)

    per_trace_metric_rows = []

    for filename, file_data in per_trace_metrics.items():
        category = list(filter(lambda x: x[0] == filename, directories))[0][2]
        for per_trace_metric_name, per_trace_metric_data in file_data.items():
            for section_name, section_data in per_trace_metric_data.items():
                    for value_idx, value in enumerate(section_data):
                        per_trace_metric_rows.append([
                            filename,
                            filename.split("sleep-computation-comparison/")[1].split("/")[0],
                            per_trace_metric_name,
                            section_name,
                            value_idx,
                            value,
                            category
                        ])

    with open("data/per_trace_metrics.csv", "w") as f:
        writer = csv.writer(
            f
        )
        writer.writerow([
            'filename', 
            'capacitor_name', 
            'per_trace_metric', 
            'trace_section', 
            'trace_idx', 
            'value', 
            'category'
        ])
        writer.writerows(per_trace_metric_rows)

    print("Saved aggregated_metrics.csv and per_trace_metrics.csv")

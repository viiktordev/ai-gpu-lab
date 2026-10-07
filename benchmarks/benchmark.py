#!/usr/bin/env python3

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request


DEFAULT_OLLAMA_URL = "http://localhost:11434"


def generate(ollama_url: str, model: str, prompt: str) -> dict:
    url = f"{ollama_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started_at = time.perf_counter()

    with request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))

    client_duration = time.perf_counter() - started_at

    result["_client_duration_seconds"] = client_duration

    return result


def ns_to_seconds(value: int) -> float:
    return value / 1_000_000_000


def calculate_metrics(result: dict) -> dict:
    eval_count = result.get("eval_count", 0)
    eval_duration = ns_to_seconds(result.get("eval_duration", 0))

    prompt_eval_count = result.get("prompt_eval_count", 0)
    prompt_eval_duration = ns_to_seconds(
        result.get("prompt_eval_duration", 0)
    )

    total_duration = ns_to_seconds(result.get("total_duration", 0))
    load_duration = ns_to_seconds(result.get("load_duration", 0))

    generation_tps = (
        eval_count / eval_duration
        if eval_duration > 0
        else 0
    )

    prompt_tps = (
        prompt_eval_count / prompt_eval_duration
        if prompt_eval_duration > 0
        else 0
    )

    return {
        "total_duration_seconds": total_duration,
        "client_duration_seconds": result["_client_duration_seconds"],
        "load_duration_seconds": load_duration,
        "prompt_tokens": prompt_eval_count,
        "prompt_tokens_per_second": prompt_tps,
        "generated_tokens": eval_count,
        "generation_tokens_per_second": generation_tps,
    }


def percentile(values: list[float], percentile_value: float) -> float:
    values = sorted(values)

    if not values:
        return 0

    index = (len(values) - 1) * percentile_value
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return (
        values[lower] * (1 - weight)
        + values[upper] * weight
    )


def print_run(run_number: int, metrics: dict) -> None:
    print(
        f"Run {run_number:02d} | "
        f"{metrics['generation_tokens_per_second']:.2f} tok/s | "
        f"{metrics['generated_tokens']} tokens | "
        f"{metrics['total_duration_seconds']:.2f}s"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Ollama LLM inference."
    )

    parser.add_argument(
        "--model",
        default="qwen3:8b",
        help="Ollama model to benchmark",
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of benchmark runs",
    )

    parser.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Number of warm-up runs",
    )

    parser.add_argument(
        "--url",
        default=DEFAULT_OLLAMA_URL,
        help="Ollama API URL",
    )

    parser.add_argument(
        "--prompt",
        default="Explain Kubernetes in three sentences.",
        help="Prompt used for the benchmark",
    )

    args = parser.parse_args()

    print()
    print("======================================")
    print(" Ollama LLM Benchmark")
    print("======================================")
    print(f"Model:   {args.model}")
    print(f"Runs:    {args.runs}")
    print(f"Warm-up: {args.warmup}")
    print(f"API:     {args.url}")
    print()

    # Warm-up
    for i in range(args.warmup):
        print(f"Warm-up {i + 1}/{args.warmup}...")
        generate(args.url, args.model, args.prompt)

    print()
    print("Running benchmark...")
    print()

    runs = []

    for i in range(args.runs):
        result = generate(
            args.url,
            args.model,
            args.prompt,
        )

        metrics = calculate_metrics(result)

        runs.append(
            {
                "run": i + 1,
                "metrics": metrics,
            }
        )

        print_run(i + 1, metrics)

    generation_tps = [
        run["metrics"]["generation_tokens_per_second"]
        for run in runs
    ]

    latencies = [
        run["metrics"]["total_duration_seconds"]
        for run in runs
    ]

    summary = {
        "model": args.model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runs": args.runs,
        "warmup_runs": args.warmup,
        "prompt": args.prompt,
        "generation_tokens_per_second": {
            "average": statistics.mean(generation_tps),
            "median": statistics.median(generation_tps),
            "min": min(generation_tps),
            "max": max(generation_tps),
        },
        "latency_seconds": {
            "average": statistics.mean(latencies),
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
            "min": min(latencies),
            "max": max(latencies),
        },
        "results": runs,
    }

    print()
    print("======================================")
    print(" Results")
    print("======================================")

    print(
        f"Average generation: "
        f"{summary['generation_tokens_per_second']['average']:.2f} tok/s"
    )

    print(
        f"Median generation:  "
        f"{summary['generation_tokens_per_second']['median']:.2f} tok/s"
    )

    print(
        f"Average latency:     "
        f"{summary['latency_seconds']['average']:.2f}s"
    )

    print(
        f"P50 latency:         "
        f"{summary['latency_seconds']['p50']:.2f}s"
    )

    print(
        f"P95 latency:         "
        f"{summary['latency_seconds']['p95']:.2f}s"
    )

    # Save result
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_model_name = args.model.replace(":", "-").replace("/", "-")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    output_file = (
        output_dir
        / f"{safe_model_name}-{timestamp}.json"
    )

    with output_file.open("w") as file:
        json.dump(summary, file, indent=2)

    print()
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()

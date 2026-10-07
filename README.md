# AI GPU Lab

A self-hosted GPU infrastructure lab for experimenting with local AI
workloads, LLM inference, benchmarking, speech processing,
observability, and containerized GPU applications.

The goal of this project is to explore how production-oriented AI
workloads can be deployed and operated on dedicated GPU infrastructure
while keeping the environment reproducible and observable.

## Overview

This lab runs on a dedicated Linux server equipped with an NVIDIA GPU.

AI workloads are containerized with Docker and access the GPU through
the NVIDIA Container Toolkit.

The project currently focuses on local LLM inference using Ollama, with
plans to expand into alternative inference engines, speech-to-text,
text-to-speech, monitoring, and Kubernetes integration.

``` text
                    ┌─────────────────────┐
                    │    Applications     │
                    │  Kubernetes / APIs  │
                    └──────────┬──────────┘
                               │
                          HTTP / gRPC
                               │
                               ▼
                    ┌─────────────────────┐
                    │    AI GPU Server    │
                    │                     │
                    │  Docker             │
                    │  NVIDIA Runtime     │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
           LLM              Speech-to-Text      TTS
         Ollama                Whisper          Voice
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                       NVIDIA GPU / CUDA
```

## Hardware

Current GPU server:

-   NVIDIA GeForce RTX 5070 Ti
-   16 GB VRAM
-   NVIDIA Driver 595
-   CUDA 13.x compatible driver
-   Ubuntu Server

## Tech Stack

-   Ubuntu Server
-   Docker
-   Docker Compose
-   NVIDIA Container Toolkit
-   Ollama
-   Python
-   NVIDIA CUDA

Planned:

-   vLLM
-   Speech-to-Text
-   Text-to-Speech
-   Prometheus
-   Grafana
-   Kubernetes integration

## Repository Structure

``` text
ai-gpu-lab/
├── docker/
│   ├── ollama/
│   │   ├── docker-compose.yml
│   │   └── README.md
│   ├── vllm/
│   ├── whisper/
│   └── tts/
├── benchmarks/
│   ├── llm/
│   │   ├── benchmark.py
│   │   └── results/
│   ├── stt/
│   └── tts/
├── scripts/
│   ├── gpu-info.sh
│   ├── gpu-test.sh
│   └── health-check.sh
├── monitoring/
│   ├── prometheus/
│   └── grafana/
├── docs/
│   ├── architecture.md
│   ├── gpu-setup.md
│   └── benchmarks.md
├── examples/
│   ├── python-client/
│   └── node-client/
└── README.md
```

## Running Ollama

Ollama runs as a container with direct access to the NVIDIA GPU.

Start the service:

``` bash
cd docker/ollama
docker compose up -d
```

Check its status:

``` bash
docker compose ps
```

Verify GPU access from inside the container:

``` bash
docker exec ollama nvidia-smi
```

The Ollama API is exposed on:

``` text
http://localhost:11434
```

Check the available models:

``` bash
curl http://localhost:11434/api/tags
```

## Running a Model

Pull a model:

``` bash
docker exec -it ollama ollama pull qwen3:8b
```

Run it interactively:

``` bash
docker exec -it ollama ollama run qwen3:8b
```

Or use the HTTP API:

``` bash
curl http://localhost:11434/api/generate \
  -d '{
    "model": "qwen3:8b",
    "prompt": "Explain Kubernetes in three sentences.",
    "stream": false
  }'
```

## Benchmarking

The repository includes a simple benchmark tool for measuring local LLM
inference performance.

Run:

``` bash
cd benchmarks/llm
python3 benchmark.py
```

The benchmark performs a warm-up followed by multiple inference runs and
calculates metrics such as:

-   Generation throughput (tokens/sec)
-   Average latency
-   P50 latency
-   P95 latency
-   Prompt processing throughput
-   Generated token count

Results are stored as JSON files under:

``` text
benchmarks/llm/results/
```

### Initial Result

First test using Qwen3 8B:

  Hardware / Model                Value
  ------------------------------- ----------------------------
  GPU                             NVIDIA GeForce RTX 5070 Ti
  VRAM                            16 GB
  Model                           Qwen3 8B
  Inference Engine                Ollama
  Initial generation throughput   \~141 tokens/sec

> This is an initial single-run result. Reproducible multi-run
> benchmarks will be added as the project evolves.

## GPU Validation

GPU access can be validated independently of the AI workloads:

``` bash
docker run --rm --gpus all ubuntu nvidia-smi
```

This verifies the complete container GPU path:

``` text
Docker
   │
   ▼
NVIDIA Container Toolkit
   │
   ▼
NVIDIA Driver
   │
   ▼
RTX 5070 Ti
```

## Goals

This project is intended to explore more than simply running local
models.

The main areas of experimentation include:

-   Self-hosted LLM inference
-   GPU containerization
-   Model performance benchmarking
-   GPU utilization and VRAM monitoring
-   LLM serving through HTTP APIs
-   Concurrent inference workloads
-   Speech-to-text pipelines
-   Text-to-speech pipelines
-   AI workload observability
-   Kubernetes integration
-   Local-first AI architectures
-   Cloud API fallback strategies

## Roadmap

-   [x] Configure NVIDIA GPU drivers
-   [x] Configure Docker GPU access
-   [x] Install NVIDIA Container Toolkit
-   [x] Deploy Ollama with Docker Compose
-   [x] Run first local LLM
-   [x] Create initial LLM benchmark
-   [ ] Benchmark multiple LLMs
-   [ ] Collect GPU utilization during benchmarks
-   [ ] Collect VRAM and power consumption metrics
-   [ ] Deploy vLLM
-   [ ] Compare Ollama vs vLLM
-   [ ] Deploy speech-to-text models
-   [ ] Deploy text-to-speech models
-   [ ] Add Prometheus metrics
-   [ ] Build Grafana dashboards
-   [ ] Integrate with Kubernetes workloads
-   [ ] Implement local inference + cloud fallback
-   [ ] Load test concurrent inference requests

## Why This Project?

Running an AI model locally is relatively simple.

Operating AI workloads as infrastructure introduces different
challenges:

-   GPU resource management
-   Container runtime integration
-   Model lifecycle management
-   Performance measurement
-   Observability
-   Concurrent workloads
-   API availability
-   Infrastructure reproducibility
-   Cost optimization

This repository documents my experiments around those problems while
building a practical self-hosted AI platform.

## License

This project is intended for experimentation and learning.

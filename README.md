# AI GPU Lab

Self-hosted GPU infrastructure lab for experimenting with local AI inference, benchmarking, speech processing, and containerized GPU workloads.

The goal is to build a local AI platform that can serve applications and Kubernetes workloads while exploring performance, observability, and hybrid local/cloud inference.

## Architecture

```text
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

- NVIDIA GeForce RTX 5070 Ti — 16 GB VRAM
- Ubuntu Server
- NVIDIA Driver + CUDA support

## Stack

- Docker / Docker Compose
- NVIDIA Container Toolkit
- Ollama
- Python

## LLM Benchmarks

Benchmarks running locally on an **NVIDIA GeForce RTX 5070 Ti (16 GB)**.

| Model | Engine | Avg. Tokens/s | Avg. Latency |
| --- | --- | ---: | ---: |
| Qwen3 8B | Ollama | 142.47 | 1.91s |

Detailed benchmark results are available in [`benchmarks/results/`](benchmarks/results/).

Run the benchmark:

```bash
python3 benchmarks/benchmark.py
```

## Running Ollama

Start the Ollama service:

```bash
cd docker/ollama
docker compose up -d
```

Pull and run a model:

```bash
docker exec -it ollama ollama pull qwen3:8b
docker exec -it ollama ollama run qwen3:8b
```

## Roadmap

- [x] NVIDIA GPU container runtime
- [x] Ollama GPU inference
- [x] LLM benchmarking
- [ ] Benchmark multiple LLMs
- [ ] GPU / VRAM monitoring
- [ ] vLLM inference server
- [ ] Speech-to-Text
- [ ] Text-to-Speech
- [ ] Prometheus + Grafana
- [ ] Kubernetes integration
- [ ] Local inference + cloud fallback

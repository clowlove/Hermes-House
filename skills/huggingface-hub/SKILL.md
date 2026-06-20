---
name: huggingface-hub
description: "HuggingFace hf CLI: search/download/upload models, datasets."
version: 1.0.0
author: Hugging Face
license: MIT
tags: [huggingface, hf, models, datasets, hub, mlops]
---

# Hugging Face CLI (`hf`) Reference Guide

The `hf` command is the modern command-line interface for interacting with the Hugging Face Hub, providing tools to manage repositories, models, datasets, and Spaces.

> **IMPORTANT:** The `hf` command replaces the now deprecated `huggingface-cli` command.

## Quick Start
*   **Installation:** `curl -LsSf https://hf.co/cli/install.sh | bash -s`
*   **Help:** Use `hf --help` to view all available functions and real-world examples.
*   **Authentication:** Recommended via `HF_TOKEN` environment variable or the `--token` flag.

---

## Core Commands

### General Operations
*   `hf download REPO_ID`: Download files from the Hub.
*   `hf upload REPO_ID`: Upload files/folders (recommended for single-commit).
*   `hf upload-large-folder REPO_ID LOCAL_PATH`: Recommended for resumable uploads of large directories.
*   `hf sync`: Sync files between a local directory and a bucket.
*   `hf env` / `hf version`: View environment and version details.

### Authentication (`hf auth`)
*   `login` / `logout`: Manage sessions using tokens from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
*   `list` / `switch`: Manage and toggle between multiple stored access tokens.
*   `whoami`: Identify the currently logged-in account.

### Repository Management (`hf repos`)
*   `create` / `delete`: Create or permanently remove repositories.
*   `duplicate`: Clone a model, dataset, or Space to a new ID.
*   `move`: Transfer a repository between namespaces.
*   `branch` / `tag`: Manage Git-like references.
*   `delete-files`: Remove specific files using patterns.

---

## Specialized Hub Interactions

### Datasets & Models
*   **Datasets:** `hf datasets list`, `info`, and `parquet` (list parquet URLs).
*   **SQL Queries:** `hf datasets sql SQL` — Execute raw SQL via DuckDB against dataset parquet URLs.
*   **Models:** `hf models list` and `info`.
*   **Papers:** `hf papers list` — View daily papers.

### Discussions & Pull Requests (`hf discussions`)
*   Manage the lifecycle of Hub contributions: `list`, `create`, `info`, `comment`, `close`, `reopen`, and `rename`.
*   `diff`: View changes in a PR.
*   `merge`: Finalize pull requests.

### Infrastructure & Compute
*   **Endpoints:** Deploy and manage Inference Endpoints (`deploy`, `pause`, `resume`, `scale-to-zero`, `catalog`).
*   **Jobs:** Run compute tasks on HF infrastructure. Includes `hf jobs uv` for running Python scripts with inline dependencies and `stats` for resource monitoring.
*   **Spaces:** Manage interactive apps. Includes `dev-mode` and `hot-reload` for Python files without full restarts.

### Storage & Automation
*   **Buckets:** Full S3-like bucket management (`create`, `cp`, `mv`, `rm`, `sync`).
*   **Cache:** Manage local storage with `list`, `prune` (remove detached revisions), and `verify` (checksum checks).
*   **Webhooks:** Automate workflows by managing Hub webhooks (`create`, `watch`, `enable`/`disable`).
*   **Collections:** Organize Hub items into collections (`add-item`, `update`, `list`).

---

## Advanced Usage & Tips

### Global Flags
*   `--format json`: Produces machine-readable output for automation.
*   `-q` / `--quiet`: Limits output to IDs only.

### Extensions & Skills
## Hermes Agent HF Resources (cntalk)

| Resource | Type | URL |
|----------|------|-----|
| hello-hermes | Space | hf.co/spaces/cntalk/hello-hermes |
| hermes-toolkit | Space | hf.co/spaces/cntalk/hermes-toolkit |
| hermes-examples | Dataset | hf.co/datasets/cntalk/hermes-examples |
| agent-prompts | Dataset | hf.co/datasets/cntalk/agent-prompts |
| hermes-skills | Dataset | hf.co/datasets/cntalk/hermes-skills |
| hermes-integration | Dataset | hf.co/datasets/cntalk/hermes-integration |

Collection: [hermes-agent-resources](https://huggingface.co/collections/cntalk/hermes-agent-resources-69f9c5b62fb70b0bbb6ae0b1)

### Sync Script
```bash
python ~/.hermes/scripts/hf_sync.py  # Sync Hermes resources to HF
```

## Free Inference API Models

- text-generation: meta-llama/Llama-3.2-1B-Instruct, mistralai/Mistral-7B-Instruct-v0.2
- summarization: facebook/bart-large-cnn
- translation: Helsinki-NLP/opus-mt-zh-en
- sentiment-analysis: distilbert-base-uncased-finetuned-sst-2-english
- question-answering: deepset/roberta-base-squad2
- image-classification: google/vit-base-patch16-224

### Inference API Example (Python)
```python
from huggingface_hub import InferenceClient

client = InferenceClient(model="meta-llama/Llama-3.2-1B-Instruct", token="hf_xxx")
result = client.text_generation(prompt="Hello, how are you?", max_new_tokens=100, temperature=0.7)
```

## Tips

- Free accounts can create public models/datasets/Spaces
- Space CPU Basic is free; T4 GPU is billed per hour
- Inference API has rate limits (when model not specified)
- Ensure `.gitattributes` is set correctly before upload (LFS if needed)
- Extensions: extend CLI via `hf extensions install REPO_ID`
- Skills: manage AI assistant skills with `hf skills add`

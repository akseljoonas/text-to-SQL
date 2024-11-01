# Text-to-SQL with Stable Code 3B

This project explores using Stable Code 3B, a Small Language Model (SLM), for converting natural language questions into SQL queries. It evaluates full fine-tuning and parameter-efficient fine-tuning (LoRA) methods on the BIRD Benchmark dataset.

## Project Structure
- **data/**: Processed and raw datasets for training and evaluation (generated from BIRD Benchmark).
  - `generations/`: Model-generated outputs.
  - `processed/`: JSON files for training, mini-dev, and dev sets (including database schemas).
  - `raw/`: Original JSON files for BIRD benchmark data (training and dev sets).

- **databases/**: SQLite databases (training and dev sets) required for evaluation and schema generation.  
  **Note**: This directory is not included in the repository. Please download the databases from the [BIRD Benchmark Dataset webpage](https://bird-bench.github.io).

- **notebooks/**: Jupyter notebooks for running full parameter fine-tuning and LoRA fine-tuning.

- **src/**: Core project scripts.
  - `execution_evaluation.py`: Code for evaluating model-generated SQL queries on execution accuracy.
  - `schema_linking.py`: Handles database schema generation for the training and inference prompts.
  - `utils/`: Helper scripts for database conversion, execution, and schema linking.

## Requirements
Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```
## Contributions
Aksel Joonas Reedi, Mika Ernesto Umana Lemus, Mihkel Mariusz Jezierski
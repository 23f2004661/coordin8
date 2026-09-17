"""CLI script to run retrieval and generation evaluations."""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evals.runner import EvalRunner


def main():
    print("Running Coordin8 Evaluation Benchmarks...")
    runner = EvalRunner()
    results = runner.run_retrieval_benchmark()
    print("Benchmark completed:", results)


if __name__ == "__main__":
    main()

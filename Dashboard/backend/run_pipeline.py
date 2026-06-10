"""Temporary script to run the ETL pipeline."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.etl.pipeline import ETLPipeline

pipeline = ETLPipeline()
metrics = pipeline.run(reset=True)
print(f"\nFinal metrics: {metrics}")

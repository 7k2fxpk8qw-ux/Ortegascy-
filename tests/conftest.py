import sys
import os

# Ensure the repository root is on the Python path so tests can import
# the project modules (ton_client, ethena_ton, main).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

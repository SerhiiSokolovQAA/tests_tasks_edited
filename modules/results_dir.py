import os

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)
dump_path = os.path.join(RESULTS_DIR, "db_dump.json")

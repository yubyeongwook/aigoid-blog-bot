# -*- coding: utf-8 -*-
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

try:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

from main_afternoon import evaluate_morning_picks
picks = evaluate_morning_picks()
print("Evaluated Picks Result:")
print(json.dumps(picks, ensure_ascii=False, indent=2))

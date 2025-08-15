# api/index.py
"""
Vercel entrypoint for a FastAPI app.

It tries to import a top-level `app = FastAPI()` from one of:
- main.py                  (repo root)   -> from main import app
- app/main.py              (package)     -> from app.main import app
- src/main.py              (src layout)  -> from src.main import app

If none match, it raises a clear ImportError.
"""

from pathlib import Path
import sys

# Add repo root to import path so "from main import app" works
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Try common locations in order
_last_err = None
for target in (
    ("main", "app"),        # from main import app
    ("app.main", "app"),    # from app.main import app
    ("src.main", "app"),    # from src.main import app
):
    module_name, attr = target
    try:
        mod = __import__(module_name, fromlist=[attr])
        app = getattr(mod, attr)  # FastAPI instance
        break
    except Exception as e:  # keep trying others
        _last_err = e
else:
    raise ImportError(
        "Could not import FastAPI `app`.\n"
        "Tried: `from main import app`, `from app.main import app`, `from src.main import app`.\n"
        f"Last error: {_last_err}"
    )

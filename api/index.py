import os
import sys
from pathlib import Path

# Set up paths so that 'app' can be imported whether running from root or backend
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"

if backend_dir.is_dir() and str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
elif str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Ensure VERCEL environment flag is explicitly recognized
os.environ.setdefault("VERCEL", "1")

from app.main import app

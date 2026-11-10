"""Run TACS read-only tools with: PYTHONPATH=python python -m tacs."""
from .core import _main

if __name__ == "__main__":
    raise SystemExit(_main())

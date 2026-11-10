"""Pantheon: read-only structural analysis for explicitly approved Python files."""
from .engine import AnalysisError, analyze_approved_files, generate_pantheon_modules
__all__ = ["AnalysisError", "analyze_approved_files", "generate_pantheon_modules"]

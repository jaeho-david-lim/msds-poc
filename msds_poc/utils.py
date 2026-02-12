"""Utility functions for MSDS PoC."""

import json
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def save_result(output_path: Path, data: Dict[str, Any]) -> None:
    """Save result to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

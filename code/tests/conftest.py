import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["PRC_OFFLINE"] = "1"


@pytest.fixture()
def demo(tmp_path, monkeypatch):
    """A fresh seeded database. The real placement.db is never touched."""
    monkeypatch.setenv("PRC_DB", str(tmp_path / "test.db"))
    monkeypatch.setenv("PRC_PROMPT_LOG", str(tmp_path / "prompts.jsonl"))
    from app import datasets

    datasets.setup()
    return tmp_path

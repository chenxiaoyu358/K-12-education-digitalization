"""Load keyword dictionaries from data files."""

from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "keyword_dicts"


def load_keywords(filename: str) -> list[str]:
    """Load keywords from a text file (one keyword per line)."""
    filepath = _DATA_DIR / filename
    if not filepath.exists():
        return []
    keywords = []
    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            keywords.append(line)
    return keywords


def load_all_keyword_dicts() -> dict[str, list[str]]:
    """Load all ICT category keyword dictionaries.

    Order matters: categories are checked in insertion order.
    training_consulting and ops_maintenance sit before smart_campus so
    specific service terms fire before the broad 信息化 catch-all.
    """
    return {
        "network_infra": load_keywords("network_infra.txt"),
        "computer_terminal": load_keywords("computer_terminal.txt"),
        "multimedia_display": load_keywords("multimedia_display.txt"),
        "digital_lab": load_keywords("digital_lab.txt"),
        "maker_stem": load_keywords("maker_stem.txt"),
        "teaching_system": load_keywords("teaching_system.txt"),
        "training_consulting": load_keywords("training_consulting.txt"),
        "ops_maintenance": load_keywords("ops_maintenance.txt"),
        "smart_campus": load_keywords("smart_campus.txt"),
        "campus_environment": load_keywords("campus_environment.txt"),
        "digital_resources": load_keywords("digital_resources.txt"),
    }

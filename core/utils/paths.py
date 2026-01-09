from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
MEMORY_DIR = DATA_DIR / "memory"
PROCESSED_DIR = DATA_DIR / "processed"

REGISTRY_DB_PATH = DATA_DIR / "memory" / "registry.sqlite3"


def ensure_data_dirs() -> None:
    for p in (UPLOADS_DIR, VECTORSTORE_DIR, MEMORY_DIR, PROCESSED_DIR):
        p.mkdir(parents=True, exist_ok=True)

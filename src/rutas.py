"""
Rutas del proyecto. Uso en notebooks:

    import sys; sys.path.append("..")
    from src.rutas import BRONZE
    df = pd.read_parquet(BRONZE / "iar_agencias.parquet")
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BRONZE = DATA / "bronze"
SILVER = DATA / "silver"
GOLD = DATA / "gold"
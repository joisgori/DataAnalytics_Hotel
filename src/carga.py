# src/carga.py
import pandas as pd
from src.rutas import BRONZE

def cargar_bronze():
    """Devuelve un dict {nombre: DataFrame} con todos los parquet de bronze."""
    return {
        p.stem.removeprefix("iar_"): pd.read_parquet(p)
        for p in sorted(BRONZE.glob("*.parquet"))
    }
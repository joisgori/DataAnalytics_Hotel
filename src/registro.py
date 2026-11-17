"""Registro persistente de la auditoría: incidencias y supuestos en reports/*.csv.

Cada notebook registra lo que encuentra y el registro sobrevive entre notebooks y sesiones.
Registrar dos veces el mismo id sobrescribe la entrada anterior, así que puedes
volver a ejecutar un notebook entero sin duplicar nada.
"""
import pandas as pd

from src.rutas import ROOT

REPORTS = ROOT / "reports"


def _guardar(nombre, fila):
    REPORTS.mkdir(exist_ok=True)
    ruta = REPORTS / f"{nombre}.csv"
    actual = pd.read_csv(ruta, dtype=str) if ruta.exists() else pd.DataFrame(columns=list(fila))
    actual = actual[actual["id"] != fila["id"]]
    nuevo = pd.concat([actual, pd.DataFrame([fila]).astype(str)], ignore_index=True)
    nuevo = nuevo.sort_values("id", key=lambda s: s.str.extract(r"(\d+)", expand=False).astype(float))
    nuevo.to_csv(ruta, index=False)
    return nuevo


def incidencia(id, tabla, hallazgo, impacto, decision, pregunta=""):
    """Algo que está mal o es anómalo en los datos, con su impacto y la decisión para silver."""
    return _guardar("incidencias", {
        "id": id, "tabla": tabla, "hallazgo": hallazgo,
        "impacto": impacto, "decision": decision, "pregunta_negocio": pregunta,
    })


def supuesto(id, enunciado, nivel, evidencia, impacto_si_falso, pregunta=""):
    """Algo que se da por cierto sin confirmación total. nivel: verde, amarillo o rojo."""
    assert nivel in {"verde", "amarillo", "rojo"}, "nivel debe ser verde, amarillo o rojo"
    return _guardar("supuestos", {
        "id": id, "supuesto": enunciado, "nivel": nivel, "evidencia": evidencia,
        "impacto_si_falso": impacto_si_falso, "pregunta_negocio": pregunta,
    })


def leer(nombre):
    """nombre: 'incidencias' o 'supuestos'."""
    ruta = REPORTS / f"{nombre}.csv"
    return pd.read_csv(ruta, dtype=str).fillna("") if ruta.exists() else pd.DataFrame()
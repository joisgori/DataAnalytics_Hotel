"""Funciones de auditoría para la capa bronze."""
from itertools import permutations

import pandas as pd

TEXTOS_NULOS = {"", "null", "none", "nan", "n/a", "na", "-", "?", "sin dato", "desconocido"}


def perfil(df):
    """Tipo, % de nulos, valores únicos y un ejemplo por columna."""
    return pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos_%": (df.isna().mean() * 100).round(2),
        "unicos": df.nunique(),
        "ejemplo": df.iloc[0] if len(df) else None,
    })


def nulos_disfrazados(df, textos=TEXTOS_NULOS):
    """Por columna de texto, cuántos valores significan 'sin dato' aunque no sean nulos."""
    out = {}
    for col in df.select_dtypes(include=["object", "string"]).columns:
        s = df[col].dropna().astype(str).str.strip().str.lower()
        n = int(s.isin(textos).sum())
        if n:
            out[col] = n
    return pd.Series(out, dtype="int64", name="nulos_disfrazados").sort_values(ascending=False)


def claves_candidatas(df):
    """Columnas únicas y sin nulos: candidatas a clave primaria."""
    return [c for c in df.columns if df[c].is_unique and df[c].notna().all()]


def revisar_claves(dfs, claves):
    """claves = {tabla: columna o [columnas]}. Comprueba que cada clave sea única y sin nulos."""
    filas = []
    for tabla, cols in claves.items():
        cols = [cols] if isinstance(cols, str) else list(cols)
        df = dfs[tabla]
        duplicados = int(df.duplicated(subset=cols).sum())
        nulos = int(df[cols].isna().any(axis=1).sum())
        filas.append({
            "tabla": tabla,
            "clave": ", ".join(cols),
            "filas": len(df),
            "duplicados": duplicados,
            "filas_con_nulos": nulos,
            "clave_valida": duplicados == 0 and nulos == 0,
        })
    return pd.DataFrame(filas)


def revisar_integridad(dfs, relaciones, medidas=None):
    """relaciones = [(tabla_hechos, fk, tabla_catalogo, pk), ...]
    medidas = {tabla_hechos: columna} para medir el impacto de las huérfanas en negocio."""
    medidas = medidas or {}
    filas = []
    for hechos, fk, dim, pk in relaciones:
        df = dfs[hechos]
        valores = df[fk]
        huerfana = valores.notna() & ~valores.isin(dfs[dim][pk])
        fila = {
            "relacion": f"{hechos}.{fk} → {dim}.{pk}",
            "filas": len(df),
            "nulos": int(valores.isna().sum()),
            "huerfanas_filas_%": round(huerfana.mean() * 100, 2),
            "ids_huerfanos": int(valores[huerfana].nunique()),
            "ejemplos": valores[huerfana].unique()[:5].tolist(),
        }
        medida = medidas.get(hechos)
        if medida:
            total = df[medida].sum()
            fila[f"huerfanas_{medida}_%"] = round(df.loc[huerfana, medida].sum() / total * 100, 2) if total else None
        filas.append(fila)
    return pd.DataFrame(filas)


def descubrir_relaciones(dfs, umbral=0.95):
    """Prueba todos los pares de columnas entre tablas: ¿los valores de A están en B, y B es única?
    Devuelve candidatas a FK → PK. Espera falsos positivos: descártalos con criterio."""
    unicas = {t: [c for c in df.columns if df[c].is_unique] for t, df in dfs.items()}
    cache = {}

    def valores(t, c):
        if (t, c) not in cache:
            cache[(t, c)] = set(dfs[t][c].dropna().unique())
        return cache[(t, c)]

    candidatas = []
    for (t1, d1), (t2, d2) in permutations(dfs.items(), 2):
        for c1 in d1.columns:
            for c2 in unicas[t2]:
                if d1[c1].dtype.kind != d2[c2].dtype.kind:
                    continue
                v1 = valores(t1, c1)
                if not v1:
                    continue
                cobertura = len(v1 & valores(t2, c2)) / len(v1)
                if cobertura >= umbral:
                    candidatas.append((t1, c1, t2, c2, round(cobertura, 3)))
    return pd.DataFrame(candidatas, columns=["tabla_hijo", "columna", "tabla_padre", "columna_padre", "cobertura"])


def prueba_formula(calculado, guardado, tolerancia=0.01):
    """¿Cuánto cuadra una columna guardada con su fórmula? Resume también lo que no cuadra."""
    dif = (calculado - guardado).dropna()
    no_cuadra = dif.abs() >= tolerancia
    return {
        "filas_comparables": len(dif),
        "cuadra_%": round(float((~no_cuadra).mean()) * 100, 2),
        "diferencias_que_no_cuadran": dif[no_cuadra].describe(),
    }


def a_fecha(s, formato="%Y%m%d", patron=r"\d{8}"):
    """Convierte texto a fecha con formato explícito; lo que no encaja queda como NaT.
    El patrón evita que '2019081' se lea como 1 de agosto: %d acepta un solo dígito."""
    texto = s.astype("string").str.strip()
    return pd.to_datetime(texto.where(texto.str.fullmatch(patron)), format=formato, errors="coerce")


def desfase_dias(fecha_a, fecha_b, top=10):
    """Distribución del desfase en días entre dos fechas."""
    return (fecha_a - fecha_b).dt.days.value_counts().head(top)


def expandir_noches(df, llegada="llegada", salida="salida"):
    """Una fila por noche de estancia, de la llegada a la víspera de la salida."""
    v = df.dropna(subset=[llegada, salida])
    v = v[v[salida] > v[llegada]].copy()
    v["noche"] = [pd.date_range(l, s - pd.Timedelta(days=1)) for l, s in zip(v[llegada], v[salida])]
    v = v.explode("noche")
    v["noche"] = pd.to_datetime(v["noche"])
    return v
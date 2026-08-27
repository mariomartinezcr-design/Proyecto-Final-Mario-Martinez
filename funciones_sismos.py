import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Busca una columna en el DataFrame aunque el nombre tenga pequeñas diferencias
# Ejemplos: "Magnitud", "magnitud", "magnitude", "mag"
def normalizar_nombre_columna(columna):
    texto = str(columna).strip().lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = re.sub(r"[^a-z0-9]+", "", texto)
    return texto


def obtener_columna(df: pd.DataFrame, nombres: list[str]) -> str:
    columnas = {normalizar_nombre_columna(col): col for col in df.columns}

    for nombre in nombres:
        clave = normalizar_nombre_columna(nombre)
        if clave in columnas:
            return columnas[clave]

    alternativas = ", ".join(nombres)
    raise KeyError(f"No se encontro ninguna de estas columnas: {alternativas}")


# Devuelve un reporte del ultimo sismo sentido del año

def resumen_anual(df: pd.DataFrame) -> str:
    magnitud_col = obtener_columna(df, ["magnitud", "magnitude", "mag"])
    profundidad_col = obtener_columna(df, ["profundidad", "depth", "profundidadkm", "profundidad_km"])
    fecha_col = obtener_columna(df, ["fecha", "fecha_hora", "date", "datetime", "hora", "fechayhora"])
    localizacion_col = obtener_columna(df, ["localizacion", "ubicacion", "lugar", "region", "zona", "localidad", "provincia"])

    total = len(df)
    magnitudes = pd.to_numeric(df[magnitud_col], errors="coerce")
    profundidades = pd.to_numeric(df[profundidad_col], errors="coerce")
    fechas = pd.to_datetime(df[fecha_col], errors="coerce")

    indice_fecha_max = fechas.idxmax()
    magnitud_ultimo = magnitudes.loc[indice_fecha_max]
    profundidad_ultimo = profundidades.loc[indice_fecha_max]
    localizacion_ultima = df.loc[indice_fecha_max, localizacion_col]

    return (
        f"Este es el sismo numero {total} del ano.\n"
        f"- Magnitud: {magnitud_ultimo}\n"
        f"- Profundidad: {profundidad_ultimo}\n"
        f"- Localizacion: {localizacion_ultima}\n"
    )


# Compara cada valor con la media de magnitud y profundidad
# Muestra cuántos registros están por encima o por debajo de la media

def comparar_con_media(df: pd.DataFrame) -> str:
    magnitud_col = obtener_columna(df, ["magnitud", "magnitude", "mag"])
    profundidad_col = obtener_columna(df, ["profundidad", "depth", "profundidadkm", "profundidad_km"])
    fecha_col = obtener_columna(df, ["fecha", "fecha_hora", "date", "datetime", "hora", "fechayhora"])

    magnitudes = pd.to_numeric(df[magnitud_col], errors="coerce")
    profundidades = pd.to_numeric(df[profundidad_col], errors="coerce")
    fechas = pd.to_datetime(df[fecha_col], errors="coerce")
    indice_fecha_max = fechas.idxmax()

    media_magnitud = magnitudes.mean()
    media_profundidad = profundidades.mean()

    por_encima_magnitud = (magnitudes > media_magnitud).sum()
    por_debajo_magnitud = (magnitudes < media_magnitud).sum()
    por_encima_profundidad = (profundidades > media_profundidad).sum()
    por_debajo_profundidad = (profundidades < media_profundidad).sum()

    return (
        "\nComparativa anual del sismo sentido:\n"
        f"- Magnitud de sismo sentido: {magnitudes.loc[indice_fecha_max]}\n"
        f"- Profundidad de sismo sentido: {profundidades.loc[indice_fecha_max]}\n"
        f"- Media de magnitud: {media_magnitud:.2f}\n"
        f"- Sismos por encima de la media: {por_encima_magnitud}\n"
        f"- Sismos por debajo de la media: {por_debajo_magnitud}\n"
        f"- Media de profundidad: {media_profundidad:.2f}\n"
        f"- Sismos por encima de la media de profundidad: {por_encima_profundidad}\n"
        f"- Sismos por debajo de la media de profundidad: {por_debajo_profundidad}\n"
    )


# Elimina las primeras 5 palabras de cada ubicacion y cuenta repeticiones
# Esto permite detectar zonas repetidas aunque la descripcion sea muy larga

def localizaciones_repetidas(df: pd.DataFrame, top_n: int = 5) -> str:
    localizacion_col = obtener_columna(df, ["localizacion", "ubicacion", "lugar", "region", "zona", "localidad", "provincia"])

    series = df[localizacion_col].fillna("").astype(str)
    ubicaciones = series.apply(lambda texto: " ".join(texto.split()[5:]) if len(texto.split()) > 5 else texto)
    conteo = ubicaciones.value_counts().head(top_n)

    if conteo.empty:
        return "\nNo se encontraron ubicaciones repetidas.\n"

    lineas = [
        "\nUbicaciones repetidas (ignorando las primeras 5 palabras):",
        f"- Total de ubicaciones distintas: {ubicaciones.nunique()}",
    ]
    for ubicacion, cantidad in conteo.items():
        lineas.append(f"- '{ubicacion}': {cantidad} veces")

    return "\n".join(lineas) + "\n"


# Muestra graficos con matplotlib para visualizar tendencia del conjunto de datos

def mostrar_graficos(df: pd.DataFrame) -> None:
    magnitud_col = obtener_columna(df, ["magnitud", "magnitude", "mag"])
    profundidad_col = obtener_columna(df, ["profundidad", "depth", "profundidadkm", "profundidad_km"])
    fecha_col = obtener_columna(df, ["fecha", "fecha_hora", "date", "datetime", "hora", "fechayhora"])
    localizacion_col = obtener_columna(df, ["localizacion", "ubicacion", "lugar", "region", "zona", "localidad", "provincia"])

    eje_x = pd.to_datetime(df[fecha_col], errors="coerce")

    # Grafico 1: magnitud por fecha
    plt.figure(figsize=(10, 4))
    plt.plot(eje_x, pd.to_numeric(df[magnitud_col], errors="coerce"), marker="o")
    plt.title("Magnitud por fecha")
    plt.xlabel("Fecha")
    plt.ylabel("Magnitud")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    plt.close()

    # Grafico 2: profundidad por fecha
    plt.figure(figsize=(10, 4))
    plt.plot(df[fecha_col], df[profundidad_col], marker="o", color="tab:orange")
    plt.title("Profundidad por fecha")
    plt.xlabel("Fecha")
    plt.ylabel("Profundidad")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    plt.close()

    # Grafico 3: histograma de magnitudes
    plt.figure(figsize=(8, 5))
    plt.hist(df[magnitud_col], bins=10, color="tab:green", edgecolor="black")
    plt.title("Histograma de magnitudes")
    plt.xlabel("Magnitud")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.show()
    plt.close()

    # Grafico 4: ubicaciones repetidas
    serie = df[localizacion_col].fillna("").astype(str)
    ubicaciones = serie.apply(lambda texto: " ".join(texto.split()[5:]) if len(texto.split()) > 5 else texto)
    conteo = ubicaciones.value_counts().head(10)

    if not conteo.empty:
        plt.figure(figsize=(10, 5))
        conteo.plot(kind="bar", color="tab:purple")
        plt.title("Ubicaciones repetidas")
        plt.xlabel("Ubicacion")
        plt.ylabel("Cantidad")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
        plt.close()

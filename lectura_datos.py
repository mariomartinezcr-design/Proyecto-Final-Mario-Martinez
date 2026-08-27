from datetime import date
from io import StringIO
from pathlib import Path
import re
import sys

import pandas as pd
import requests

# URL del servicio web que devuelve los sismos por año
URL = "https://www.ovsicori.una.ac.cr/sistemas/ssentido/SismosAnual.php"

# Año mínimo soportado por la aplicación
ANIO_MIN = 2009


def normalizar_nombre_columna(columna):
    # Normaliza nombres de columnas para trabajar con CSV reales y con variaciones de escritura
    texto = str(columna).strip().lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = re.sub(r"[^a-z0-9]+", "", texto)
    return texto


def descargar_sismos(anio: int) -> Path:
    # Realiza la petición HTTP y descarga la tabla del año indicado
    respuesta = requests.post(URL, data={"anno": anio}, timeout=30)
    respuesta.raise_for_status()

    # Lee todas las tablas HTML y busca la que corresponde a los sismos
    tablas = pd.read_html(StringIO(respuesta.text))
    tabla = next((tabla for tabla in tablas if len(tabla.columns) == 9), None)

    if tabla is None:
        raise RuntimeError("No se encontro la tabla de sismos en la respuesta del sitio.")

    # Guarda el resultado en un CSV con el nombre del año
    archivo = Path(f"sismicidad_{anio}.csv")
    tabla.to_csv(archivo, index=False, encoding="utf-8-sig")
    return archivo


def cargar_datos(ruta_csv: str | Path) -> pd.DataFrame:
    # Lee el archivo CSV y devuelve un DataFrame listo para análisis
    df = pd.read_csv(ruta_csv, encoding="utf-8-sig", header=None)

    # El sitio incluye una fila repetida antes de la cabecera real del CSV
    # Por eso se busca la fila que contiene las columnas reales del conjunto de datos
    fila_cabecera = None
    for indice, fila in df.iterrows():
        valores = [str(valor).strip() for valor in fila.tolist() if pd.notna(valor)]
        valores_norm = [normalizar_nombre_columna(valor) for valor in valores]
        if "fecha" in valores_norm and "magnitud" in valores_norm and "profundidadkm" in valores_norm:
            fila_cabecera = indice
            break

    if fila_cabecera is None:
        raise ValueError("No se encontro la cabecera real del CSV de sismos.")

    cabecera = df.iloc[fila_cabecera].tolist()
    df = df.iloc[fila_cabecera + 1 :].copy()
    df.columns = [normalizar_nombre_columna(columna) for columna in cabecera]

    # Convierte columnas numéricas y de fecha a tipos útiles para análisis
    columnas_numericas = ["magnitud", "profundidadkm", "latitud", "longitud"]
    for columna in columnas_numericas:
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna].astype(str).str.replace(",", "."), errors="coerce")

    if "fecha" in df.columns and "horalocal" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horalocal"].astype(str), errors="coerce")

    return df.reset_index(drop=True)


def obtener_anio_usuario(valor: str | int | None = None) -> int:
    # Permite pasar el año como argumento, usar el año actual o pedirlo si hay terminal interactiva
    anio_actual = date.today().year

    if valor is not None:
        anio = int(valor)
    elif sys.stdin.isatty():
        entrada = input(f"Ano a descargar ({ANIO_MIN}-{anio_actual}) [{anio_actual}]: ").strip()
        anio = int(entrada or anio_actual)
    else:
        anio = anio_actual

    if not ANIO_MIN <= anio <= anio_actual:
        raise ValueError(f"El ano debe estar entre {ANIO_MIN} y {anio_actual}.")

    return anio

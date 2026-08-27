import sys
from pathlib import Path

from lectura_datos import descargar_sismos, cargar_datos, obtener_anio_usuario
from funciones_sismos import (
    comparar_con_media,
    localizaciones_repetidas,
    mostrar_graficos,
    resumen_anual,
)


# Busca el CSV más reciente dentro del mismo directorio del proyecto
# Si no existe ninguno, solicita el año y descarga uno nuevo

def seleccionar_archivo() -> Path:
    archivos_csv = sorted(Path.cwd().glob("sismicidad_*.csv"))

    if archivos_csv:
        print("Archivos CSV disponibles:")
        for i, archivo in enumerate(archivos_csv, start=1):
            print(f"{i}. {archivo.name}")

        opcion = input("Presiona Enter para usar el más reciente o escribe el nombre del archivo: ").strip()
        if not opcion:
            return archivos_csv[-1]

        archivo = Path(opcion)
        if archivo.exists():
            return archivo

        print("Archivo no encontrado. Se usara el más reciente disponible.")
        return archivos_csv[-1]

    anio = obtener_anio_usuario(sys.argv[1] if len(sys.argv) > 1 else None)
    return descargar_sismos(anio)


# Muestra el menu principal con las opciones del proyecto

def menu_principal() -> None:
    print("\n========================")
    print("SISTEMA DE ANALISIS DE SISMOS")
    print("========================")
    print("1. Resumen anual del total de sismos sentidos")
    print("2. Comparacion con la media (magnitud y profundidad)")
    print("3. Localizacion repetida")
    print("4. Mostrar graficos")
    print("5. Salir")
    print("========================")


# Ejecuta la opción elegida por el usuario y repite hasta salir

def ejecutar_menu(df) -> None:
    while True:
        menu_principal()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            print(resumen_anual(df))
        elif opcion == "2":
            print(comparar_con_media(df))
        elif opcion == "3":
            print(localizaciones_repetidas(df, top_n=10))
        elif opcion == "4":
            mostrar_graficos(df)
        elif opcion == "5":
            print("Saliendo del sistema...")
            break
        else:
            print("Opcion no valida. Intente nuevamente.")

        continuar = input("\nDesea volver al menu principal? (s/n): ").strip().lower()
        if continuar not in ["s", "si", "y", "yes"]:
            print("Saliendo del sistema...")
            break


# Punto de entrada de la aplicacion
if __name__ == "__main__":
    archivo_csv = seleccionar_archivo()
    df = cargar_datos(archivo_csv)
    print(f"\nArchivo cargado: {archivo_csv}")
    ejecutar_menu(df)

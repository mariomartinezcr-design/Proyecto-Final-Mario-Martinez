# Informe del proyecto:

## 1. Introducción

Este proyecto consiste en una aplicación de consola para analizar los sismos sentidos registrados durante un año. El programa utiliza datos obtenidos de un archivo CSV, calcula estadísticas básicas, identifica ubicaciones repetidas y genera gráficos para facilitar la interpretación de la información.

La solución se diseñó de forma modular para separar la lectura y preparación de los datos, la lógica de análisis y la interacción con el usuario. Esta separación permite que cada parte del programa tenga una responsabilidad clara y que los cambios puedan realizarse sin afectar todo el sistema.

## 2. Objetivo del proyecto

El objetivo principal es convertir una tabla de registros sísmicos en información útil y fácil de consultar. El usuario puede:

- Conocer cuántos sismos sentidos se registraron en el año.
- Consultar la magnitud y la profundidad máximas.
- Comparar los datos con sus medias.
- Saber si el último sismo está por encima, por debajo o igual a la media de magnitud y profundidad.
- Detectar ubicaciones que aparecen repetidas.
- Observar los datos mediante gráficos.

El archivo utilizado como ejemplo es `sismicidad_2026.csv`, que contiene 128 registros de sismos.

## 3. Organización general del sistema

El proyecto está dividido en tres módulos principales:

### `appSismo.py`

Es el punto de entrada y controla la interacción con el usuario. Sus responsabilidades son:

- Buscar archivos CSV disponibles.
- Permitir seleccionar un archivo o descargar los datos de un año.
- Cargar el archivo seleccionado.
- Mostrar el menú principal.
- Ejecutar la función correspondiente a cada opción.

Este módulo no realiza directamente los cálculos. Delega esa tarea en `funciones_sismos.py`, lo que mantiene más sencilla la parte de interfaz.

### `lectura_datos.py`

Se ocupa de obtener y preparar los datos. Sus funciones principales son:

- `descargar_sismos(anio)`: realiza una solicitud al sitio de OVSICORI, localiza la tabla de sismos y la guarda como CSV.
- `cargar_datos(ruta_csv)`: lee el archivo, encuentra la cabecera real, asigna los nombres de columnas y convierte los datos a tipos adecuados.
- `obtener_anio_usuario(valor)`: valida el año que se desea consultar.

### `funciones_sismos.py`

Contiene la lógica del análisis. Sus funciones producen los resúmenes, las comparaciones, el conteo de ubicaciones repetidas y los gráficos.

## 4. Por qué se escogieron estas estructuras

### DataFrame de pandas

Se escogió `pandas.DataFrame` como estructura principal porque los datos tienen forma de tabla: cada fila representa un sismo y cada columna representa una característica, como fecha, magnitud, profundidad o localización.

El `DataFrame` permite:

- Seleccionar columnas por nombre.
- Convertir columnas completas a valores numéricos.
- Calcular medias y valores máximos.
- Contar valores repetidos.
- Trabajar con fechas y ordenar o localizar registros.

Esto evita recorrer manualmente cada fila para operaciones que pandas puede realizar de forma clara y eficiente.

### Series de pandas

Las columnas se manejan como `Series`. Por ejemplo, la magnitud y la profundidad se convierten en series numéricas antes de calcular sus medias. Esto permite aplicar operaciones como `mean()`, `max()` y comparaciones elemento por elemento.

### Diccionarios

En `obtener_columna()` se utiliza un diccionario para relacionar el nombre normalizado de cada columna con su nombre original. La búsqueda es rápida y permite trabajar con encabezados que tengan diferencias de mayúsculas, tildes, espacios o símbolos.

### Listas

Las listas se utilizan para:

- Guardar los nombres alternativos posibles de una columna.
- Construir progresivamente las líneas de los informes de texto.
- Recibir las tablas encontradas durante la descarga HTML.

### `Path` de pathlib

Se utiliza `Path` para buscar archivos CSV y construir rutas. Esta estructura es más segura y legible que manipular rutas únicamente como cadenas de texto.

## 5. Preparación de los datos

El CSV descargado no presenta directamente una cabecera limpia. Antes de la cabecera real aparece una fila informativa que indica el año y el total de sismos. Por esa razón, `cargar_datos()` lee inicialmente el archivo sin asumir que la primera fila contiene los nombres correctos.

El procedimiento aplicado es:

1. Leer el CSV con `header=None`.
2. Recorrer las filas hasta encontrar una que contenga las palabras `Fecha`, `Magnitud` y `Profundidad (km)`.
3. Usar esa fila como cabecera real.
4. Eliminar las filas anteriores.
5. Normalizar los nombres de las columnas.
6. Convertir magnitud, profundidad, latitud y longitud a números.
7. Unir la fecha y la hora local en una columna de tipo fecha.
8. Reiniciar los índices del `DataFrame`.

La conversión numérica utiliza `errors="coerce"`. Esto significa que un valor inválido se transforma en `NaN` en vez de detener todo el programa. Como consecuencia, pandas puede ignorar esos valores al calcular medias o máximos.

## 6. Normalización de nombres de columnas

La función `normalizar_nombre_columna()` realiza tres operaciones:

1. Elimina espacios al inicio y al final.
2. Convierte el texto a minúsculas.
3. Elimina tildes, espacios y símbolos que puedan dificultar la comparación.

Por ejemplo, `Profundidad (km)` se transforma en `profundidadkm`. Esto permite que el resto del programa encuentre la columna aunque el archivo use una escritura ligeramente diferente.

La función `obtener_columna()` recibe una lista de nombres posibles. Así, una columna de magnitud puede buscarse como `magnitud`, `magnitude` o `mag`. Si ninguna alternativa existe, se lanza un `KeyError` con un mensaje explicativo.

Esta decisión hace que el programa sea más resistente a variaciones en los archivos de entrada.

## 7. Lógica del resumen anual

La función `resumen_anual(df)` realiza estas operaciones:

1. Localiza las columnas de magnitud, profundidad y fecha.
2. Cuenta los registros mediante `len(df)`.
3. Convierte magnitud y profundidad a valores numéricos.
4. Calcula la magnitud máxima y la profundidad máxima.
5. Convierte la fecha a formato de fecha y hora.
6. Localiza el registro con la fecha más reciente mediante `idxmax()`.
7. Obtiene de ese registro la magnitud y profundidad del último sismo.
8. Calcula la media de magnitud y profundidad.
9. Compara el último sismo con cada media.

La comparación utiliza una función interna llamada `comparar()`. La lógica es:

- Si el valor es mayor que la media, devuelve `por encima`.
- Si el valor es menor que la media, devuelve `por debajo`.
- Si ambos valores son iguales, devuelve `igual`.

Por ello, el resumen puede indicar, por ejemplo:

- El último sismo sentido está por debajo de la media en magnitud.
- El último sismo sentido está por debajo de la media en profundidad.

## 8. Comparación general con la media

La función `comparar_con_media(df)` calcula por separado:

- La media de magnitud.
- La cantidad de sismos con magnitud mayor que la media.
- La cantidad de sismos con magnitud menor que la media.
- La media de profundidad.
- La cantidad de sismos con profundidad mayor que la media.
- La cantidad de sismos con profundidad menor que la media.

Las expresiones booleanas, como `magnitudes > media_magnitud`, producen valores verdaderos o falsos para cada registro. Al aplicar `.sum()`, los valores verdaderos se cuentan como sismos que cumplen la condición.

Los valores exactamente iguales a la media no se incluyen ni en el grupo superior ni en el inferior. Esto evita clasificarlos incorrectamente.

## 9. Lógica de las ubicaciones repetidas

Las localizaciones del sitio web son descripciones completas, por ejemplo: `8 km al noreste de ...`. Para agrupar lugares similares, el programa elimina las primeras cinco palabras de cada descripción:

```python
" ".join(texto.split()[5:])
```

Después utiliza `value_counts()` para contar cuántas veces aparece cada ubicación agrupada y muestra las primeras diez mediante `head(10)`.

También se muestra el total de ubicaciones distintas calculado con `nunique()`. En el archivo actual:

- Hay 128 registros de sismos.
- Hay 110 textos de localización diferentes sin agrupar.
- Hay 89 ubicaciones distintas después de aplicar la regla de agrupación.
- Hay 14 ubicaciones agrupadas que aparecen más de una vez.

La cifra de 89 es la que utiliza actualmente la aplicación. Es importante aclarar que se basa en una regla textual, no en coordenadas geográficas. Por eso dos textos que se refieran al mismo sitio podrían permanecer separados si tienen diferencias como un punto final, una tilde o una forma distinta de escribir el nombre.

## 10. Lógica de los gráficos

La función `mostrar_graficos(df)` usa Matplotlib y crea cuatro visualizaciones:

1. Magnitud por fecha: muestra la variación de la magnitud a lo largo del tiempo.
2. Profundidad por fecha: muestra cómo cambia la profundidad de los sismos.
3. Histograma de magnitudes: muestra la frecuencia de los diferentes rangos de magnitud.
4. Barras de ubicaciones: muestra las diez ubicaciones agrupadas con mayor número de registros.

En los gráficos de líneas se convierte la fecha con `pd.to_datetime()`. Para los gráficos de barras se reutiliza la misma transformación de ubicaciones que se usa en el informe textual, con el fin de que ambos resultados sean coherentes.

Cada figura se muestra con `plt.show()` y luego se cierra con `plt.close()`, evitando que las figuras anteriores queden abiertas o consuman recursos innecesariamente.

## 11. Flujo de ejecución del programa

El flujo completo es el siguiente:

1. Se ejecuta `appSismo.py`.
2. `seleccionar_archivo()` busca archivos con el patrón `sismicidad_*.csv`.
3. El usuario selecciona un archivo o se descarga uno nuevo.
4. `cargar_datos()` prepara el contenido y devuelve un `DataFrame`.
5. Se muestra el menú principal.
6. El usuario escoge una opción.
7. `ejecutar_menu()` llama a la función de análisis correspondiente.
8. Se muestra el resultado.
9. El programa pregunta si se desea volver al menú.
10. El ciclo continúa hasta que el usuario selecciona salir.

## 12. Situaciones en que el código no funcionó y cómo se resolvieron

### 12.1. La cabecera no estaba en la primera fila

Al leer el CSV de forma convencional, pandas podía interpretar la fila informativa del año como cabecera. Esto provocaba que las columnas no tuvieran nombres útiles y que las funciones no encontraran `magnitud`, `fecha` o `profundidad`.

Se resolvió leyendo el archivo con `header=None`, buscando la fila que contiene los nombres reales y asignándola como cabecera después.

### 12.2. Diferencias en los nombres de columnas

El archivo usa nombres como `Profundidad (km)`, mientras que las funciones necesitan encontrar esa columna con un nombre sencillo. Las tildes, los espacios y los paréntesis podían provocar errores de búsqueda.

Se resolvió normalizando los nombres y permitiendo varias alternativas mediante `obtener_columna()`.

### 12.3. Valores numéricos con formatos variables

Los números podían venir como texto o utilizar coma decimal. Si se intentaba calcular directamente una media, podían aparecer errores o resultados incorrectos.

Se resolvió convirtiendo las columnas con `pd.to_numeric()` y reemplazando la coma por punto en `cargar_datos()`.

### 12.4. El último registro no era necesariamente el último sismo

Inicialmente podía parecer correcto usar `df.iloc[-1]`. Sin embargo, el CSV actual está ordenado del registro más reciente al más antiguo. Por eso la última fila corresponde al sismo más antiguo.

Se resolvió tomando la fecha máxima con `pd.to_datetime()` y `idxmax()`. De esa manera se identifica el último sismo por su fecha real, independientemente del orden de las filas.

### 12.5. Los gráficos no se veían

El código utilizaba el backend `Agg` de Matplotlib. Ese backend permite crear gráficos sin interfaz, pero no abre ventanas, por lo que `plt.show()` no mostraba los gráficos al usuario.

Se resolvió eliminando la selección forzada de `Agg` y permitiendo que Matplotlib utilizara el backend gráfico disponible, `TkAgg`. También se agregó `plt.close()` después de cada gráfico.

### 12.6. Se mostraban pocas ubicaciones

La función utiliza `head(10)`, por lo que solo muestra las diez ubicaciones más frecuentes. Esto no significa que existan únicamente diez ubicaciones en el archivo.

Se resolvió agregando el total de ubicaciones distintas mediante `nunique()`. Para el CSV actual, el resultado es de 89 ubicaciones agrupadas.

### 12.7. Ubicaciones aparentemente iguales podían aparecer separadas

Una ubicación como `Jacó` y otra como `Jacó.` se consideran textos diferentes porque el punto final forma parte de la cadena. Esto puede dividir el conteo de un mismo lugar.

La solución actual reduce las descripciones eliminando las primeras cinco palabras, pero todavía conserva diferencias de puntuación. Esta es una mejora pendiente si se desea una agrupación geográfica más exacta: habría que limpiar la puntuación y, preferiblemente, utilizar coordenadas de latitud y longitud.

## 13. Decisiones de diseño y sus ventajas

La aplicación se hizo por módulos porque cada módulo responde a una necesidad diferente. Esto facilita la lectura, las pruebas y el mantenimiento.

Se eligió una interfaz de consola porque el objetivo principal era practicar lectura de archivos, procesamiento de datos, funciones, estructuras de control y visualización. El menú hace que las funciones puedan probarse sin modificar el código.

Se utilizaron funciones independientes para cada análisis. Así, `resumen_anual()`, `comparar_con_media()`, `localizaciones_repetidas()` y `mostrar_graficos()` pueden recibir el mismo `DataFrame`, trabajar de forma independiente y devolver un resultado específico.

También se agregaron validaciones y mensajes de error para que los problemas del archivo sean detectables, en lugar de producir resultados silenciosamente incorrectos.

## 14. Limitaciones actuales y posibles mejoras

- La aplicación depende de que el sitio web mantenga una tabla con nueve columnas.
- La agrupación de ubicaciones se basa en texto y no en una distancia geográfica.
- Si todas las fechas fueran inválidas, `idxmax()` no tendría un registro válido para seleccionar.
- El menú funciona en consola y no posee una interfaz gráfica.
- Los gráficos se muestran uno después de otro, por lo que el usuario debe cerrar o avanzar por cada ventana según el comportamiento del backend.
Se decidió mostrar los gráficos uno tras otro porque cada llamada a plt.show() pausa la ejecución hasta que el usuario cierra la ventana actual. Esto permite analizar cada visualización por separado. Mostrar los cuatro simultáneamente podría saturar la pantalla y dificultar la lectura, especialmente en equipos con poco espacio. Además, usar plt.close() después de cada gráfico libera memoria y evita que las figuras se acumulen.

La desventaja es que el usuario debe cerrar cada ventana para pasar a la siguiente. Una mejora futura sería crear una sola ventana con cuatro subgráficos.
- Sería conveniente agregar pruebas automatizadas para casos como un CSV vacío, fechas inválidas, columnas ausentes y ubicaciones con signos de puntuación diferentes.

## 15. Conclusión

El proyecto se diseñó como un sistema sencillo, modular y resistente a las características reales del archivo de datos. La estructura separa la adquisición, la preparación, el análisis y la interacción, mientras que pandas y Matplotlib permiten resolver de manera directa las operaciones estadísticas y visuales.

Las dificultades encontradas fueron importantes para mejorar la solución: el formato irregular del CSV obligó a detectar la cabecera real; las variaciones de nombres requirieron normalización; el orden descendente de las fechas obligó a localizar el último sismo por fecha; y el backend no interactivo impedía visualizar los gráficos. Cada problema se resolvió ajustando la lógica al comportamiento real de los datos y del entorno de ejecución.

Como resultado, el programa puede transformar los 128 registros del archivo `sismicidad_2026.csv` en un resumen anual, comparaciones estadísticas, un conteo de ubicaciones repetidas y representaciones gráficas comprensibles.

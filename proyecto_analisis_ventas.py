from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# 0. CONFIGURACIÓN GENERAL
# ============================================================

CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_DATOS = CARPETA_PROYECTO / "data"
CARPETA_SALIDA = CARPETA_PROYECTO / "outputs"

ARCHIVO_EXCEL = CARPETA_DATOS / "Contoso Sales.xlsx"
ARCHIVO_VENTAS = CARPETA_DATOS / "FactSales.txt"

CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

COLUMNAS_FACT_ORIGINALES = [
    "OrderID", "DateKey", "channelKey", "StoreKey", "ProductKey",
    "PromotionKey", "SalesQuantity", "ReturnQuantity", "Cantidad_total",
    "Devolución", "Venta_type", "Devolución_type", "Precio_unitario", "Ingresos"
]


# ============================================================
# 1. FUNCIONES AUXILIARES
# ============================================================

def verificar_archivos() -> None:
    """Comprueba que los archivos de entrada estén en la carpeta data."""
    print("=== REVISIÓN DE ARCHIVOS DE ENTRADA ===")
    print(f"Excel encontrado: {ARCHIVO_EXCEL.exists()} -> {ARCHIVO_EXCEL}")
    print(f"FactSales encontrado: {ARCHIVO_VENTAS.exists()} -> {ARCHIVO_VENTAS}")

    faltantes = []
    if not ARCHIVO_EXCEL.exists():
        faltantes.append(str(ARCHIVO_EXCEL))
    if not ARCHIVO_VENTAS.exists():
        faltantes.append(str(ARCHIVO_VENTAS))

    if faltantes:
        mensaje = (
            "No se encontraron todos los archivos requeridos.\n"
            "Revise que exista una carpeta llamada 'data' junto al script y que contenga:\n"
            "  - Contoso Sales.xlsx\n"
            "  - FactSales.txt\n\n"
            "Archivos faltantes:\n" + "\n".join(f"  - {f}" for f in faltantes)
        )
        raise FileNotFoundError(mensaje)


def exportar_csv(df: pd.DataFrame, nombre_archivo: str, ordenar_por: str | None = None,
                 ascendente: bool = False) -> pd.DataFrame:
    """Guarda un DataFrame en outputs y devuelve el mismo DataFrame."""
    tabla = df.copy()
    if ordenar_por is not None and ordenar_por in tabla.columns:
        tabla = tabla.sort_values(ordenar_por, ascending=ascendente)

    ruta = CARPETA_SALIDA / nombre_archivo
    tabla.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"Archivo generado: {nombre_archivo} ({tabla.shape[0]} filas, {tabla.shape[1]} columnas)")
    return tabla


def limpiar_numero_latino(serie: pd.Series) -> pd.Series:
    """Convierte textos con coma decimal y espacios de miles a valores numéricos."""
    texto = (
        serie.astype(str)
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    return pd.to_numeric(texto, errors="coerce")


def cargar_excel_completo(ruta_excel: Path) -> dict[str, pd.DataFrame]:
    """Lee todas las hojas del archivo Excel y las devuelve en un diccionario."""
    libro = pd.ExcelFile(ruta_excel)
    print("\n=== HOJAS DETECTADAS EN EL EXCEL ===")
    for hoja in libro.sheet_names:
        print(f"- {hoja}")

    tablas = {hoja: pd.read_excel(ruta_excel, sheet_name=hoja) for hoja in libro.sheet_names}

    print("\n=== DIMENSIONES DE TABLAS DEL EXCEL ===")
    for nombre, df in tablas.items():
        print(f"{nombre}: {df.shape[0]} filas x {df.shape[1]} columnas")
    return tablas


def cargar_fact_sales(ruta_txt: Path) -> pd.DataFrame:
    """Lee FactSales usando distintas codificaciones si es necesario."""
    codificaciones = ["utf-8-sig", "utf-8", "latin1"]
    ultimo_error: Exception | None = None

    for codificacion in codificaciones:
        try:
            ventas = pd.read_csv(
                ruta_txt,
                sep="\t",
                encoding=codificacion,
                low_memory=False
            )
            print(f"\nFactSales leído con codificación: {codificacion}")
            print(f"FactSales: {ventas.shape[0]} filas x {ventas.shape[1]} columnas")
            return ventas
        except UnicodeDecodeError as error:
            ultimo_error = error

    raise UnicodeDecodeError(
        "utf-8-sig",
        b"",
        0,
        1,
        f"No fue posible leer FactSales. Último error: {ultimo_error}"
    )


def preparar_fact_sales(ventas: pd.DataFrame) -> pd.DataFrame:
    """Ajusta fechas, cantidades y montos para que puedan analizarse."""
    df = ventas.copy()

    columnas_necesarias = [
        "DateKey", "Precio_unitario", "Ingresos", "SalesQuantity",
        "ReturnQuantity", "Cantidad_total"
    ]
    faltantes = [col for col in columnas_necesarias if col not in df.columns]
    if faltantes:
        raise KeyError(f"FactSales no contiene estas columnas necesarias: {faltantes}")

    df["DateKey"] = pd.to_datetime(df["DateKey"], dayfirst=True, errors="coerce").dt.normalize()
    df["Precio_unitario"] = limpiar_numero_latino(df["Precio_unitario"])
    df["Ingresos"] = limpiar_numero_latino(df["Ingresos"])

    for columna in ["SalesQuantity", "ReturnQuantity", "Cantidad_total"]:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    df["Ingresos_calculados"] = df["Precio_unitario"] * df["Cantidad_total"]
    df["Diferencia_ingresos"] = df["Ingresos"] - df["Ingresos_calculados"]
    return df


def clasificar_variable(nombre_columna: str, tipo_dato: str) -> str:
    """Asigna una categoría estadística básica a una variable."""
    nombre = nombre_columna.lower()
    tipo = tipo_dato.lower()

    fechas = {"datekey", "startdate", "enddate"}
    discretas = {"salesquantity", "returnquantity", "cantidad_total", "employeecount", "promo_days"}
    continuas = {"precio_unitario", "ingresos", "unitcost", "unitprice", "weight", "discountpercent", "sellingareasize"}
    identificadores = {"orderid", "promotionlabel", "classid", "colorid"}

    if nombre in fechas or "datetime" in tipo:
        return "Fecha"
    if nombre in discretas:
        return "Discreta"
    if nombre in continuas:
        return "Continua"
    if nombre.endswith("key") or nombre.endswith("id") or nombre in identificadores:
        return "Identificador"
    if "object" in tipo or "string" in tipo:
        return "Categórica"
    if "int" in tipo:
        return "Discreta"
    if "float" in tipo:
        return "Continua"
    return "Otra"


def frecuencias_empiricas(df: pd.DataFrame, columna: str, archivo: str) -> pd.DataFrame:
    """Calcula frecuencia absoluta y probabilidad empírica para una columna."""
    salida = df[columna].value_counts(dropna=False).reset_index()
    salida.columns = [columna, "Frecuencia"]
    salida["Probabilidad_empirica"] = salida["Frecuencia"] / len(df)
    return exportar_csv(salida, archivo)


def resumen_metricas(df: pd.DataFrame, grupos: list[str]) -> pd.DataFrame:
    """Resume ventas, devoluciones, ingresos y tasas por grupo."""
    resumen = (
        df.groupby(grupos, dropna=False)
        .agg(
            Numero_ordenes=("OrderID", "count"),
            Numero_ordenes_con_devolucion=("ReturnQuantity", lambda x: (x > 0).sum()),
            Cantidad_Ventas=("SalesQuantity", "sum"),
            Cantidad_Devoluciones=("ReturnQuantity", "sum"),
            Cantidad_Total=("Cantidad_total", "sum"),
            Total_ingresos=("Ingresos", "sum")
        )
        .reset_index()
    )

    resumen["Tasa_devolucion_unidades"] = 0.0
    con_ventas = resumen["Cantidad_Ventas"] != 0
    resumen.loc[con_ventas, "Tasa_devolucion_unidades"] = (
        resumen.loc[con_ventas, "Cantidad_Devoluciones"] / resumen.loc[con_ventas, "Cantidad_Ventas"]
    )

    resumen["Tasa_ordenes_con_devolucion"] = 0.0
    con_ordenes = resumen["Numero_ordenes"] != 0
    resumen.loc[con_ordenes, "Tasa_ordenes_con_devolucion"] = (
        resumen.loc[con_ordenes, "Numero_ordenes_con_devolucion"] / resumen.loc[con_ordenes, "Numero_ordenes"]
    )

    resumen["Ingreso_promedio_por_orden"] = 0.0
    resumen.loc[con_ordenes, "Ingreso_promedio_por_orden"] = (
        resumen.loc[con_ordenes, "Total_ingresos"] / resumen.loc[con_ordenes, "Numero_ordenes"]
    )
    return resumen


def seleccionar(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Devuelve columnas existentes y avisa si falta alguna columna esperada."""
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas faltantes en tabla: {faltantes}")
    return df[columnas].copy()


# ============================================================
# 2. ANÁLISIS PRELIMINAR
# ============================================================

def generar_resumen_tablas(tablas: dict[str, pd.DataFrame], fact: pd.DataFrame,
                           muestra_fact: pd.DataFrame) -> pd.DataFrame:
    registros = []
    for nombre, df in tablas.items():
        registros.append({
            "Tabla": nombre,
            "Filas": df.shape[0],
            "Columnas": df.shape[1],
            "Celdas_nulas_totales": int(df.isna().sum().sum()),
            "Columnas_con_nulos": int((df.isna().sum() > 0).sum())
        })

    registros.append({
        "Tabla": "FactSales_muestra_1000_filas",
        "Filas": muestra_fact.shape[0],
        "Columnas": muestra_fact.shape[1],
        "Celdas_nulas_totales": int(muestra_fact.isna().sum().sum()),
        "Columnas_con_nulos": int((muestra_fact.isna().sum() > 0).sum())
    })

    registros.append({
        "Tabla": "FactSales_completo",
        "Filas": fact.shape[0],
        "Columnas": fact.shape[1],
        "Celdas_nulas_totales": int(fact.isna().sum().sum()),
        "Columnas_con_nulos": int((fact.isna().sum() > 0).sum())
    })
    return exportar_csv(pd.DataFrame(registros), "01_resumen_preliminar_tablas.csv")


def generar_tipos_datos(tablas: dict[str, pd.DataFrame], fact: pd.DataFrame,
                        muestra_fact: pd.DataFrame) -> pd.DataFrame:
    registros = []

    def agregar_tabla(nombre: str, df: pd.DataFrame) -> None:
        for columna in df.columns:
            registros.append({
                "Tabla": nombre,
                "Columna": columna,
                "Tipo_dato": str(df[columna].dtype),
                "Valores_nulos": int(df[columna].isna().sum()),
                "Valores_unicos": int(df[columna].nunique(dropna=True))
            })

    for nombre, df in tablas.items():
        agregar_tabla(nombre, df)
    agregar_tabla("FactSales_muestra_1000_filas", muestra_fact)
    agregar_tabla("FactSales_completo_limpio", fact)

    return exportar_csv(pd.DataFrame(registros), "02_tipos_datos_columnas.csv")


def generar_nulos_fact(fact: pd.DataFrame) -> pd.DataFrame:
    nulos = pd.DataFrame({
        "Columna": fact.columns,
        "Valores_nulos": fact.isna().sum().values,
        "Porcentaje_nulos": (fact.isna().sum().values / len(fact)) * 100
    })
    return exportar_csv(nulos, "03_nulos_fact_sales_completo.csv")


def generar_rango_fechas(fact: pd.DataFrame) -> pd.DataFrame:
    fechas = pd.DataFrame({
        "Indicador": ["Fecha mínima", "Fecha máxima", "Cantidad de fechas únicas"],
        "Valor": [fact["DateKey"].min(), fact["DateKey"].max(), fact["DateKey"].nunique()]
    })
    return exportar_csv(fechas, "04_rango_fechas_fact_sales.csv")


def generar_estadisticas_fact(fact: pd.DataFrame) -> pd.DataFrame:
    columnas = ["SalesQuantity", "ReturnQuantity", "Cantidad_total", "Precio_unitario", "Ingresos"]
    estadisticas = fact[columnas].agg([
        "count", "mean", "median", "std", "var", "min", "max", "skew"
    ]).T
    estadisticas["Curtosis"] = fact[columnas].kurtosis()
    estadisticas = estadisticas.rename(columns={
        "count": "Cantidad_datos",
        "mean": "Media",
        "median": "Mediana",
        "std": "Desviacion_estandar",
        "var": "Varianza",
        "min": "Minimo",
        "max": "Maximo",
        "skew": "Asimetria"
    }).rename_axis("Variable").reset_index()
    return exportar_csv(estadisticas, "05_estadisticas_fact_sales.csv")


def validar_ingresos(fact: pd.DataFrame) -> pd.DataFrame:
    validacion = pd.DataFrame({
        "Indicador": [
            "Diferencia absoluta promedio",
            "Diferencia absoluta máxima",
            "Registros con diferencia mayor a 0.01"
        ],
        "Valor": [
            fact["Diferencia_ingresos"].abs().mean(),
            fact["Diferencia_ingresos"].abs().max(),
            int((fact["Diferencia_ingresos"].abs() > 0.01).sum())
        ]
    })
    return exportar_csv(validacion, "11_validacion_ingresos.csv")


# ============================================================
# MEJORA 2: DimCalendar incluida en el diccionario de tablas
# ============================================================

def generar_diccionario_tablas() -> pd.DataFrame:
    """
    Genera el diccionario de tablas del modelo.
    MEJORA: se agrega DimCalendar, que antes faltaba aunque se creaba en ejecución.
    """
    datos = [
        ["FactSales", "Tabla de hechos", "Registro de venta por orden, producto, tienda, canal, promoción y fecha.", "Base para ingresos, ventas, devoluciones y métricas."],
        ["DimChannel", "Tabla dimensional", "Canal comercial.", "Análisis de ventas por canal."],
        ["DimGeography", "Tabla dimensional", "Zona geográfica asociada a tiendas.", "Análisis por continente, país o región."],
        ["DimProduct", "Tabla dimensional", "Producto del catálogo.", "Análisis por producto, marca, fabricante, costo y precio."],
        ["DimProductCategory", "Tabla dimensional", "Categoría general de producto.", "Agrupación de productos por categoría."],
        ["DimProductSubCategory", "Tabla dimensional", "Subcategoría de producto.", "Conecta productos con categorías generales."],
        ["DimPromotion", "Tabla dimensional", "Promoción o campaña.", "Análisis por descuento o promoción."],
        ["DimStores", "Tabla dimensional", "Tienda de Contoso.", "Análisis por tienda, tipo, empleados y tamaño."],
        # MEJORA 2: DimCalendar ahora aparece en el diccionario
        ["DimCalendar", "Tabla dimensional (derivada)", "Una fila por día del rango de ventas.", "Permite análisis temporal: año, mes, trimestre, día de semana. Creada a partir del rango de fechas de FactSales."],
    ]
    diccionario = pd.DataFrame(datos, columns=[
        "Tabla", "Tipo_tabla", "Que_representa_cada_fila", "Uso_en_el_modelo"
    ])
    return exportar_csv(diccionario, "12_diccionario_tablas.csv")


def generar_clasificacion_variables(tablas: dict[str, pd.DataFrame], fact: pd.DataFrame) -> pd.DataFrame:
    registros = []

    def agregar(nombre: str, df: pd.DataFrame) -> None:
        for columna in df.columns:
            if columna in ["Ingresos_calculados", "Diferencia_ingresos"]:
                continue
            tipo = str(df[columna].dtype)
            registros.append({
                "Tabla": nombre,
                "Columna": columna,
                "Tipo_dato_python": tipo,
                "Clasificacion_variable": clasificar_variable(columna, tipo),
                "Valores_nulos": int(df[columna].isna().sum()),
                "Porcentaje_nulos": (df[columna].isna().sum() / len(df)) * 100,
                "Valores_unicos": int(df[columna].nunique(dropna=True))
            })

    for nombre, df in tablas.items():
        agregar(nombre, df)
    agregar("FactSales", fact)
    return exportar_csv(pd.DataFrame(registros), "13_clasificacion_variables.csv")


def generar_estadisticas_generales(tablas: dict[str, pd.DataFrame], fact: pd.DataFrame) -> pd.DataFrame:
    registros = []

    def agregar(nombre_tabla: str, df: pd.DataFrame) -> None:
        for columna in df.columns:
            tipo = str(df[columna].dtype)
            clase = clasificar_variable(columna, tipo)
            if clase not in ["Discreta", "Continua"]:
                continue
            serie = pd.to_numeric(df[columna], errors="coerce")
            registros.append({
                "Tabla": nombre_tabla,
                "Columna": columna,
                "Clasificacion_variable": clase,
                "Cantidad_datos": serie.count(),
                "Media": serie.mean(),
                "Mediana": serie.median(),
                "Desviacion_estandar": serie.std(),
                "Varianza": serie.var(),
                "Minimo": serie.min(),
                "Maximo": serie.max(),
                "Asimetria": serie.skew(),
                "Curtosis": serie.kurtosis()
            })

    for nombre, df in tablas.items():
        agregar(nombre, df)
    agregar("FactSales", fact[[col for col in COLUMNAS_FACT_ORIGINALES if col in fact.columns]])
    return exportar_csv(pd.DataFrame(registros), "14_estadisticas_numericas_todas_tablas.csv")


def generar_frecuencias_relevantes(tablas: dict[str, pd.DataFrame], fact: pd.DataFrame) -> pd.DataFrame:
    variables = {
        "DimChannel": ["ChannelName"],
        "DimGeography": ["ContinentName", "RegionCountryName"],
        "DimProduct": ["Manufacturer", "BrandName", "ClassName", "ColorName"],
        "DimProductCategory": ["ProductCategory"],
        "DimProductSubCategory": ["ProductSubcategoryName"],
        "DimPromotion": ["PromotionName"],
        "DimStores": ["StoreType"],
        "FactSales": ["Devolución", "Venta_type", "Devolución_type"],
    }

    registros = []
    for nombre_tabla, columnas in variables.items():
        df = fact if nombre_tabla == "FactSales" else tablas[nombre_tabla]
        for columna in columnas:
            if columna not in df.columns:
                continue
            conteo = df[columna].value_counts(dropna=False).head(10)
            for valor, frecuencia in conteo.items():
                registros.append({
                    "Tabla": nombre_tabla,
                    "Columna": columna,
                    "Valor": valor,
                    "Frecuencia": int(frecuencia),
                    "Probabilidad_empirica": frecuencia / len(df)
                })
    return exportar_csv(pd.DataFrame(registros), "15_frecuencias_categoricas_relevantes.csv")


# ============================================================
# MEJORA 1: DETECCIÓN DE VALORES ATÍPICOS (IQR + Z-SCORE)
# ============================================================

def detectar_outliers(fact: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta valores atípicos en las columnas numéricas clave de FactSales
    usando dos métodos complementarios:
      - IQR  : un valor es atípico si cae fuera de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
      - Z-score: un valor es atípico si su z-score supera ±3 desviaciones estándar

    Genera el archivo 30_outliers_fact_sales.csv con el conteo y porcentaje
    de outliers por columna y por método.
    """
    columnas = ["SalesQuantity", "ReturnQuantity", "Cantidad_total", "Precio_unitario", "Ingresos"]
    registros = []

    for columna in columnas:
        serie = pd.to_numeric(fact[columna], errors="coerce").dropna()
        n = len(serie)

        # --- Método IQR ---
        q1 = serie.quantile(0.25)
        q3 = serie.quantile(0.75)
        iqr = q3 - q1
        limite_inf_iqr = q1 - 1.5 * iqr
        limite_sup_iqr = q3 + 1.5 * iqr
        outliers_iqr = int(((serie < limite_inf_iqr) | (serie > limite_sup_iqr)).sum())

        # --- Método Z-score ---
        media = serie.mean()
        std = serie.std()
        if std > 0:
            z_scores = (serie - media) / std
            outliers_z = int((z_scores.abs() > 3).sum())
        else:
            outliers_z = 0

        registros.append({
            "Columna": columna,
            "N_valores": n,
            # IQR
            "Q1": round(q1, 4),
            "Q3": round(q3, 4),
            "IQR": round(iqr, 4),
            "Limite_inferior_IQR": round(limite_inf_iqr, 4),
            "Limite_superior_IQR": round(limite_sup_iqr, 4),
            "Outliers_IQR": outliers_iqr,
            "Pct_outliers_IQR": round(outliers_iqr / n * 100, 4),
            # Z-score
            "Media": round(media, 4),
            "Desv_std": round(std, 4),
            "Outliers_Zscore": outliers_z,
            "Pct_outliers_Zscore": round(outliers_z / n * 100, 4),
        })

    return exportar_csv(pd.DataFrame(registros), "30_outliers_fact_sales.csv")


# ============================================================
# 3. MODELO RELACIONAL
# ============================================================

def crear_dim_calendar(fact: pd.DataFrame) -> pd.DataFrame:
    calendario = pd.DataFrame({
        "DateKey": pd.date_range(fact["DateKey"].min(), fact["DateKey"].max(), freq="D")
    })
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    dias = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }
    calendario["Anio"] = calendario["DateKey"].dt.year
    calendario["Mes"] = calendario["DateKey"].dt.month
    calendario["Nombre_mes"] = calendario["Mes"].map(meses)
    calendario["Trimestre"] = "T" + calendario["DateKey"].dt.quarter.astype(str)
    calendario["Dia"] = calendario["DateKey"].dt.day
    calendario["Dia_semana_num"] = calendario["DateKey"].dt.weekday + 1
    calendario["Nombre_dia"] = calendario["DateKey"].dt.weekday.map(dias)
    return exportar_csv(calendario, "18_dim_calendar.csv")


def definir_relaciones() -> pd.DataFrame:
    relaciones = [
        [1, "FactSales", "ProductKey", "DimProduct", "ProductKey", "Muchos a uno (*:1)", "DimProduct filtra FactSales", "Venta asociada con producto."],
        [2, "FactSales", "StoreKey", "DimStores", "StoreKey", "Muchos a uno (*:1)", "DimStores filtra FactSales", "Venta asociada con tienda."],
        [3, "FactSales", "channelKey", "DimChannel", "ChannelKey", "Muchos a uno (*:1)", "DimChannel filtra FactSales", "Venta asociada con canal."],
        [4, "FactSales", "PromotionKey", "DimPromotion", "PromotionKey", "Muchos a uno (*:1)", "DimPromotion filtra FactSales", "Venta asociada con promoción."],
        [5, "FactSales", "DateKey", "DimCalendar", "DateKey", "Muchos a uno (*:1)", "DimCalendar filtra FactSales", "Venta asociada con fecha."],
        [6, "DimStores", "GeographyKey", "DimGeography", "GeographyKey", "Muchos a uno (*:1)", "DimGeography filtra DimStores", "Tienda asociada con zona geográfica."],
        [7, "DimProduct", "ProductSubcategoryKey", "DimProductSubCategory", "ProductSubcategoryKey", "Muchos a uno (*:1)", "DimProductSubCategory filtra DimProduct", "Producto asociado con subcategoría."],
        [8, "DimProductSubCategory", "ProductCategoryKey", "DimProductCategory", "ProductCategoryKey", "Muchos a uno (*:1)", "DimProductCategory filtra DimProductSubCategory", "Subcategoría asociada con categoría."],
    ]
    columnas = [
        "Relacion_ID", "Tabla_origen", "Columna_origen", "Tabla_destino", "Columna_destino",
        "Cardinalidad_sugerida", "Direccion_filtro_sugerida", "Descripcion"
    ]
    return exportar_csv(pd.DataFrame(relaciones, columns=columnas), "16_relaciones_modelo.csv")


def validar_relaciones(tablas: dict[str, pd.DataFrame], fact: pd.DataFrame,
                       relaciones: pd.DataFrame) -> pd.DataFrame:
    def obtener(nombre: str) -> pd.DataFrame:
        return fact if nombre == "FactSales" else tablas[nombre]

    def ejemplos(valores: set, limite: int = 10) -> str:
        if not valores:
            return ""
        return ", ".join(sorted(map(str, valores))[:limite])

    registros = []
    for _, rel in relaciones.iterrows():
        origen = obtener(rel["Tabla_origen"])
        destino = obtener(rel["Tabla_destino"])
        serie_origen = origen[rel["Columna_origen"]]
        serie_destino = destino[rel["Columna_destino"]]

        claves_origen = set(serie_origen.dropna().unique())
        claves_destino = set(serie_destino.dropna().unique())
        sin_destino = claves_origen - claves_destino
        sin_uso = claves_destino - claves_origen
        duplicados_destino = int(serie_destino.duplicated().sum())

        estado = "OK" if (
            serie_origen.isna().sum() == 0
            and serie_destino.isna().sum() == 0
            and duplicados_destino == 0
            and len(sin_destino) == 0
        ) else "REVISAR"

        registros.append({
            "Relacion_ID": rel["Relacion_ID"],
            "Tabla_origen": rel["Tabla_origen"],
            "Columna_origen": rel["Columna_origen"],
            "Tabla_destino": rel["Tabla_destino"],
            "Columna_destino": rel["Columna_destino"],
            "Nulos_origen": int(serie_origen.isna().sum()),
            "Nulos_destino": int(serie_destino.isna().sum()),
            "Claves_unicas_origen": len(claves_origen),
            "Claves_unicas_destino": len(claves_destino),
            "Duplicados_en_clave_destino": duplicados_destino,
            "Claves_origen_sin_destino": len(sin_destino),
            "Claves_destino_sin_uso": len(sin_uso),
            "Ejemplos_origen_sin_destino": ejemplos(sin_destino),
            "Estado_validacion": estado
        })
    return exportar_csv(pd.DataFrame(registros), "17_validacion_relaciones.csv")


# ============================================================
# 4. MÉTRICAS DE NEGOCIO
# ============================================================

def indicadores_generales(fact: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    ventas = fact["SalesQuantity"].sum()
    devoluciones = fact["ReturnQuantity"].sum()
    cantidad_neta = fact["Cantidad_total"].sum()
    ingresos = fact["Ingresos"].sum()
    ordenes = len(fact)
    ordenes_con_devolucion = int((fact["ReturnQuantity"] > 0).sum())

    tiendas_total = tablas["DimStores"]["StoreKey"].nunique()
    tiendas_con_ventas = fact["StoreKey"].nunique()
    precio_promedio_catalogo = pd.to_numeric(tablas["DimProduct"]["UnitPrice"], errors="coerce").mean()

    datos = [
        ["Cantidad_Ventas", ventas, "Unidades vendidas antes de devoluciones."],
        ["Cantidad_Devoluciones", devoluciones, "Unidades devueltas."],
        ["Cantidad_Total", cantidad_neta, "Unidades netas después de devoluciones."],
        ["Total_ingresos", ingresos, "Ingresos netos totales."],
        ["Numero_ordenes", ordenes, "Cantidad de registros de venta."],
        ["Numero_ordenes_con_devolucion", ordenes_con_devolucion, "Registros con devolución."],
        ["Tasa_ordenes_con_devolucion", ordenes_con_devolucion / ordenes, "Proporción de órdenes con devolución."],
        ["Tasa_devolucion_unidades", devoluciones / ventas, "Unidades devueltas respecto a unidades vendidas."],
        ["Numero_stores", tiendas_total, "Tiendas registradas."],
        ["Numero_stores_con_ventas", tiendas_con_ventas, "Tiendas con ventas registradas."],
        ["Promedio_precio_unitario", precio_promedio_catalogo, "Precio unitario promedio del catálogo."],
        ["Ingreso_promedio_por_orden", ingresos / ordenes, "Ingreso promedio por registro de venta."],
    ]
    return exportar_csv(pd.DataFrame(datos, columns=["Indicador", "Valor", "Descripcion"]),
                        "19_indicadores_generales_negocio.csv")


def tablas_enriquecidas(fact: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    producto = seleccionar(tablas["DimProduct"], [
        "ProductKey", "ProductName", "ProductSubcategoryKey", "Manufacturer",
        "BrandName", "ClassName", "UnitCost", "UnitPrice"
    ])
    subcategoria = seleccionar(tablas["DimProductSubCategory"], [
        "ProductSubcategoryKey", "ProductSubcategoryName", "ProductCategoryKey"
    ])
    categoria = seleccionar(tablas["DimProductCategory"], [
        "ProductCategoryKey", "ProductCategory"
    ])
    producto_full = producto.merge(subcategoria, on="ProductSubcategoryKey", how="left")
    producto_full = producto_full.merge(categoria, on="ProductCategoryKey", how="left")

    fact_producto = seleccionar(fact, [
        "OrderID", "DateKey", "ProductKey", "SalesQuantity", "ReturnQuantity",
        "Cantidad_total", "Precio_unitario", "Ingresos"
    ]).merge(producto_full, on="ProductKey", how="left")

    tiendas = seleccionar(tablas["DimStores"], [
        "StoreKey", "GeographyKey", "StoreType", "StoreName", "EmployeeCount", "SellingAreaSize"
    ])
    geografia = seleccionar(tablas["DimGeography"], [
        "GeographyKey", "ContinentName", "RegionCountryName"
    ])
    tiendas_full = tiendas.merge(geografia, on="GeographyKey", how="left")
    fact_tienda_geo = seleccionar(fact, [
        "OrderID", "DateKey", "StoreKey", "SalesQuantity", "ReturnQuantity", "Cantidad_total", "Ingresos"
    ]).merge(tiendas_full, on="StoreKey", how="left")

    canal = seleccionar(tablas["DimChannel"], ["ChannelKey", "ChannelName"])
    fact_canal = seleccionar(fact, [
        "OrderID", "channelKey", "SalesQuantity", "ReturnQuantity", "Cantidad_total", "Ingresos"
    ]).merge(canal, left_on="channelKey", right_on="ChannelKey", how="left")

    promocion = seleccionar(tablas["DimPromotion"], [
        "PromotionKey", "PromotionName", "DiscountPercent", "Promo_days"
    ])
    fact_promocion = seleccionar(fact, [
        "OrderID", "PromotionKey", "SalesQuantity", "ReturnQuantity", "Cantidad_total", "Ingresos"
    ]).merge(promocion, on="PromotionKey", how="left")

    fact_tiempo = seleccionar(fact, [
        "OrderID", "DateKey", "SalesQuantity", "ReturnQuantity", "Cantidad_total", "Ingresos"
    ])
    fact_tiempo["Anio"] = fact_tiempo["DateKey"].dt.year
    fact_tiempo["Mes"] = fact_tiempo["DateKey"].dt.month

    return {
        "producto": fact_producto,
        "tienda_geo": fact_tienda_geo,
        "canal": fact_canal,
        "promocion": fact_promocion,
        "tiempo": fact_tiempo,
    }


# ============================================================
# MEJORA 3: CÁLCULO YoY ROBUSTO (TOLERANTE A AÑOS FALTANTES)
# ============================================================

def calcular_yoy_robusto(ventas_anio: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la variación año contra año (YoY) usando merge en lugar de shift().

    Con shift(), si hay un año sin datos en la serie el cálculo se desplaza
    incorrectamente. Con merge se garantiza que cada año se compare siempre
    contra su año anterior exacto, aunque haya huecos en la serie.
    """
    df = ventas_anio.copy().sort_values("Anio")

    # Creamos una copia del año anterior para hacer join explícito
    anio_anterior = df[["Anio", "Total_ingresos", "Cantidad_Total"]].copy()
    anio_anterior = anio_anterior.rename(columns={
        "Total_ingresos": "Total_ingresos_AA",
        "Cantidad_Total": "Cantidad_Total_AA",
        "Anio": "Anio_AA"
    })
    anio_anterior["Anio"] = anio_anterior["Anio_AA"] + 1  # el "año actual" que verá este registro

    df = df.merge(anio_anterior[["Anio", "Total_ingresos_AA", "Cantidad_Total_AA"]],
                  on="Anio", how="left")

    df["Ingresos_actuales_vs_AA"] = df["Total_ingresos"] - df["Total_ingresos_AA"]
    df["Variacion_porcentual_vs_AA"] = (
        df["Ingresos_actuales_vs_AA"] / df["Total_ingresos_AA"]
    )

    return df


def generar_metricas_negocio(fact: pd.DataFrame, tablas: dict[str, pd.DataFrame]) -> None:
    indicadores_generales(fact, tablas)
    base = tablas_enriquecidas(fact, tablas)

    exportar_csv(
        resumen_metricas(base["producto"], ["ProductCategory"]),
        "20_ventas_por_categoria_producto.csv",
        ordenar_por="Total_ingresos"
    )

    exportar_csv(
        resumen_metricas(base["producto"], ["ProductCategory", "ProductSubcategoryName"]),
        "21_ventas_por_subcategoria_producto.csv",
        ordenar_por="Total_ingresos"
    )

    productos = resumen_metricas(base["producto"], [
        "ProductKey", "ProductName", "ProductCategory", "ProductSubcategoryName",
        "Manufacturer", "BrandName"
    ])

    exportar_csv(productos, "22_productos_mas_vendidos.csv", ordenar_por="Cantidad_Total")
    exportar_csv(productos, "23_productos_con_mas_devoluciones.csv", ordenar_por="Cantidad_Devoluciones")

    exportar_csv(
        resumen_metricas(base["tienda_geo"], ["ContinentName", "RegionCountryName"]),
        "24_ventas_por_ubicacion_geografica.csv",
        ordenar_por="Total_ingresos"
    )

    exportar_csv(
        resumen_metricas(base["tienda_geo"], [
            "StoreKey", "StoreName", "StoreType", "ContinentName", "RegionCountryName"
        ]),
        "25_facturacion_por_store.csv",
        ordenar_por="Total_ingresos"
    )

    exportar_csv(
        resumen_metricas(base["canal"], ["ChannelName"]),
        "26_ventas_por_canal.csv",
        ordenar_por="Total_ingresos"
    )

    exportar_csv(
        resumen_metricas(base["promocion"], ["PromotionKey", "PromotionName", "DiscountPercent"]),
        "27_ventas_por_promocion.csv",
        ordenar_por="Total_ingresos"
    )

    # MEJORA 3: YoY robusto usando merge en lugar de shift()
    ventas_anio = resumen_metricas(base["tiempo"], ["Anio"]).sort_values("Anio")
    ventas_anio = calcular_yoy_robusto(ventas_anio)
    exportar_csv(ventas_anio, "28_ventas_por_anio.csv", ordenar_por="Anio", ascendente=True)

    ventas_mes = resumen_metricas(base["tiempo"], ["Anio", "Mes"]).sort_values(["Anio", "Mes"])
    ventas_mes["Acumulado_anio_ingresos"] = ventas_mes.groupby("Anio")["Total_ingresos"].cumsum()
    ventas_mes["Acumulado_anio_cantidad_total"] = ventas_mes.groupby("Anio")["Cantidad_Total"].cumsum()
    exportar_csv(ventas_mes, "29_ventas_por_mes_acumulado.csv", ordenar_por="Anio", ascendente=True)


# ============================================================
# 5. EJECUCIÓN PRINCIPAL
# ============================================================

def main() -> None:
    verificar_archivos()

    print("\n=== CARGA DE DATOS ===")
    tablas = cargar_excel_completo(ARCHIVO_EXCEL)
    fact_raw = cargar_fact_sales(ARCHIVO_VENTAS)
    muestra_fact = fact_raw.head(1000).copy()
    fact = preparar_fact_sales(fact_raw)

    print("\n=== ANÁLISIS PRELIMINAR ===")
    generar_resumen_tablas(tablas, fact, muestra_fact)
    generar_tipos_datos(tablas, fact, muestra_fact)
    generar_nulos_fact(fact)
    generar_rango_fechas(fact)
    generar_estadisticas_fact(fact)

    frecuencias_empiricas(fact, "Devolución", "06_frecuencia_devolucion.csv")
    frecuencias_empiricas(fact, "Venta_type", "07_frecuencia_tipo_venta.csv")
    frecuencias_empiricas(fact, "Devolución_type", "08_frecuencia_tipo_devolucion.csv")
    frecuencias_empiricas(fact, "SalesQuantity", "09_frecuencia_cantidad_vendida.csv")
    frecuencias_empiricas(fact, "ReturnQuantity", "10_frecuencia_cantidad_devuelta.csv")

    validar_ingresos(fact)
    generar_diccionario_tablas()           # MEJORA 2: ahora incluye DimCalendar
    generar_clasificacion_variables(tablas, fact)
    generar_estadisticas_generales(tablas, fact)
    generar_frecuencias_relevantes(tablas, fact)

    # MEJORA 1: detección de outliers
    print("\n=== DETECCIÓN DE OUTLIERS ===")
    detectar_outliers(fact)

    print("\n=== MODELO RELACIONAL ===")
    tablas["DimCalendar"] = crear_dim_calendar(fact)
    relaciones = definir_relaciones()
    validacion = validar_relaciones(tablas, fact, relaciones)

    print("\nResumen de relaciones:")
    print(validacion["Estado_validacion"].value_counts(dropna=False))

    print("\n=== MÉTRICAS DE NEGOCIO ===")
    generar_metricas_negocio(fact, tablas)   # MEJORA 3: YoY robusto aplicado aquí

    print("\nProceso terminado correctamente.")
    print(f"Archivos CSV disponibles en: {CARPETA_SALIDA}")


if __name__ == "__main__":
    main()

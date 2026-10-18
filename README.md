# Contoso Sales · Análisis de ventas con Python y Power BI

Proyecto académico de análisis exploratorio, estadística descriptiva y métricas comerciales sobre la empresa ficticia Contoso. El flujo transforma datos de ventas en tablas CSV y gráficas, utilizadas para estudiar productos, tiendas, canales, promociones y evolución temporal.

## Estado de la publicación

El script actualizado y el Excel de dimensiones están incluidos en el repositorio. El dashboard de dos páginas y los datos de ventas se descargan desde la [versión v1.0.0](https://github.com/dagonzlz/Proyecto_contoso/releases/tag/v1.0.0).

- [Descargar dashboard de Power BI](https://github.com/dagonzlz/Proyecto_contoso/releases/download/v1.0.0/Proyecto_Contoso_Dashboard.pbix).
- [Descargar FactSales.zip](https://github.com/dagonzlz/Proyecto_contoso/releases/download/v1.0.0/FactSales.zip). Extraer `FactSales.txt` dentro de `data/` antes de ejecutar el script.

El informe PDF no forma parte de esta publicación.

## Qué hace el proyecto

- Carga las dimensiones del Excel y la tabla de ventas separada por tabulaciones.
- Convierte fechas y valores numéricos con coma decimal.
- Calcula estadísticas descriptivas y probabilidades empíricas.
- Detecta valores atípicos mediante IQR y Z-score, sin asumir que sean errores.
- Compara ingresos registrados con precio unitario por cantidad neta.
- Define y valida ocho relaciones entre tablas.
- Genera un calendario, indicadores generales y resúmenes por producto, categoría, tienda, país, canal y promoción.
- Compara cada año con su año anterior exacto y genera gráficas PNG.

## Estructura

```text
Proyecto_contoso/
├── data/
│   ├── Contoso Sales.xlsx
│   ├── README.md
│   └── FactSales.txt             # extraer desde FactSales.zip (Releases)
├── proyecto_analisis_ventas.py
├── requirements.txt
├── outputs/                     # CSV generados al ejecutar
└── graficas/                    # PNG y resumen generados al ejecutar
```

## Instalación y ejecución

Se requiere Python 3.10 o superior.

```bash
git clone https://github.com/dagonzlz/Proyecto_contoso.git
cd Proyecto_contoso
python -m venv .venv
```

Activar el entorno en Windows:

```powershell
.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Instalar dependencias y ejecutar:

```bash
python -m pip install -r requirements.txt
python proyecto_analisis_ventas.py
```

Antes de ejecutar, descargar `FactSales.zip` desde Releases y extraer `FactSales.txt` en `data/`. El script utiliza rutas relativas a su propia ubicación. Cerrar los CSV abiertos en Excel para evitar bloqueos de escritura. El volumen del conjunto completo puede requerir memoria y tiempo de procesamiento considerables.

## Datos de entrada

El Excel contiene las dimensiones DimChannel, DimGeography, DimProduct, DimProductCategory, DimProductSubCategory, DimPromotion y DimStores.

La tabla de ventas debe incluir las columnas originales:
`OrderID`, `DateKey`, `channelKey`, `StoreKey`, `ProductKey`, `PromotionKey`, `SalesQuantity`, `ReturnQuantity`, `Cantidad_total`, `Devolución`, `Venta_type`, `Devolución_type`, `Precio_unitario` e `Ingresos`.

## Resultados

El script genera 30 CSV numerados: análisis preliminar (01–15), modelo relacional y calendario (16–18), métricas comerciales (19–29) y resumen de valores atípicos (30). También genera visualizaciones en `graficas/`.

Los resultados no se incluyen como si hubiesen sido recalculados: el flujo completo no se ha ejecutado durante esta publicación; los datos originales están disponibles en Releases.

## Dashboard de Power BI

La versión seleccionada para publicación contiene:
1. **Resumen (Dashboard)**.
2. **Análisis de Ventas**.

Para consultarla se requiere Power BI Desktop. La apertura, la apariencia visual y la actualización de fuentes deben comprobarse en esa aplicación. Al cambiar de computadora, puede ser necesario ajustar las rutas de origen. La publicación en GitHub no crea un dashboard web interactivo.

## Alcance y precauciones de interpretación

El análisis es descriptivo: asociaciones entre promociones e ingresos no prueban causalidad. El código usa el conteo de registros para algunas métricas llamadas “órdenes”; no equivale necesariamente al conteo de OrderID distintos. Las cantidades de unidades, las filas y las órdenes deben distinguirse al presentar resultados.

## Autoría

Trabajo académico colaborativo realizado por Angie Daniela González Alfaro, Kimberly Rivera Jiménez y Faustin Andrey Acuña Burgos, para el curso IE0405 Modelos Probabilísticos de Señales y Sistemas de la Universidad de Costa Rica (I ciclo de 2026).

Contoso es una empresa ficticia utilizada como caso de estudio. Este repositorio no atribuye a sus autores la propiedad del conjunto de datos original.

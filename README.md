# Contoso Sales · Análisis de ventas con Python y Power BI

Proyecto académico de análisis exploratorio, estadística descriptiva y métricas comerciales sobre la empresa ficticia Contoso. El flujo transforma datos de ventas en tablas CSV y gráficas, utilizadas para estudiar productos, tiendas, canales, promociones y evolución temporal.

## Estado de la publicación

El repositorio incluye la versión original del código y el Excel de dimensiones. La actualización del script adjunto, que incorpora las gráficas descritas más abajo, está pendiente de transferencia. **FactSales.txt no está incluido**: se necesita una copia del archivo original utilizado en el proyecto para ejecutar el análisis completo. No debe sustituirse por otro conjunto de Contoso sin revisar su esquema.

El dashboard de dos páginas está preparado, pero su transferencia a GitHub está pendiente. El informe académico PDF no se distribuye en este repositorio.

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
│   └── FactSales.txt             # aportar localmente; no incluido
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

Antes de ejecutar, colocar el archivo original `FactSales.txt` en `data/`. El script utiliza rutas relativas a su propia ubicación. Cerrar los CSV abiertos en Excel para evitar bloqueos de escritura. El volumen del conjunto completo puede requerir memoria y tiempo de procesamiento considerables.

## Datos de entrada

El Excel contiene las dimensiones DimChannel, DimGeography, DimProduct, DimProductCategory, DimProductSubCategory, DimPromotion y DimStores.

La tabla de ventas debe incluir las columnas originales:
`OrderID`, `DateKey`, `channelKey`, `StoreKey`, `ProductKey`, `PromotionKey`, `SalesQuantity`, `ReturnQuantity`, `Cantidad_total`, `Devolución`, `Venta_type`, `Devolución_type`, `Precio_unitario` e `Ingresos`.

## Resultados

La versión actualizada preparada para publicación genera 30 CSV numerados: análisis preliminar (01–15), modelo relacional y calendario (16–18), métricas comerciales (19–29) y resumen de valores atípicos (30). También genera visualizaciones en `graficas/`.

Los resultados no se incluyen como si hubiesen sido recalculados: esta publicación no ejecutó el flujo completo porque falta el archivo de ventas.

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

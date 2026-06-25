# Proyecto_contoso
Analizar el rendimiento de una empresa a partir de las herramientas probabilísticas estudiadas en el curso y brindando recomendaciones que podría tomar la empresa para mejorar o corregir aspectos del negocio
Proyecto 01: Principios de Análisis de Datos

Caso de estudio: Contoso Sales



================================================================================
1. Descripción general del proyecto
================================================================================



Este proyecto realiza un análisis exploratorio, estadístico y de negocio sobre
los datos de ventas de la empresa ficticia Contoso, siguiendo un proceso ETL
básico para transformar datos crudos en información útil para la toma de
decisiones.



El trabajo incluye:



  - Análisis preliminar de las tablas proporcionadas.
  - Limpieza y transformación de datos (fechas, formatos numéricos latinos).
  - Cálculo de estadísticas descriptivas por variable.
  - Cálculo de frecuencias y probabilidades empíricas.
  - Detección de valores atípicos mediante IQR y Z-score.
  - Validación de consistencia de ingresos.
  - Diseño y validación de un modelo relacional estrella.
  - Cálculo de métricas e indicadores de negocio.
  - Variación año contra año (YoY) robusta ante huecos en la serie temporal.
  - Construcción de un dashboard interactivo en Power BI.



================================================================================
2. Estructura de carpetas
================================================================================



La carpeta del proyecto debe mantenerse con esta estructura:



  proy_contoso/
  │
  ├── data/
  │   ├── Contoso Sales.xlsx
  │   └── FactSales.txt
  │
  ├── outputs/
  │   ├── 01_resumen_preliminar_tablas.csv
  │   ├── 02_tipos_datos_columnas.csv
  │   ├── ...
  │   └── 30_outliers_fact_sales.csv
  │
  ├── proyecto_analisis_ventas.py
  ├── Dashboard_Contoso.pbix
  ├── Reporte_Hallazgos.pdf
  └── README.txt



================================================================================
3. Archivos principales
================================================================================



  proyecto_analisis_ventas.py

      Script principal del proyecto. Lee los datos originales, limpia y
      transforma las columnas necesarias, calcula estadísticas, detecta
      outliers, valida relaciones del modelo y genera todos los archivos
      CSV de salida en la carpeta outputs/.



  Contoso Sales.xlsx

      Archivo Excel con las tablas dimensionales del modelo: productos,
      tiendas, categorías, subcategorías, promociones, canales y geografía.



  FactSales.txt

      Archivo de texto separado por tabulaciones con la tabla principal de
      ventas. Contiene más de 2.2 millones de registros y es el archivo
      más pesado del proyecto.



  outputs/

      Carpeta donde el script guarda los 30 archivos CSV generados.
      Sirven como evidencia del análisis y como fuente de datos para
      el dashboard de Power BI y el reporte.



  Dashboard_Contoso.pbix

      Dashboard interactivo en Power BI con visualizaciones, métricas y
      filtros para analizar el rendimiento del negocio.



  Reporte_Hallazgos.pdf

      Documento con el planteo del análisis, hallazgos encontrados y
      recomendaciones de negocio derivadas del estudio de los datos.



================================================================================
4. Requisitos para ejecutar el script
================================================================================



Se requiere Python 3.10 o superior y las siguientes librerías:



  - pandas
  - numpy
  - openpyxl



Para instalarlas desde la terminal:



  py -m pip install pandas numpy openpyxl



Nota: el script usa la sintaxis de union de tipos (str | None) introducida
en Python 3.10, por lo que no es compatible con versiones anteriores.



================================================================================
5. Cómo ejecutar el script
================================================================================



  1. Descargar o sincronizar toda la carpeta proy_contoso.
  2. No modificar la estructura de carpetas.
  3. Verificar que Contoso Sales.xlsx y FactSales.txt estén dentro de data/.
  4. Abrir la carpeta principal en Visual Studio Code o cualquier terminal.
  5. Ejecutar:

       py proyecto_analisis_ventas.py

  El script leerá los archivos desde data/ y generará o actualizará los
  archivos CSV dentro de outputs/.



================================================================================
6. Sobre las rutas del proyecto
================================================================================



El script construye todas las rutas de forma relativa usando la ubicación
del propio archivo .py como punto de referencia. Esto significa que no
depende de un usuario de Windows ni de una ruta fija como:



  C:\Users\usuario\...



El proyecto debería funcionar en cualquier computadora siempre que se
mantenga la estructura de carpetas descrita en la sección 2.



================================================================================
7. Sobre el dashboard de Power BI
================================================================================



El archivo Dashboard_Contoso.pbix puede abrirse directamente en
Power BI Desktop sin necesidad de configuración adicional para visualizarlo.



Si se intenta actualizar los datos desde otra computadora, Power BI puede
solicitar que se actualicen las rutas de origen apuntando a la carpeta
outputs/ del proyecto en la nueva máquina.



================================================================================
8. Archivos generados por el script
================================================================================



El script genera 30 archivos CSV numerados, organizados en cuatro grupos:



  01 al 15 — Análisis preliminar
      Resumen de tablas, tipos de datos, valores nulos, rango de fechas,
      estadísticas descriptivas, frecuencias empíricas y validación de
      ingresos. También incluye el diccionario de tablas y la clasificación
      de variables.

  16 al 18 — Modelo relacional
      Definición y validación de las 8 relaciones del modelo estrella,
      más la tabla calendario generada automáticamente desde FactSales.

  19 al 29 — Métricas de negocio
      Indicadores generales, ventas por categoría y subcategoría de
      producto, productos más vendidos, productos con más devoluciones,
      facturación por tienda, ventas por canal, por promoción y análisis
      temporal anual y mensual con acumulados y variación YoY.

  30 — Detección de outliers
      Análisis de valores atípicos en las variables numéricas clave de
      FactSales usando los métodos IQR y Z-score.



================================================================================
9. Recomendaciones
================================================================================



  - Antes de ejecutar el script de nuevo, cerrar cualquier archivo CSV que
    esté abierto en Excel. Windows puede bloquearlo e impedir que Python
    lo sobreescriba, lo que generará un error de permisos.

  - Guardar una copia del dashboard de Power BI antes de hacer cambios
    importantes, ya que el formato .pbix no tiene historial de versiones
    automático.

  - Si se agregan nuevos datos a FactSales.txt, volver a ejecutar el script
    completo para que todos los CSVs y métricas queden actualizados.

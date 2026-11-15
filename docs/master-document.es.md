# **QHANTAR**

## **Documento maestro de fundamentos, funcionamiento y diferenciación científica**

**NASA Space Apps 2026 · Dancing with the SARs**

**Tesis central:** QHANTAR ayuda a determinar dónde una observación radar NISAR permite interpretar el posible movimiento cuesta abajo de una ladera y dónde esa interpretación no está suficientemente respaldada por la geometría o la calidad de la medición.

**Posicionamiento:** Observabilidad de laderas con NISAR.

**Frase de identidad:** «No basta con ver una señal. Hay que saber si el radar podía observar aquello que queremos interpretar».

---

# **1\. RESUMEN EJECUTIVO: ¿QUÉ ES QHANTAR?**

QHANTAR es una herramienta web de análisis geoespacial que procesa un producto real GUNW de la misión NISAR y cruza tres dimensiones de información:

1. **Geometría del terreno:** pendiente y orientación de cada ladera, derivadas de un modelo digital de elevación (DEM).  
2. **Geometría de observación:** dirección desde la que el radar observa el terreno, representada por los vectores de línea de visión (LOS) nativos del producto.  
3. **Calidad de la observación:** coherencia interferométrica, componentes conectados y máscaras de validez de la pareja de imágenes.

Con esos datos, QHANTAR genera un mapa que clasifica el terreno en cuatro estados:

* Interpretable.  
* Visible, pero incoherente.  
* Coherente, pero poco sensible.  
* No observable o inválido.

El objetivo es que el usuario no tenga que mirar únicamente un interferograma y decidir por intuición dónde confiar en él.

QHANTAR proporciona una capa de análisis que explica **qué condiciones permiten interpretar una observación y cuáles impiden hacerlo**.

No es un detector automático de deslizamientos. No es un predictor de desastres. No es un sistema que mida por sí solo el desplazamiento real de una ladera.

Su función es evaluar la observabilidad y la interpretabilidad de la evidencia radar.

# **2\. EL PROBLEMA CIENTÍFICO: ¿POR QUÉ EXISTE QHANTAR?**

## **2.1 El radar no observa el terreno desde todas las direcciones**

Un radar de apertura sintética (SAR) instalado en un satélite emite señales hacia la superficie y registra la energía que regresa.

La geometría de observación importa porque el satélite no mide directamente todos los componentes del movimiento del terreno.

En interferometría SAR (InSAR), una medición LOS representa la componente del desplazamiento proyectada sobre la dirección de observación del radar.

Esto genera un problema particular en las montañas.

Imaginemos dos laderas:

* La primera tiene una dirección de movimiento cuesta abajo aproximadamente alineada con la dirección desde la que observa el satélite.  
* La segunda tiene una dirección de movimiento casi perpendicular a esa observación.

Ambas podrían moverse físicamente. Sin embargo, la proyección del movimiento sobre la línea de visión sería diferente.

La primera podría producir una señal más sensible al movimiento hipotético cuesta abajo. La segunda podría presentar una señal pequeña, aunque exista movimiento real.

Por tanto:

**Que el radar no muestre una señal significativa no demuestra que el terreno esté estable. Puede significar que la geometría de observación no es sensible a ese movimiento.**

Esta es una de las razones fundamentales por las que existe QHANTAR.

## **2.2 No todo lo que aparece en un interferograma es interpretable**

Una segunda dificultad es la calidad de la observación.

La coherencia interferométrica permite evaluar cuánto se parecen las señales complejas de dos adquisiciones, dentro de las condiciones del procesamiento.

Una coherencia baja puede dificultar la interpretación de la fase.

Además, existen problemas geométricos y de procesamiento:

* Layover: superposición de retornos de distintas partes del terreno.  
* Foreshortening: compresión de superficies en la dirección de rango.  
* Shadow: zonas que no reciben una iluminación radar adecuada.  
* Decorrelation: pérdida de coherencia entre adquisiciones.  
* Errores de desenrollado de fase.  
* Efectos atmosféricos e ionosféricos.  
* Diferencias entre el DEM utilizado para el análisis y el utilizado en la geocodificación.

Un usuario puede observar una imagen con colores y patrones y creer que está viendo deformación real.

Pero una imagen visualmente interesante no equivale a una medición físicamente interpretable.

QHANTAR nace para introducir una evaluación explícita antes de interpretar la evidencia.

## **2.3 El problema que queremos evitar**

Existen dos errores de interpretación que queremos ayudar a prevenir:

**Error A: falso convencimiento de movimiento.**

El usuario observa una anomalía de fase y la interpreta como movimiento de ladera, sin comprobar la calidad de la medición ni las posibles fuentes de error.

**Error B: falso convencimiento de estabilidad.**

El usuario no observa una señal significativa y concluye que no existe movimiento, aunque la dirección del movimiento hipotético sea poco observable desde la geometría del satélite.

QHANTAR no elimina todas las fuentes de incertidumbre. Ayuda a identificar condiciones que deben evaluarse antes de formular conclusiones.

# **3\. ¿QUÉ HACE QHANTAR EXACTAMENTE?**

El proceso tiene ocho etapas.

## **Etapa 1\. Recibir un producto NISAR GUNW**

El insumo principal es un archivo de nivel 2:

`NISAR_L2_..._GUNW_...h5`

GUNW significa *Geocoded Unwrapped Interferogram*.

Es un producto que contiene un interferograma desenrollado y capas auxiliares geocodificadas.

Según la documentación de ASF, incluye, entre otros elementos:

* Fase interferométrica desenrollada.  
* Magnitud de coherencia.  
* Componentes conectados.  
* Interferograma complejo envuelto.  
* Capas de estimación ionosférica y su incertidumbre.  
* Capas de corrección externa, cuando están disponibles.

La fase desenrollada se distribuye a 80 m de resolución de publicación; la coherencia dispone de capas a 20 y 80 m. Los GUNW descritos en la documentación corresponden a pares vecinos de aproximadamente 12 días, en HH o VV y frecuencia A.

Fuente: ASF, NISAR Data User Guide, GUNW.

https\://nisar-docs.asf.alaska.edu/gunw/

## **Etapa 2\. Inspeccionar el producto y su procedencia**

QHANTAR no debe asumir que todos los archivos tienen las mismas dimensiones, atributos o condiciones.

Primero inspecciona el HDF5 para identificar:

* Datasets disponibles.  
* Dimensiones.  
* Resolución.  
* Sistema de coordenadas.  
* Transformación geográfica.  
* Valores nodata.  
* Metadatos de adquisición.  
* Madurez del producto.  
* CRID.  
* Capas geométricas.

La aplicación debe mostrar el identificador exacto del producto, fechas, colección y madurez.

No debemos mezclar sin control productos BETA, PROVISIONAL y VALIDATED.

La documentación de ASF explica que ciertos problemas de los productos provisionales P05023, incluidos problemas de marcas de tiempo que afectaban imágenes y productos interferométricos, fueron corregidos en el procesamiento P05036. La madurez y el CRID importan para interpretar la calidad del dato.

Fuente:

https\://hyp3-docs.asf.alaska.edu/nisar-docs/nisar-known-issues/

## **Etapa 3\. Extraer la evidencia radar**

Del producto se extraen las capas necesarias:

**Fase interferométrica**

Representa la fase desenrollada del interferograma, en radianes.

Es una observación que requiere interpretación científica. No debe etiquetarse automáticamente como desplazamiento confirmado.

**Coherencia**

Es un indicador de calidad de la relación entre las adquisiciones interferométricas.

No es desplazamiento, velocidad ni probabilidad de movimiento.

**Componentes conectados**

Permiten identificar regiones pertenecientes a componentes del proceso de desenrollado.

Los píxeles con componente inválida o igual a cero, según la convención del producto, no deben tratarse como mediciones válidas.

**Máscaras y capas auxiliares**

Se utilizan cuando están presentes y sus convenciones han sido verificadas.

QHANTAR conserva estas capas como evidencia separada, sin mezclarlas en un indicador arbitrario.

## **Etapa 4\. Obtener la geometría nativa de NISAR**

Esta es una decisión técnica importante.

No queremos depender únicamente de un ángulo de incidencia genérico o de una aproximación simplificada del rumbo orbital.

La documentación de metadatos de NISAR describe variables como:

* `incidenceAngle`  
* `losUnitVectorX`  
* `losUnitVectorY`  
* `elevationAngle`

El glosario de ASF define `losUnitVectorX` y `losUnitVectorY` como las componentes Este y Norte del vector unitario LOS, orientado desde el objetivo terrestre hacia el sensor, en el sistema Este-Norte-Arriba.

La componente vertical puede derivarse mediante:

\[ u\_{LOS,z}=\\sqrt{1-u\_{LOS,x}^{2}-u\_{LOS,y}^{2}} \]

Por tanto:

\[ \\vec{u}*{LOS}= (u*{LOS,x},u\_{LOS,y},u\_{LOS,z}) \]

Estos vectores son información nativa de la geometría del producto, no una dirección inventada por QHANTAR.

Hay un detalle de implementación: las capas geométricas pueden estar almacenadas como cubos en función de la altura. Deben interpolarse a la altura correspondiente del DEM antes de calcular la relación geométrica.

Fuentes:

https\://nisar-docs.asf.alaska.edu/metadata/

https\://nisar-docs.asf.alaska.edu/glossary/

## **Etapa 5\. Calcular la geometría de las laderas**

Se utiliza un modelo digital de elevación (DEM), por ejemplo Copernicus GLO-30 o NASADEM, sujeto a disponibilidad, licencia y compatibilidad.

A partir del DEM se calcula:

* Pendiente (\\beta).  
* Orientación de la dirección cuesta abajo (\\alpha).  
* Elevación.  
* Validez del terreno.

La pendiente describe cuánto se inclina el terreno.

La orientación describe hacia dónde apunta la dirección cuesta abajo.

Se expresa el vector unitario de movimiento hipotético cuesta abajo en coordenadas Este-Norte-Arriba:

\[ \\vec{u}\_{slope}= (\\sin\\alpha\\cos\\beta,, \\cos\\alpha\\cos\\beta,, \-\\sin\\beta) \]

La convención de orientación debe estar documentada y probada para evitar errores de rumbo.

Una superficie casi plana no tiene una dirección cuesta abajo suficientemente definida para este cálculo y debe tratarse como una condición no válida o no aplicable.

## **Etapa 6\. Calcular la sensibilidad geométrica**

El motor calcula:

\[ S=\\vec{u}*{slope}\\cdot\\vec{u}*{LOS} \]

Y también:

\[ \|S\|=\\left\|\\vec{u}*{slope}\\cdot\\vec{u}*{LOS}\\right\| \]

Donde:

* (S) es la proyección firmada.  
* (\|S\|) es la magnitud de la sensibilidad geométrica.

Interpretación:

* Un valor absoluto cercano a 1 significa que la dirección hipotética de movimiento cuesta abajo está muy alineada con la LOS.  
* Un valor absoluto cercano a 0 significa que esa dirección de movimiento tiene una proyección pequeña sobre la LOS.

El signo indica la orientación de la proyección bajo la convención adoptada. En nuestro sistema, un signo positivo corresponde a una proyección hacia el sensor.

**Importante:** S no es una medición de movimiento. Es una propiedad geométrica del movimiento hipotético y de la observación.

No indica que la montaña se esté moviendo.

Tampoco es una probabilidad de deslizamiento ni un índice de peligro.

## **Etapa 7\. Evaluar distorsión y calidad**

El motor evalúa las condiciones geométricas que pueden impedir la observación.

En particular, utiliza la relación entre:

* Pendiente.  
* Orientación de la ladera.  
* Dirección de rango.  
* Ángulo de incidencia.

Con ello identifica condiciones de layover y shadow según el modelo implementado.

También considera:

* Validez de la geometría.  
* Datos faltantes.  
* Pendientes no aplicables.  
* Coherencia.  
* Componentes conectados.

Las condiciones de calidad no se sustituyen por una única puntuación.

## **Etapa 8\. Generar el mapa de cuatro estados**

La salida principal es un mapa de interpretabilidad.

| Estado | Condiciones | Qué significa |
| ----- | ----- | ----- |
| 1\. Interpretable | Geometría válida, sensibilidad suficiente, coherencia suficiente y componentes válidos | La fase puede analizarse respecto al movimiento hipotético cuesta abajo, con las limitaciones declaradas |
| 2\. Visible, incoherente | Sensibilidad suficiente, coherencia insuficiente | La geometría permite sensibilidad, pero la medición no tiene calidad suficiente |
| 3\. Coherente, poco sensible | Coherencia suficiente, sensibilidad baja | La medición tiene coherencia, pero es poco sensible al movimiento hipotético cuesta abajo |
| 0\. No observable / inválido | Layover, shadow, datos inválidos, componente inválido, geometría ausente o pendiente no aplicable | No se debe interpretar la fase como evidencia válida de ese movimiento |

Los valores iniciales de referencia son:

* Sensibilidad: (\|S\| \\geq 0.3).  
* Coherencia: (\\gamma \\geq 0.5).

Estos umbrales son decisiones iniciales ajustables, no constantes universales ni resultados científicos demostrados.

La coherencia y la sensibilidad se muestran por separado.

No se multiplican para inventar un índice compuesto.

# **4\. ¿CUÁL ES NUESTRA DIFERENCIACIÓN REAL?**

Esta es la sección más importante del documento.

No debemos decir que inventamos la sensibilidad LOS, la relación pendiente-radar o la evaluación geométrica de laderas.

Eso sería falso.

## **4.1 Lo que ya existía antes de QHANTAR**

**A. Índice R y mapas de visibilidad**

Notti y colaboradores publicaron en 2010 un trabajo sobre datos radar satelitales y cartografía de deslizamientos.

Su análisis considera:

* Geometría radar.  
* Ángulo de incidencia.  
* Pendiente.  
* Orientación del terreno.  
* Distorsiones geométricas como layover, foreshortening y shadow.

El índice R evalúa la relación entre la geometría del terreno y la geometría de adquisición.

Por tanto, la relación entre pendiente, orientación y visibilidad radar no es nueva.

Referencia:

Notti et al. (2010), *X-band satellite radar data for landslide mapping and monitoring*.

https\://nhess.copernicus.org/articles/10/1865/2010/

**B. World-wide InSAR sensitivity index**

Van Natijne, Bogaard, van Leijen, Hanssen y Lindenbergh publicaron en 2022 el trabajo:

*World-wide InSAR sensitivity index for landslide deformation tracking.*

Este trabajo es especialmente importante para nuestra diferenciación.

Propone una evaluación mundial del potencial de InSAR para detectar deformación cuesta abajo.

Combina:

* Sensibilidad geométrica del radar al movimiento cuesta abajo.  
* Presencia potencial de superficies coherentes.  
* Geometría de observación.  
* Evaluación previa de la capacidad de monitoreo.

Además, proporciona una herramienta abierta de Google Earth Engine.

Su objetivo es principalmente evaluar el potencial de observación a priori, antes de disponer necesariamente de una pareja interferométrica concreta.

Referencia:

https\://doi.org/10.1016/j.jag.2022.102829

**Conclusión:** no podemos presentar la combinación de sensibilidad geométrica y coherencia como un descubrimiento de QHANTAR. Ya existe trabajo científico que aborda esa combinación.

## **4.2 Entonces, ¿qué proponemos hacer diferente?**

La diferencia propuesta es el momento, la fuente y el nivel de evidencia con que hacemos la evaluación.

| Dimensión | Evaluación previa genérica | QHANTAR propuesto |
| ----- | ----- | ----- |
| Pregunta | ¿Sería favorable esta geometría para observar movimiento cuesta abajo? | ¿Es interpretable esta ladera en esta pareja NISAR concreta? |
| Momento | A priori | A posteriori, sobre el producto procesado |
| Sensor | Ejemplos y herramientas previas como Sentinel-1 | NISAR L-band |
| Geometría | Geometría orbital o aproximaciones según herramienta | Vectores LOS nativos del GUNW |
| Calidad | Potencial de dispersores coherentes o estimaciones previas | Coherencia realmente medida en la pareja |
| Validez | Evaluación potencial de observabilidad | Coherencia y componentes conectados de la observación concreta |
| Resultado | Potencial de monitoreo | Clasificación de cuatro estados para esa observación |
| Reproducibilidad | Depende de la herramienta y sus datos | Pipeline, pruebas, convenciones y procedencia publicados por QHANTAR |

La diferencia fundamental que perseguimos es:

**Pasar de preguntar si una ladera podría observarse en general a evaluar si una observación NISAR concreta proporciona condiciones suficientes para interpretar el movimiento hipotético cuesta abajo.**

Esto no significa que seamos los primeros en hacerlo en todo el mundo.

Significa que, dentro de nuestra revisión documentada, no encontramos una implementación pública que reuniera exactamente esos elementos de la forma propuesta.

Es una hipótesis de diferenciación, no una afirmación de novedad universal.

## **4.3 Diferenciación frente a los proyectos de la competición**

La revisión de competidores documentada por el equipo encontró:

| Proyecto | Capacidades documentadas | Oportunidad de QHANTAR |
| ----- | ----- | ----- |
| LunaHorizon | GUNW real, fase, coherencia, máscaras, componentes conectados, inspección de píxel, umbrales, exportaciones y pruebas automatizadas declaradas | Añadir un análisis de interpretabilidad por ladera usando geometría LOS nativa y calidad medida de la pareja |
| Earth Whisper | Evidencia de cambio de coherencia, contexto de terreno, NASADEM, pendiente local, incertidumbre y expedientes de investigación | Integrar la sensibilidad geométrica LOS de la pareja con las condiciones reales de calidad y componentes |
| dancing-with-sars-eq | Búsqueda de pares NISAR y casos de procesamiento GUNW | Diferenciarse mediante el análisis de observabilidad de laderas |
| TerraCascade | Plataforma orientada a pronóstico de cambios | Mantener una afirmación más acotada, verificable y científicamente defendible |
| SAR Atlas / disasterWatch | Referencias identificadas en la investigación inicial, sin auditoría profunda completa en el documento fundacional | No atribuirles ni negarles capacidades sin revisar sus implementaciones |

La comparación detallada de LunaHorizon y Earth Whisper es más sólida que la de los proyectos que solo se revisaron superficialmente.

Por tanto, no afirmamos que todos los competidores carezcan de análisis LOS.

Tampoco afirmamos que QHANTAR sea el único producto del mundo que combina terreno, geometría y calidad.

La diferencia debe demostrarse en código, resultados y documentación.

# **5\. ¿QUÉ APORTA QHANTAR A LA COMUNIDAD NISAR?**

Nuestra contribución propuesta tiene cinco elementos:

1. **Un módulo abierto de interpretabilidad:** transforma un GUNW en una clasificación de cuatro estados que ayuda a identificar dónde la evidencia es interpretable y dónde no.

2. **Uso de geometría nativa:** utiliza los vectores LOS del producto, en lugar de depender exclusivamente de una geometría genérica.

3. **Calidad medida de la pareja:** incorpora coherencia y componentes conectados de la observación concreta.

4. **Método reproducible:** publica fórmulas, convenciones, umbrales, pruebas y comandos de procesamiento.

5. **Caso andino documentado:** busca demostrar la utilidad del método en un contexto montañoso relevante para Bolivia y la región andina, si encontramos una escena adecuada.

No afirmamos que NASA necesite QHANTAR ni que hayamos demostrado todavía su utilidad operativa para una institución.

Afirmamos que puede ser un paso previo útil para evitar interpretaciones precipitadas de productos radar en terrenos montañosos.

# **6\. ¿QUÉ NO HACE QHANTAR?**

Esta sección debe aparecer tanto en el código como en el discurso.

QHANTAR NO:

* Predice deslizamientos.  
* Detecta automáticamente todos los movimientos de ladera.  
* Calcula un índice de riesgo.  
* Determina si una montaña es estable.  
* Mide desplazamiento real únicamente a partir de S.  
* Convierte coherencia en desplazamiento.  
* Interpreta automáticamente fase cruda como un evento confirmado.  
* Determina por sí solo las causas de una anomalía.  
* Recupera tres componentes de movimiento a partir de una única geometría LOS.  
* Garantiza que una zona clasificada como interpretable tenga movimiento detectable.

Una sola observación LOS mide una proyección del movimiento tridimensional. No permite separar por sí sola los componentes Este, Norte y vertical.

Para una reconstrucción tridimensional hacen falta observaciones independientes adicionales y una geometría suficientemente adecuada, o supuestos físicos complementarios.

Tampoco prometemos detectar movimientos lentos con una sola pareja de 12 días.

El documento fundacional estima que un movimiento de 5 cm/año equivale a aproximadamente 1.6 mm en 12 días. Esa señal puede quedar por debajo del ruido y de otras incertidumbres de un interferograma individual.

QHANTAR no debe presentarse como un detector de deslizamientos lentos basado en un único par.

# **7\. ¿CÓMO DEMOSTRAMOS QUE FUNCIONA?**

La credibilidad del proyecto depende de separar pruebas matemáticas, pruebas del formato y validación empírica.

## **7.1 Pruebas matemáticas**

Estado documentado: 9 de 9 pruebas sintéticas aprobadas.

Incluyen:

* Movimiento paralelo a LOS.  
* Movimiento perpendicular a LOS.  
* Pendiente plana.  
* Orientaciones de cinco rumbos.  
* Layover.  
* Shadow.  
* Clasificación de cuatro estados.  
* Equivalencia entre LOS nativa y una formulación por ángulos en los casos de prueba.

Esto demuestra que el motor se comporta correctamente en los casos analíticos diseñados.

No demuestra todavía que funcione perfectamente en una escena real.

## **7.2 Prueba de formato NISAR**

La documentación de ASF confirma que GUNW contiene metadatos geométricos como vectores LOS.

El código del proyecto ya contempla su lectura e interpolación en el formato documentado.

Sin embargo, todavía debe verificarse el funcionamiento completo sobre un archivo real.

## **7.3 Hipótesis empírica H1**

Queremos comprobar si las zonas que el modelo identifica como layover o shadow presentan:

* Menor coherencia mediana.  
* Mayor proporción de componentes conectados iguales a cero.

En comparación con zonas geométricamente válidas.

La hipótesis está pendiente de ejecución con una escena real.

Si no se confirma, lo reportaremos.

No modificaremos los resultados para hacer que la hipótesis parezca correcta.

## **7.4 Contraste H2**

Comparar nuestra clasificación con una implementación independiente del índice R o un modelo de visibilidad equivalente.

Objetivo: identificar coincidencias, diferencias y posibles errores.

## **7.5 Sensibilidad H3**

Comparar la geometría LOS nativa del GUNW con una aproximación basada en rumbo e incidencia.

Objetivo: cuantificar cuánto cambia el resultado al usar geometría nativa.

## **7.6 Contexto local H4**

Como análisis adicional, investigar si zonas activas conocidas de La Paz coinciden con áreas clasificadas como interpretables o no observables.

Esto requiere inventarios o polígonos geográficos fiables.

No debe presentarse como validación si no tenemos esos datos.

**Regla de evaluación:** publicar resultados positivos y negativos.

# **8\. FUNDAMENTOS TÉCNICOS Y ARQUITECTURA**

El pipeline previsto es:

**ENTRADAS**

* GUNW HDF5 de NISAR.  
* DEM público.  
* Metadatos geométricos.  
* Información de procedencia.

**PROCESAMIENTO CIENTÍFICO**

Python:

* NumPy.  
* h5py.  
* Rasterio.  
* pyproj.

Etapas:

1. Inspección del archivo.  
2. Extracción de fase, coherencia, componentes y máscaras.  
3. Extracción de geometría LOS.  
4. Interpolación de geometría a la altura del DEM.  
5. Cálculo de pendiente y orientación.  
6. Cálculo de sensibilidad.  
7. Evaluación de layover y shadow.  
8. Clasificación de cuatro estados.  
9. Exportación de resultados.

**SALIDAS**

* PNG georreferenciados.  
* JSON de resultados.  
* Metadatos.  
* Parámetros.  
* Resumen de calidad.  
* Evidencia reproducible.

**APLICACIÓN WEB**

React \+ TypeScript \+ Vite \+ MapLibre GL JS.

La aplicación presenta los resultados mediante cinco vistas:

1. Resumen de misión.  
2. Observatorio de montaña.  
3. Evidencia radar.  
4. Observabilidad pendiente–LOS.  
5. Pasaporte de evidencia.

No necesitamos una arquitectura compleja.

El producto puede funcionar con archivos científicos procesados previamente, servidos como recursos estáticos.

El archivo HDF5 original, de varios gigabytes, no debe subirse innecesariamente al repositorio público.

# **9\. LOS PRINCIPIOS QUE DEFINEN A QHANTAR**

Estos son nuestros fundamentos institucionales y científicos:

**1\. Honestidad antes que espectáculo.**

No presentamos datos ilustrativos como reales. No ocultamos resultados negativos.

**2\. Procedencia visible.**

Cada resultado debe indicar producto, fechas, madurez, CRID, fuente y método.

**3\. Separación de evidencia.**

Fase, coherencia, geometría y calidad se presentan como dimensiones diferentes.

**4\. Reproducibilidad.**

Una persona debe poder clonar el repositorio y regenerar el análisis con instrucciones claras.

**5\. Apertura.**

El código, las convenciones y el método deben ser públicos, con una licencia permisiva.

**6\. Utilidad científica.**

El diseño existe para ayudar a interpretar correctamente los datos, no solo para impresionar al jurado.

**7\. Responsabilidad en el uso de IA.**

Declaramos el uso de ChatGPT, Claude y Antigravity, especificando qué tareas realizaron y qué verificó el equipo humano.

# **10\. QUÉ NOS HARÍA DIFÍCILES DE REEMPLAZAR**

No es el código por sí solo. Alguien puede copiar una implementación.

Nuestra fortaleza debe construirse con:

* Pruebas analíticas completas.  
* Convenciones geométricas explícitas.  
* Resultados sobre una escena real NISAR.  
* Comparación independiente con métodos anteriores.  
* Uso de vectores LOS nativos.  
* Análisis de calidad medido en la pareja.  
* Documentación abierta.  
* Un caso andino reproducible.  
* Una reputación basada en no exagerar lo que los datos permiten concluir.

No tenemos todavía una ventaja competitiva demostrada en todos esos elementos.

Son los activos que debemos construir.

# **11\. ESTADO REAL DEL PROYECTO**

| Elemento | Estado documentado |
| ----- | ----- |
| Fundamento matemático | Implementado |
| Pruebas sintéticas | 9/9 aprobadas |
| Lectura de geometría GUNW | Implementada para el formato documentado |
| Escena NISAR real procesada | Pendiente |
| Mapa real de cuatro estados | Pendiente |
| Validación empírica H1 | Pendiente |
| Contraste H2 | Pendiente |
| Comparación H3 | Pendiente |
| Pasaporte exportable | Objetivo de implementación |
| Validación con usuarios reales | No realizada |

Esta tabla debe actualizarse cada vez que se complete un hito.

No debemos cambiar un estado a «completado» porque una pantalla se vea terminada.

# **12\. LA EXPLICACIÓN QUE DEBE RECORDAR EL JURADO**

## **Versión corta**

QHANTAR es una herramienta que evalúa dónde una observación NISAR es interpretable en terrenos montañosos. Cruza la geometría de cada ladera con la línea de visión del radar y con la calidad medida de la pareja interferométrica para identificar dónde existe sensibilidad suficiente y dónde no se debe confiar en la interpretación.

## **Versión de diferenciación**

La relación entre pendiente y geometría radar ya existe en la literatura científica. Nuestra contribución no es inventarla. Proponemos aplicarla sobre una pareja GUNW concreta de NISAR, usando sus vectores LOS nativos y su coherencia y componentes conectados medidos, para generar una clasificación reproducible de cuatro estados. Así pasamos de una estimación general del potencial de observación a un análisis de interpretabilidad condicionado por la evidencia de una adquisición específica.

## **Versión de impacto**

En zonas montañosas, una señal ausente no siempre significa que no haya movimiento: puede significar que el radar no era sensible a él. QHANTAR busca ayudar a investigadores y analistas a reconocer esa limitación antes de sacar conclusiones.

# **13\. PREGUNTAS DIFÍCILES QUE DEBEMOS SABER RESPONDER**

**¿Esto ya existe?**

Sí existen métodos anteriores para estudiar la visibilidad radar, la sensibilidad al movimiento cuesta abajo y la relación entre pendiente y LOS. Nuestro aporte propuesto es la aplicación posterior sobre una pareja GUNW de NISAR, utilizando geometría nativa y calidad medida, con una clasificación reproducible. No afirmamos ser los primeros en el mundo.

**¿Detecta deslizamientos?**

No. Evalúa las condiciones de observabilidad e interpretabilidad de una observación radar respecto a un movimiento hipotético cuesta abajo.

**¿Por qué no basta con mostrar coherencia?**

Porque la coherencia evalúa la calidad de la relación interferométrica, pero no indica por sí sola si la geometría LOS es sensible al movimiento que queremos estudiar.

**¿Por qué no basta con calcular pendiente y orientación?**

Porque una estimación geométrica previa no incorpora necesariamente la calidad y validez reales de la pareja interferométrica que se está analizando.

**¿Por qué utilizar los vectores LOS nativos?**

Porque representan la geometría de observación proporcionada por el producto y permiten evaluar la proyección en cada ubicación con mayor fidelidad que una aproximación uniforme de rumbo e incidencia.

**¿Por qué cuatro estados?**

Porque geometría y calidad son dimensiones diferentes. Una ladera puede ser geométricamente sensible y tener mala coherencia; o tener buena coherencia y poca sensibilidad. Mezclarlas en una sola puntuación escondería esa diferencia.

**¿Cómo sabemos que funciona?**

Tenemos nueve pruebas sintéticas aprobadas. La validación sobre una escena real y las hipótesis empíricas todavía deben ejecutarse y reportarse.

**¿Puede determinar movimiento tridimensional?**

No. Una única geometría LOS no permite recuperar por sí sola los tres componentes del desplazamiento.

**¿Qué pasa si los datos contradicen nuestra hipótesis?**

Se publica el resultado negativo y se revisa el alcance de la conclusión.

---

# **14\. DECLARACIÓN FINAL DE IDENTIDAD**

QHANTAR existe porque interpretar una observación radar sin evaluar su geometría y su calidad puede conducir a conclusiones equivocadas.

Nuestra misión no es afirmar que el radar lo ve todo.

Nuestra misión es identificar qué puede observar, qué no puede observar y por qué.

**QHANTAR: saber dónde confiar en el radar y dónde no.**


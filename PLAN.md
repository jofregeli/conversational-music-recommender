# PLAN — Recomendador musical conversacional

Herramienta 1 del porfolio de IA de Jofre. Las decisiones y sus motivos están en `DECISIONS.md`.

## Objetivo

Un servicio en Python que recibe una petición en lenguaje natural (y, si se quiere, canciones de referencia o un clip de audio) y devuelve canciones reales de un catálogo Creative Commons. Un agente con personalidad explica por qué las ha elegido.

El objetivo principal es **aprender**: Jofre tiene que poder explicar cada pieza y cada decisión, aunque no las programe todas.

Ritmo: 5-10 h/semana, sin fecha límite. Las duraciones son orientativas (unas 19 semanas en total).

## Alcance mínimo (v1)

**Dentro**
- Catálogo: subconjunto mood/theme de MTG-Jamendo (unas 18.500 pistas) más las 706 pistas del Song Describer Dataset (SDD).
- Embeddings texto-audio: MuQ-MuLan y CLaMP 3, comparados en SDD.
- Primer entrenamiento: clasificador de las 56 etiquetas de mood/theme sobre los embeddings, comparado con los resultados de referencia de MTG-Jamendo.
- Búsqueda exacta con numpy, filtros por etiquetas (también las predichas), BM25, fusión RRF y MMR.
- Referencias: texto libre, canciones del catálogo, clip de audio subido (60 s como máximo, no se guarda) y descripción generada por el LLM, marcada como tal.
- Agente: LLM local (Ollama, unos 9B) con bucle de tool use escrito a mano y salida restringida a los IDs que devuelven las herramientas.
- Evaluación: SDD (ítem conocido), benchmark propio de 50 consultas con pooling, métricas del clasificador y métricas del agente.
- API con FastAPI y demo web (en otro repo) con reproductor de Jamendo y atribución.

**Fuera de v1**
ListenBrainz y filtrado colaborativo · YouTube · fine-tuning de los modelos de embeddings (el adaptador contrastivo va a v2) · Essentia · base de datos vectorial · búsqueda «artista – título» en MusicBrainz · previews de iTunes o Deezer.

## Cómo trabajamos

Claude Code escribe la mayor parte del código; Jofre decide y entiende. En cada hito: primero los conceptos, con preguntas de comprobación; las decisiones se apuntan en `DECISIONS.md`; y en cuatro zonas de aprendizaje pequeñas Jofre escribe el núcleo (ver `CLAUDE.md`).

Cada hito tiene dos criterios de «terminado»: uno técnico y uno de comprensión.

---

## Hito 0 — Entorno y fundamentos (≈2 semanas)

**Conceptos:** vector, producto escalar, norma, similitud coseno, normalización L2, top-k (vecinos más cercanos).

**Jofre:** cuaderno `notebooks/00_coseno.ipynb` con vectores de juguete (por ejemplo, canciones descritas con tres números: energía, tempo, acústica) y su primera función de top-k.

**Delegado:** repo, uv, PyTorch cu128, ruff, pytest, script de comprobación de la GPU.

**Terminado cuando:**
- `uv sync` instala todo y `scripts/check_gpu.py` confirma la RTX 5080 haciendo una multiplicación de matrices en la GPU.
- El cuaderno se ejecuta de principio a fin.
- Comprensión: Jofre explica sin mirar por qué el coseno es el producto escalar de dos vectores normalizados y qué devuelve un top-k.

## Hito 1 — Catálogo (≈2 semanas)

**Conceptos:** metadatos frente a contenido; licencias CC (BY, SA, NC, ND); distribución de etiquetas y cola larga.

**Delegado:**
- Scripts de descarga: metadatos de MTG-Jamendo (incluidas las particiones oficiales del subconjunto mood/theme), audio del subconjunto en baja calidad (unos 46 GB) y SDD (descripciones y audio de sus 706 pistas).
- Enriquecimiento con la API de Jamendo: nombre, artista, licencia y URL de stream. Límite de 35.000 peticiones al mes: pedir varios IDs por llamada y cachear las respuestas.
- `data/processed/catalog.parquet`.

**Jofre:** cuaderno de exploración guiado. ¿Cuántas pistas hay por etiqueta? ¿Y por artista? ¿Qué etiquetas casi no aparecen?

**Terminado cuando:**
- `catalog.parquet` tiene una fila por pista y una columna que dice si el stream de Jamendo sigue disponible. Las pistas no disponibles quedan fuera del índice.
- El README recoge el número de pistas y de artistas y el porcentaje de pistas disponibles.
- Comprensión: Jofre sabe qué licencias hay en el catálogo y qué implican NC y ND para la demo.

## Hito 2 — Embeddings y evaluación en SDD (≈4 semanas)

**Conceptos:** qué es un embedding; espacio compartido texto-audio; aprendizaje contrastivo (de CLIP a CLAP y MuLan), a nivel de intuición; cómo resumir una pista larga en un vector; evaluación de ítem conocido (R@k, MRR, rango mediano).

**Zonas de aprendizaje:** `src/recomendador/search.py` (coseno y top-k sobre la matriz real) y `evaluation/metrics.py` (R@k, MRR, rango mediano).

**Delegado:** wrappers de MuQ-MuLan y CLaMP 3 con una interfaz común (`encode_text`, `encode_audio`, salida normalizada) y script de indexado por lotes en la GPU.

**Pasos:**
1. MuQ-MuLan sobre las 706 pistas y las 1,1k descripciones de SDD: R@1, R@5, R@10 y MRR.
2. CLaMP 3 con el mismo protocolo y tabla comparativa.
3. Miniexperimentos: consultas en español frente a inglés; fragmento central frente a media de ventanas.
4. Indexar el catálogo completo con los dos modelos (`.npy` con su lista de IDs).

**Terminado cuando:**
- `uv run python -m evaluation.sdd` regenera la tabla de `evaluation/results/sdd.md`.
- Los resultados están en el mismo orden de magnitud que los publicados, o hay una explicación escrita de por qué no. Referencia: MusicSem (2026), R@10 de 27,7 para CLAP y de 38,6 para CLaMP 3; el protocolo puede ser distinto.
- Los embeddings del catálogo están guardados para los dos modelos.
- Comprensión: Jofre explica en tres frases cómo se entrena un modelo contrastivo y por qué el R@10 baja al pasar de 706 a 18.000 pistas.

## Hito 3 — Primer entrenamiento: clasificador de moods (≈3 semanas)

**Conceptos:** aprendizaje supervisado; particiones train/validación/test y fuga de datos (por ejemplo, el mismo artista en train y en test); clasificación multietiqueta; función de pérdida (binary cross-entropy); descenso de gradiente, lotes y épocas; sobreajuste y parada temprana; ROC-AUC y PR-AUC; por qué se empieza por un baseline simple.

**Zona de aprendizaje:** el bucle de entrenamiento en `src/recomendador/tagging/train.py`.

**Delegado:** carga de las particiones oficiales, `Dataset` y `DataLoader` de PyTorch, registro de métricas y gráficas de las curvas de aprendizaje.

**Pasos:**
1. Baseline trivial: predecir cada etiqueta con su frecuencia en train. Es el suelo que hay que superar.
2. Sonda lineal (una sola capa) sobre los embeddings congelados.
3. MLP pequeña (una capa oculta) y comparación con la sonda.
4. Comparar los embeddings de MuQ-MuLan y de CLaMP 3 como entrada.
5. Comparar con los resultados de referencia de MTG-Jamendo y comprobar si las particiones oficiales separan por artista.
6. Predecir las 56 puntuaciones de mood para todo el catálogo y guardarlas.

**Terminado cuando:**
- `uv run python -m recomendador.tagging.train` entrena y deja en `evaluation/results/tagging.md` la tabla de ROC-AUC y PR-AUC macro en test: baseline, sonda y MLP, con cada embedding.
- Las puntuaciones de mood están guardadas para todo el catálogo y hay una función que las calcula para un clip nuevo.
- Comprensión: Jofre explica cada línea de su bucle de entrenamiento, cómo reconoce el sobreajuste en las curvas y por qué el test solo se mira al final.

## Hito 4 — Búsqueda híbrida y benchmark propio (≈3 semanas)

**Conceptos:** BM25 (búsqueda léxica); filtros duros; Reciprocal Rank Fusion; MMR y diversidad; varias referencias (centroide frente a una consulta por referencia); pooling al estilo TREC; relevancia graduada; NDCG@k y P@k; test pareado (bootstrap).

**Zonas de aprendizaje:** NDCG@k y P@k en `metrics.py`. Opcional: RRF y MMR en `ranking.py`.

**Delegado:** el resto de `ranking.py`, el endpoint `/search` en FastAPI, una herramienta sencilla para escuchar y etiquetar (relevancia de 0 a 2) y los scripts de pooling.

**Pasos:**
1. Jofre escribe 50 consultas **antes** de ver resultados, de varios tipos: mood, instrumentación, actividad, «como X pero más Y», negaciones.
2. Añadir las puntuaciones de mood predichas (Hito 3) como filtro y como señal más del sistema híbrido.
3. Pool con el top-10 de cuatro sistemas (MuQ-MuLan, CLaMP 3, BM25 e híbrido) y etiquetado.
4. Tabla comparativa: NDCG@10, P@10, diversidad intra-lista, artistas distintos en el top-10 y cobertura del catálogo.
5. Semanas después, volver a etiquetar el 20 % de las consultas para medir la consistencia propia.

**Terminado cuando:**
- `evaluation/benchmark/` contiene `queries.jsonl`, `qrels.jsonl` y los pools versionados, y un comando regenera la tabla.
- Un test pareado dice si el sistema híbrido mejora o no al mejor sistema denso.
- Comprensión: Jofre explica qué es el pooling y por qué el recall que se obtiene es «relativo al pool».

## Hito 5 — Agente (≈3 semanas)

**Conceptos:** function calling o tool use; JSON Schema; el bucle del agente; mensajes `tool` y contexto; decodificación restringida; reescritura de consultas; fidelidad de las explicaciones.

**Zona de aprendizaje:** `src/recomendador/agent/loop.py` (el bucle).

**Delegado:** instalación de Ollama; herramientas con argumentos estrechos (enums de etiquetas, rangos numéricos); validación y reintento; prompts de personalidad (el tono lo decide Jofre).

**Pasos:**
1. Herramientas: `search_text(caption_en, filters)`, `search_similar(track_ids | clip)`, `get_tracks(ids)` y `describe_clip(clip)`, que devuelve los moods predichos con el clasificador del Hito 3.
2. Bucle a mano con el cliente `openai` apuntando a Ollama.
3. Respuesta final con un JSON Schema cuyo `enum` son los IDs candidatos del turno, más validación en Python.
4. Experimento: consulta cruda frente a consulta reescrita por el LLM, medido en el benchmark.
5. Evaluación del agente en unas 30 consultas: herramienta correcta, argumentos válidos, fallos a la primera, cumplimiento de restricciones, IDs fuera del catálogo (debe ser 0) y fidelidad de las explicaciones a las etiquetas.

**Terminado cuando:**
- Hay un chat por terminal que funciona en local.
- La tabla de métricas del agente está en `evaluation/results/agent.md`.
- Comprensión: Jofre dibuja el bucle de memoria y explica qué pasa cuando el modelo genera un argumento inválido.

## Hito 6 — API y demo (≈2 semanas, casi todo delegado)

**Conceptos:** proveedor de LLM intercambiable (interfaz compatible con OpenAI); qué se precalcula y qué necesita el servidor en el momento de la consulta (solo el codificador de texto, la matriz de embeddings y el clasificador).

**Delegado:** endpoint `/chat`; despliegue (por ejemplo, un Space de Hugging Face en CPU con un LLM gratuito por API; verificar antes los límites actuales); repo de la web con reproductor de Jamendo y atribución; página de metodología y resultados.

**Terminado cuando:**
- Una URL pública responde a una petición de principio a fin.
- La página de metodología muestra las tablas de SDD, del clasificador, del benchmark y del agente, generadas por los scripts.

---

## v2 (ideas, sin orden)

Adaptador contrastivo entrenado encima de los embeddings (excluyendo las pistas de SDD del entrenamiento) · Essentia (BPM, tonalidad e instrumentos como filtros) · «artista – título» → etiquetas de MusicBrainz · medir el solapamiento real con ListenBrainz · búsqueda aproximada con FAISS y medir su error · catálogo completo de MTG-Jamendo.

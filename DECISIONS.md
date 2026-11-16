# DECISIONS

Cada decisión lleva fecha, qué se decide, por qué, qué se descartó y cuándo revisarla. Las nuevas se añaden al final. Si una cambia, no se borra: se marca como «sustituida por Dxx».

---

## D01 — Catálogo: MTG-Jamendo en lugar de FMA (2026-11-16)

**Decisión:** subconjunto mood/theme de MTG-Jamendo (unas 18.500 pistas, unos 46 GB en baja calidad) más las 706 pistas del Song Describer Dataset (SDD).

**Por qué:**
- Sobre MTG-Jamendo existe SDD: 1,1k descripciones escritas por personas para 706 pistas. Permite medir la búsqueda texto→música con respuesta conocida y compararla con resultados publicados. FMA no tiene nada equivalente.
- Tiene etiquetas de género, instrumento y mood/theme (195 en total) que sirven como filtros y para evaluar.
- La API de Jamendo permite reproducir las pistas en usos no comerciales (35.000 peticiones al mes), así que no hay que alojar audio.
- Es un dataset del MTG de la UPF.

**Descartado:** FMA. No tiene benchmark de texto ni una API de streaming documentada, y sus clips son de 30 s.

**Revisar:** en el Hito 1, según cuántas pistas sigan disponibles en Jamendo.

## D02 — Sin señal colaborativa en v1 (2026-11-16)

**Decisión:** ListenBrainz queda fuera de v1.

**Por qué:** ni FMA ni MTG-Jamendo traen identificadores de MusicBrainz. MusicBrainz solo tiene unas 4.000 releases de Jamendo, frente a más de 500.000 canciones en la plataforma, y la similitud de ListenBrainz exige un mínimo de coescuchas. El solapamiento es probablemente casi nulo, aunque nadie lo ha medido. Tampoco hay datasets públicos de interacciones usuario-pista sobre catálogos Creative Commons.

**Revisar:** en v2, con un experimento barato: mapear 1.000 pistas con `mbid-mapping` y contar cuántas tienen vecinos.

## D03 — Modelos: MuQ-MuLan primero, CLaMP 3 como rival (2026-11-16)

**Decisión:** empezar con MuQ-MuLan y comparar con CLaMP 3 usando el mismo protocolo.

**Por qué:**
- Los dos ponen texto y audio en el mismo espacio, que es lo que hace falta para «describe lo que buscas».
- MuQ-MuLan tiene la API más sencilla (`pip install muq`) y embeddings de 512 dimensiones.
- CLaMP 3 es el mejor publicado en SDD según el benchmark independiente de MusicSem (2026): R@10 de 38,6 frente a 27,7 de CLAP. Además, su codificador de texto es multilingüe, así que acepta consultas en español o catalán.
- Compararlos con el mismo protocolo es el experimento central del Hito 2.

**Descartado:**
- MERT como modelo principal: no tiene parte de texto. Se usa indirectamente, porque CLaMP 3 extrae el audio con él.
- LAION-CLAP como modelo principal: está poco mantenido y da errores de carga con versiones nuevas de transformers. Queda como baseline opcional.

**Consecuencia aceptada:** los pesos de MuQ-MuLan y de MERT son CC BY-NC 4.0 (no comerciales). Vale para un porfolio, pero impide un uso comercial sin rehacer esta parte.

**Revisar:** en el Hito 2, con los resultados.

## D04 — Búsqueda exacta con numpy, sin base de datos vectorial (2026-11-16)

**Decisión:** guardar los embeddings como una matriz normalizada y buscar con un producto matriz-vector seguido de top-k.

**Por qué:** 18.500 × 512 floats ocupan unos 38 MB, y una consulta tarda milisegundos. La búsqueda es exacta, así que no añade error a la evaluación. Y programarla enseña qué hace un índice por dentro.

**Descartado:** Qdrant, Pinecone, pgvector y los índices HNSW de FAISS. Son aproximados y solo compensan a partir de millones de vectores.

**Revisar:** si el catálogo supera el millón de pistas.

## D05 — Ranking híbrido por etapas (2026-11-16)

**Decisión:** filtros duros → recuperación en paralelo (densa, BM25 sobre etiquetas y similitud con referencias) → fusión con RRF → MMR, con un máximo de 1-2 pistas por artista.

**Por qué:** los modelos tipo CLAP fallan con negaciones («sin voz») y atributos concretos; los filtros y BM25 cubren ese hueco. RRF combina listas sin tener que calibrar escalas de puntuación.

**Condición:** cada etapa se queda solo si mejora el benchmark (Hito 4).

## D06 — Referencias fuera del catálogo: subir un clip sí, YouTube no (2026-11-16)

**Decisión v1:** texto libre, canciones del catálogo, clip subido (60 s como máximo, procesado en memoria y sin guardarlo) y una descripción del LLM marcada como tal y visible para el usuario, que puede corregirla.

**Por qué no YouTube:** sus condiciones de uso prohíben descargar, y YouTube bloquea las descargas desde IPs de servidores (los mantenedores de yt-dlp lo consideran irresoluble). Funcionaría en casa y fallaría en la demo.

**v2:** «artista – título» → etiquetas de MusicBrainz (CC BY-NC-SA). Previews de iTunes o Deezer solo después de leer sus condiciones actuales, que no están verificadas.

## D07 — LLM local con Ollama y bucle escrito a mano (2026-11-16)

**Decisión:** un modelo de unos 8-9B con buen tool calling, servido con Ollama. El candidato es Qwen3.5-9B en Q4 (unos 6 GB), pero las cifras vienen de fuentes secundarias: hay que comprobarlas en el Hito 5. Cabe en los 16 GB junto al codificador de texto.

El bucle se escribe a mano con el cliente `openai` apuntando a Ollama (unas 60 líneas), para entender los esquemas, los errores y los reintentos.

**Descartado:**
- Frameworks de agentes en v1: esconden justo el bucle que se quiere entender.
- vLLM: su soporte para sm_120 está inmaduro.

## D08 — Solo IDs del catálogo, garantizado por construcción (2026-11-16)

**Decisión:** tres capas.
1. Las herramientas devuelven candidatos con sus IDs.
2. La respuesta final usa un JSON Schema con un `enum` de esos IDs (decodificación restringida).
3. Una validación en Python descarta lo que no cuadre y reintenta.

Las herramientas tienen argumentos estrechos y tipados (enums de etiquetas, rangos numéricos), no SQL libre.

**Por qué:** en TalkPlay-Tools (2025), el sistema más parecido, las llamadas SQL solo acertaban a la primera el 27,4 % de las veces, y los IDs largos se generaban mal.

## D09 — Evaluación en dos niveles, más el agente por separado (2026-11-16)

**Decisión:**
1. **SDD (ítem conocido):** R@1, R@5, R@10, MRR y rango mediano. Aquí el recall es real.
2. **Benchmark propio:** 50 consultas escritas antes de ver resultados; pooling del top-10 de cuatro sistemas; relevancia de 0 a 2; NDCG@10, P@10 y diversidad; test pareado. Aquí el recall es «relativo al pool».
3. **Agente:** herramienta y argumentos correctos, fallos a la primera, restricciones cumplidas, IDs fuera del catálogo (debe ser 0 %) y fidelidad de las explicaciones.

**Por qué:** con una sola persona etiquetando y 50 consultas no se puede juzgar todo el catálogo, y solo se detectan diferencias grandes. Volver a etiquetar el 20 % mide la consistencia propia. Un LLM como juez sirve solo de apoyo, nunca como métrica principal: no escucha el audio y tiene sesgos conocidos.

## D10 — Repos y herramientas (2026-11-16)

**Decisión:** un repo para el recomendador (servicio Python con API) y otro para la web, que se empieza en el Hito 6. Python 3.12 con uv, PyTorch ≥ 2.7 con ruedas cu128, ruff, pytest y FastAPI. Los datos y los embeddings quedan fuera de git (`data/`).

**Revisar:** si alguna dependencia de los modelos no funciona con Python 3.12, bajar a 3.11.

## D11 — Modo de trabajo (2026-11-16)

**Decisión:** Claude Code escribe la mayor parte del código. Jofre decide, entiende y escribe solo cuatro zonas pequeñas: coseno y top-k, métricas, bucle de entrenamiento (añadida con D12) y bucle del agente. Cada hito tiene un criterio de comprensión además del técnico. Con «modo explicación», Claude escribe también una zona y Jofre la explica de vuelta.

**Por qué:** el objetivo es aprender y entender las decisiones, con 5-10 h/semana y nivel inicial.

## D12 — Primer entrenamiento en v1: clasificador de moods (2026-11-16)

**Decisión:** nuevo Hito 3, entre los embeddings y la búsqueda híbrida. Se entrena en PyTorch un clasificador de las 56 etiquetas de mood/theme sobre los embeddings congelados, con las particiones oficiales de MTG-Jamendo, en este orden: baseline trivial → sonda lineal → MLP pequeña. Los hitos siguientes se renumeran: búsqueda híbrida (4), agente (5) y demo (6).

**Por qué:**
- Sin esto, la v1 solo usa modelos preentrenados y no enseña a entrenar, que es básico para trabajar en ML de audio.
- Solo depende de los embeddings del Hito 2, así que encaja justo después.
- Alimenta los hitos siguientes: las puntuaciones de mood sirven como filtro en la búsqueda híbrida y para describir el clip que sube el usuario. Añadirlo en v2 obligaría a rehacer esas partes.
- Hay resultados de referencia publicados con los que comparar.

**Coste aceptado:** unas 3 semanas más antes de tener el chat funcionando.

**Descartado en v1:** el adaptador contrastivo (entrenar una capa encima de los embeddings con la misma pérdida que CLAP). Pasa a v2: es más difícil y exige excluir las pistas de SDD del entrenamiento para no contaminar la evaluación.

**Revisar:** al terminar el Hito 3, según si la MLP mejora a la sonda lineal.

## D13 — Hook pre-push: checks que bloquean y revisión de Claude que informa (2026-11-16)

**Decisión:** un hook de git escrito a mano (`.githooks/pre-push`, activado con `git config core.hooksPath .githooks`) que antes de cada push:
1. Ejecuta `ruff check`, `ruff format --check` y `pytest`. Si algo falla, **bloquea** el push.
2. Lanza `claude -p` sobre el diff que se sube, con las normas de `.claude/review-rules.md`. Este paso **solo informa**: muestra el informe, lo guarda en `.reviews/` (fuera de git) y nunca bloquea.

**Por qué:** lo determinista puede bloquear; una opinión no determinista, no. Si la revisión bloqueara, un falso positivo obligaría a usar `--no-verify`, que se salta también ruff y pytest. Las normas incluyen las reglas de `CLAUDE.md` que ruff no ve, y en las zonas de aprendizaje la revisión da pistas y nunca la solución.

**Coste aceptado:** cada push gasta tokens y tarda entre unos 30 s y un par de minutos. Se puede saltar solo la revisión con `SKIP_REVIEW=1 git push`.

**Descartado:**
- El framework `pre-commit`: más configuración y usa su propia copia de ruff, que puede no coincidir con `uv.lock`.
- Que la revisión de Claude bloquee si encuentra algo crítico, o que solo se lance a petición.
- GitHub Actions por ahora: revisa después de subir y aún no hay remoto. Se añadirá al crear el repo en GitHub.

**Revisar:** de forma continua. Cada falso positivo se apunta en «Falsos positivos conocidos» de `.claude/review-rules.md`. Replantear el modo si la revisión resulta inútil o demasiado ruidosa.

## D14 — Comando `/cerrar-dia` para cerrar cada sesión (2026-11-16)

**Decisión:** un comando de proyecto (`.claude/commands/cerrar-dia.md`) que solo se ejecuta cuando Jofre lo escribe. Resume el día, revisa conceptos y decisiones (y añade a este archivo las que falten), guarda en la memoria de Claude el punto del proyecto, propone el siguiente paso y hace commit, y push si hay remoto.

**Por qué:** con 5-10 h/semana, las sesiones están separadas por días. Retomar exige saber exactamente dónde se quedó y qué conceptos quedaron flojos.

**Descartado:** una skill que Claude active por su cuenta. Cerrar el día lo decide Jofre.

---

## Pendiente de decidir

- Nombre del repo.
- Cómo resumir una pista larga en un vector: fragmento central o media de ventanas (Hito 2, con un experimento).
- Qué modelo indexa el catálogo final (Hito 2, según los resultados en SDD).
- Qué embedding y qué arquitectura (sonda o MLP) usa el clasificador final (Hito 3).
- Herramienta para etiquetar el benchmark (Hito 4).
- Modelo exacto del LLM (Hito 5).
- Tono de la personalidad (Hito 5).
- Dónde desplegar y qué LLM gratuito usar en la demo (Hito 6; verificar los límites del momento).

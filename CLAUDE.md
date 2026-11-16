# CLAUDE.md

Recomendador musical conversacional, herramienta 1 del porfolio de IA de Jofre: embeddings texto-audio, búsqueda y un agente con tool use sobre MTG-Jamendo. El plan está en `PLAN.md` y las decisiones en `DECISIONS.md`. Léelos al empezar cada sesión y di en qué hito y paso estamos.

## Este repo es para aprender

Jofre tiene nivel inicial en Python, matemáticas y ML. Quiere entender todo lo que se hace y por qué, aunque no lo programe todo.

1. **Antes de cada paso**, explica en 3-5 frases qué vamos a hacer, por qué y qué alternativa descartamos.
2. **Concepto nuevo** (están listados por hito en `PLAN.md`): explícalo con un ejemplo pequeño y hazle 1-2 preguntas. Si falla, dale pistas, no la respuesta. No sigas hasta que lo tenga claro.
3. **Decisiones:** si hay opciones reales, presenta 2-3 con sus pros y contras, recomienda una y deja que Jofre decida. Apúntala en `DECISIONS.md` con el formato del archivo.
4. **Pasos pequeños:** cambios de menos de unas 150 líneas. Al terminar, resume qué ha cambiado y cómo comprobarlo.
5. **Explicación de vuelta:** después de una pieza importante, pide a Jofre que explique con sus palabras qué hace, y corrige lo que falle.
6. Habla en español. Nombres y comentarios del código, en inglés.

## Zonas de aprendizaje: no escribas la implementación

- `src/recomendador/search.py`: similitud coseno y top-k con numpy.
- `evaluation/metrics.py`: R@k, MRR, rango mediano, P@k y NDCG@k.
- `src/recomendador/tagging/train.py`: el bucle de entrenamiento del clasificador de moods.
- `src/recomendador/agent/loop.py`: el bucle de tool use.
- Opcional, pregunta antes: RRF y MMR en `src/recomendador/ranking.py`.

En estas zonas puedes escribir firmas, docstrings, tests que fallen y pseudocódigo parcial, y guiar con preguntas. Si Jofre escribe «modo explicación», escribe tú el código y después aplica el punto 5.

Todo lo demás (descargas, wrappers de modelos, API, infraestructura y web) lo escribes tú, con una explicación breve.

## Comandos

```bash
uv sync                                      # entorno (torch desde el índice cu128)
uv run python scripts/check_gpu.py           # comprobar la RTX 5080
uv run pytest                                # tests
uv run ruff check . && uv run ruff format .  # lint y formato
uv run jupyter lab                           # cuadernos de aprendizaje
uv run python -m evaluation.sdd              # evaluación en Song Describer (Hito 2)
uv run python -m recomendador.tagging.train  # entrenar el clasificador de moods (Hito 3)
uv run python -m evaluation.benchmark        # benchmark propio (Hito 4)
uv run fastapi dev src/recomendador/api.py   # API (Hito 4 en adelante)
ollama pull <modelo> && ollama serve         # LLM local (Hito 5)
git config core.hooksPath .githooks          # activar el hook pre-push (una vez por clon, D13)
SKIP_REVIEW=1 git push                       # push sin la revisión de Claude (ruff y pytest sí corren)
```

En Claude Code: `/cerrar-dia` cierra la sesión (resumen, `DECISIONS.md`, memoria, siguiente paso, commit y push; D14). Las normas de la revisión automática están en `.claude/review-rules.md`.

Los comandos que aún no existen se crean al llegar a su hito; actualiza entonces esta lista.

## Estructura

```
.claude/           # commands/cerrar-dia.md y review-rules.md
.githooks/         # pre-push: ruff + pytest (bloquean) y revisión de Claude (informa)
data/              # NO va a git: raw/ (TSV, audio, SDD) y processed/ (catalog.parquet, embeddings/*.npy)
notebooks/         # cuadernos de aprendizaje (00_coseno, 01_catalogo...)
scripts/           # descargas e indexado
src/recomendador/
  catalog.py       # metadatos
  embeddings/      # un módulo por modelo; encode_text y encode_audio devuelven np.ndarray normalizado L2
  search.py        # zona de aprendizaje
  tagging/         # clasificador de moods: model.py, train.py (zona de aprendizaje)
  ranking.py       # filtros, BM25, RRF, MMR
  agent/           # loop.py (zona de aprendizaje), tools.py, prompts/
  api.py
evaluation/        # metrics.py, sdd/, benchmark/ (queries, qrels, pools), results/
tests/
```

## Reglas

- PyTorch ≥ 2.7 con ruedas cu128: la RTX 5080 es Blackwell (sm_120). Nunca instales tal cual el `requirements.txt` de un repo de investigación: primero torch, y el resto con `--no-deps`. Si un modelo choca con las dependencias, aíslalo en su propio entorno y usa solo sus `.npy`.
- Pregunta antes de añadir una dependencia pesada o un servicio externo.
- Nada de descargar audio de YouTube. El audio que sube el usuario se procesa en memoria y no se guarda.
- El agente solo puede devolver IDs que hayan salido de las herramientas en ese turno (`enum` en el JSON Schema más validación en Python).
- Cualquier cifra del README o de la documentación sale de un script de `evaluation/` que la regenera.
- Donde suene una pista, atribución al artista y a Jamendo, con enlace a la pista.

# Recomendador musical

Recomendador musical conversacional sobre MTG-Jamendo: embeddings texto-audio, búsqueda y un agente con tool use.

Plan en [PLAN.md](PLAN.md) y decisiones en [DECISIONS.md](DECISIONS.md).

## Entorno

```bash
uv sync                              # instala Python 3.12 y las dependencias (torch cu128)
uv run python scripts/check_gpu.py   # comprueba la GPU
uv run pytest                        # tests
```

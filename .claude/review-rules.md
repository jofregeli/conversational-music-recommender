# Normas de revisión de código

Las usa el hook `.githooks/pre-push` (revisión automática, solo informa) y sirven también para revisar a mano. Ver D13 en `DECISIONS.md`.

## Qué revisar (por prioridad)

1. **Errores de lógica**: casos borde (listas vacías, k mayor que el número de elementos, división por cero, vectores de norma 0), dimensiones de arrays que no cuadran, off-by-one.
2. **Reglas del proyecto** (`CLAUDE.md`):
   - El agente solo puede devolver IDs que hayan salido de las herramientas en ese turno (`enum` en el JSON Schema más validación en Python).
   - Nada de descargar audio de YouTube. El audio que sube el usuario se procesa en memoria y no se guarda en disco.
   - Ningún secreto ni API key en el código: van en `.env`.
   - Las cifras del README o de la documentación salen de un script de `evaluation/`, no se escriben a mano.
   - Donde suene una pista: atribución al artista y a Jamendo, con enlace.
   - Los wrappers de `embeddings/` devuelven `np.ndarray` normalizado L2.
   - Nombres y comentarios del código, en inglés.
   - No se añaden dependencias pesadas sin que estén justificadas en `DECISIONS.md`.
3. **Tests**: lógica nueva sin test (especialmente en `search.py`, `metrics.py`, `ranking.py`). Tests que no comprueban nada.
4. **Datos**: nada de `data/`, `.venv/`, pesos de modelos ni `.npy` grandes dentro del diff.
5. **Claridad**: código duplicado o innecesariamente complicado. Solo si de verdad dificulta entenderlo.

## Zonas de aprendizaje: pistas, nunca la solución

En `src/recomendador/search.py`, `evaluation/metrics.py`, `src/recomendador/tagging/train.py`, `src/recomendador/agent/loop.py` y `src/recomendador/ranking.py` el código lo escribe Jofre para aprender. Si hay un problema:
- Señala dónde está y qué caso falla (por ejemplo, «¿qué devuelve tu función si k = 0?»).
- **No escribas el código corregido** ni un fragmento que lo resuelva.

## Qué NO reportar

- Estilo o formato: ya lo comprueba ruff.
- Preferencias personales sin impacto real.
- Hallazgos de los que no estés seguro: mejor 2 hallazgos ciertos que 10 dudosos.
- Lo que aparezca en «Falsos positivos conocidos».

## Formato de la respuesta

Máximo 10 hallazgos, de más a menos grave:

```
🔴 Crítico | 🟡 Aviso | 🔵 Sugerencia — archivo:línea
Problema: una frase.
Por qué importa: una frase.
Cómo arreglarlo: una frase (o una pista, si es zona de aprendizaje).
```

Si no hay nada relevante, responde solo: «✅ Sin hallazgos relevantes».

## Falsos positivos conocidos

Cuando la revisión marque algo que no es un problema, se apunta aquí con fecha y motivo para que no se repita.

- (vacío por ahora)

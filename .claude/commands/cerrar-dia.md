---
description: Cierra la sesión del día (resumen, conceptos, decisiones, memoria, siguiente paso, commit y push)
disable-model-invocation: true
---

Cerramos la sesión de hoy. Haz esto en orden:

1. **Resumen del día**: qué hemos hecho (archivos creados o cambiados, comandos nuevos). Breve.

2. **Conceptos nuevos**: los que hemos visto hoy y, para cada uno, si Jofre lo explicó bien o si queda algo flojo que convenga repasar al empezar la próxima sesión.

3. **Decisiones**: las que hemos tomado hoy. Compáralas con `DECISIONS.md`. Si falta alguna, añádela con el formato del archivo (siguiente número Dxx y fecha de hoy). Actualiza también «Pendiente de decidir» si algo se ha resuelto o ha surgido algo nuevo.

4. **Memoria**: guarda en tu memoria persistente del proyecto:
   - El punto exacto en el que estamos: hito, paso y qué falta del «Terminado cuando» del hito (técnico y de comprensión).
   - Los cambios importantes y los conceptos que han quedado flojos.
   Actualiza las memorias existentes en vez de duplicarlas y borra las que hayan quedado obsoletas. No guardes lo que ya está en el repo (código, `DECISIONS.md`, historial de git).

5. **Siguiente paso**: el siguiente paso concreto para la próxima sesión y, si hace falta, qué tiene que preparar Jofre antes.

6. **Commit y push**:
   - Mira `git status`. Si hay cambios, haz commit con un mensaje en inglés en imperativo. Comprueba antes que no se cuela nada que deba estar en `.gitignore`.
   - Si hay un remoto configurado y commits sin subir, haz `git push`. El hook pre-push lanzará ruff, pytest y la revisión de Claude: resume lo que diga la revisión. Si los checks fallan, no fuerces el push ni uses `--no-verify`: explica qué falla.
   - Si no hay remoto, dilo y no hagas push.

Termina con este formato:

```
## Cierre del día — <fecha>
**Hecho:** ...
**Conceptos:** ... (✅ claros / 🔁 repasar)
**Decisiones:** ... (añadidas a DECISIONS.md: ...)
**Estamos en:** Hito X, paso Y
**Siguiente paso:** ...
**Git:** commit <hash> / push sí|no (motivo)
```

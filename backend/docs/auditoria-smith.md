# Auditoría LangSmith — `build_run_config()`

**Auditado:** 2026-06-26  
**Última actualización:** 2026-06-27 — `run_name` dinámico implementado  
**Archivos auditados:**
- `app/core/observability.py`
- `app/api/streaming.py`
- `app/api/routes/blueprint.py`

---

## Flujo de ejecución

```
run_blueprint() / resume_blueprint()
  → build_run_config(...)
    → _sse(...)
      → event_stream(...)
        → graph.stream(payload, config=config, stream_mode="updates")
```

---

## 1. Config que se envía a LangGraph (estado actual)

```python
# Siempre (tracing on/off):
config["configurable"]["thread_id"] = "bp-{uuid}"

# Solo si tracing_enabled():
config["run_name"]  = "validation_blueprint/full_run"        # dinámico desde 2026-06-27
config["tags"]      = [app_env, "validation_blueprint", "phase:full_run"]
config["metadata"]  = {
    "session_id":     thread_id,
    "user_id":        user.id,
    "project_id":     project.id,
    "blueprint_id":   bp.id,
    "environment":    app_env,
    "graph_name":     "validation_blueprint",
    "phase_name":     "full_run" | "resume:{stage}",         # condicional
}
```

LangGraph propaga `metadata` y `tags` a **todos los runs hijo** (nodos, LLM calls) automáticamente.

---

## 2. ¿Qué campos llegan realmente a LangSmith?

| Campo | ¿Llega? | Dónde aparece en LangSmith |
|---|---|---|
| `session_id` | ✅ | Metadata del run raíz + hijos |
| `user_id` | ✅ | Metadata filtrable |
| `project_id` | ✅ | Metadata filtrable |
| `blueprint_id` | ✅ | Metadata filtrable |
| `environment` | ✅ | Metadata filtrable |
| `graph_name` | ✅ | Metadata filtrable |
| `phase_name` | ✅ | Metadata filtrable (cuando `phase` no es vacío) |
| `run_name` dinámico | ✅ | Nombre visible en lista de runs — **implementado** |
| `phase` en tags | ✅ | Tag filtrable `phase:{value}` — **implementado** |
| `agent_name` | ⚠️ | Solo como nombre del run hijo (no metadata filtrable) |
| `node_name` | ⚠️ | Solo como nombre del run hijo (no metadata filtrable) |
| `execution_id` | ❌ | No existe |
| `revision_count` | ❌ | Está en `initial_state` pero no en `metadata` |

---

## 3. Cambios implementados (2026-06-27)

### `run_name` dinámico — `app/core/observability.py`

```python
# Antes:
config["run_name"] = GRAPH_NAME  # siempre "validation_blueprint"

# Después:
phase_clean = phase.strip() if isinstance(phase, str) else None
phase_clean = phase_clean or None  # "" → None

config["run_name"] = f"{GRAPH_NAME}/{phase_clean}" if phase_clean else GRAPH_NAME
```

Ejemplos de valores resultantes:

| Llamada | `run_name` resultante |
|---|---|
| `phase="full_run"` | `validation_blueprint/full_run` |
| `phase="resume:human_hypotheses"` | `validation_blueprint/resume:human_hypotheses` |
| `phase="resume:human_prioritization"` | `validation_blueprint/resume:human_prioritization` |
| `phase="resume:human_approval"` | `validation_blueprint/resume:human_approval` |
| `phase=None` o `phase=""` | `validation_blueprint` (fallback seguro) |

### `tags` con fase — `app/core/observability.py`

```python
# Antes:
config["tags"] = [settings.app_env, GRAPH_NAME]

# Después:
config["tags"] = [settings.app_env, GRAPH_NAME] + (
    [f"phase:{phase_clean}"] if phase_clean else []
)
```

Permite filtrar en LangSmith por tag `phase:full_run` o `phase:resume:human_hypotheses`.

### Invariantes que no cambiaron

- `configurable.thread_id` — sin tocar (controla checkpointing e interrupt/resume)
- Campos de `metadata` — los 6 campos base siguen igual
- Firma de `build_run_config()` — sin breaking changes
- `blueprint.py` — no se modificó
- Topología del grafo, nombres de nodos, checkpointer — sin tocar

### Tests unitarios añadidos

Archivo: `tests/test_observability.py` — 19 tests, todos verdes.

Cobertura:
- `run_name` dinámico para cada fase conocida
- Fallback cuando `phase` es `None`, `""` o solo espacios
- `configurable.thread_id` intacto en todos los casos
- `metadata.phase_name` usa `phase_clean` (sin espacios)
- `metadata.phase_name` ausente cuando `phase` es falsy
- Tags incluyen `phase:{value}` solo cuando la fase es válida
- Con tracing desactivado devuelve solo `{"configurable": {"thread_id": ...}}`

---

## 4. Análisis campo por campo de los que aún faltan

### `agent_name` / `node_name`

El comentario en `observability.py` dice:
> *"agent_name/phase_name por nodo ya los pone LangGraph con el nombre del nodo"*

Esto es **parcialmente correcto pero incompleto**:
- LangGraph sí crea runs hijo con el nombre del nodo ("supervisor", "market_agent", etc.) ✅
- Pero esos nombres son el `run_name` del child run en el árbol de trazas, **no son campos `metadata` filtrables** ❌
- Filtrar en LangSmith por `agent_name = "market_agent"` no funciona porque no está en `metadata`

### `execution_id`

No existe. En flujos interrupt/resume, el mismo `thread_id` agrupa todos los runs. No hay forma de distinguir la 3ª reanudación de la 1ª salvo por `phase_name`.

### `revision_count`

Está en `initial_state` (`blueprint.py` línea 89) pero no se pasa a `config["metadata"]`.

```python
initial_state = {
    "revision_count": 0,  # en estado del grafo ✅, en LangSmith ❌
    ...
}
```

---

## 5. Comparación con mejores prácticas LangGraph + LangSmith

| Práctica | Estado |
|---|---|
| Metadata explícita en config (no context vars) | ✅ Correcto — esencial para worker threads |
| `session_id` = `thread_id` para agrupar interrupt/resume | ✅ Correcto |
| Configuración 100% por env vars | ✅ Correcto |
| `run_name` dinámico con fase | ✅ **Implementado 2026-06-27** |
| Tags con fase para filtrado | ✅ **Implementado 2026-06-27** |
| `node_name`/`agent_name` en metadata | ❌ No posible sin tocar nodos o usar callbacks |
| `execution_id` para correlación | ❌ Pendiente |
| `revision_count` en metadata | ❌ Pendiente |

---

## 6. Cómo añadir `agent_name`/`node_name` como metadata filtrable

El código tiene la restricción de "no tocar los agentes". Las dos únicas vías sin modificar nodos son:

- **Callback handler**: Implementar un `BaseCallbackHandler` que intercepte `on_chain_start` y enriquezca el contexto con el node name. Se pasa en `config["callbacks"]`.
- **LangSmith `@traceable` decorator**: No aplica aquí porque el objetivo es LangGraph nativo.

Sin tocar nodos ni callbacks, `agent_name`/`node_name` como **metadata filtrable** no es posible con la arquitectura actual.

---

## 7. Cómo verificar en LangSmith

**Trace raíz con nombre dinámico**
Lista de runs → busca `Name = validation_blueprint/full_run`. O filtra por tag `phase:full_run`.

**Nodos/agentes sin cambios**
Abre cualquier trace. Los nombres hijo (`supervisor`, `market_agent`, etc.) deben ser idénticos a antes. `run_name` solo afecta el run raíz.

**Resumes agrupados bajo el mismo `thread_id`**
Filtra por `metadata.session_id = bp-{uuid}`. Verás el `full_run` y todos sus `resume:*` compartiendo el mismo `session_id`.

**Sin threads nuevos accidentales**
`graph.get_state({"configurable": {"thread_id": "bp-{uuid}"}})` debe devolver el estado completo del blueprint sin importar cuántos resumes haya habido.

---

## 8. Pendientes recomendados

| Prioridad | Cambio | Archivo |
|---|---|---|
| Media | Pasar `revision_count` a `metadata` | `blueprint.py` + `observability.py` |
| Media | Añadir `execution_id` (`uuid4()`) en el endpoint | `blueprint.py` |
| Baja | `BaseCallbackHandler` para enriquecer nodos con `agent_name` | nuevo archivo |

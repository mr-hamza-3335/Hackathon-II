# Quickstart: Backend Event Publishing

**Branch**: `004-backend-event-publishing`

## Prerequisites

- Phase IV API running (FastAPI + PostgreSQL)
- Dapr sidecar installed (for Kubernetes deployment)
- Kafka + Dapr components deployed (Phase V Stage 3)

## Local Development (Without Dapr)

Set `DAPR_ENABLED=false` (default). Events are logged at DEBUG level but not sent to Kafka.

```bash
# Start API as usual
cd api
uvicorn src.main:app --reload
```

Create a task — you'll see log output like:
```
DEBUG:src.events.publisher:Event publish skipped (Dapr disabled): task.created on task-events
```

## Kubernetes (With Dapr)

Set environment variables:
```yaml
env:
  - name: DAPR_ENABLED
    value: "true"
  - name: DAPR_HTTP_PORT
    value: "3500"  # Auto-injected by Dapr
```

## Verification

### Check events on Kafka topics

```bash
# Port-forward to Kafka
kubectl port-forward svc/kafka 9092:9092 -n pakaura

# Consume from task-events topic
kubectl exec -it kafka-0 -n pakaura -- \
  /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

### Create a task and verify event

```bash
# Create task via API
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Cookie: auth_token=<jwt>" \
  -d '{"title": "Test event publishing"}'

# Expected: CloudEvents JSON appears in the Kafka consumer output
```

## New Files

| File | Purpose |
|------|---------|
| `api/src/events/__init__.py` | Events module init |
| `api/src/events/schemas.py` | CloudEvents Pydantic models |
| `api/src/events/publisher.py` | Dapr Pub/Sub publisher helper |
| `api/src/config.py` | Updated with DAPR_ENABLED, DAPR_HTTP_PORT settings |

## Modified Files

| File | Change |
|------|--------|
| `api/src/routes/tasks.py` | Add event publishing after each CRUD operation |
| `api/src/mcp_server/task_operations.py` | Add event publishing after each operation |

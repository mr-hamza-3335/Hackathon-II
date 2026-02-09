# Dapr Publish API Contract

**Used by**: `api/src/events/publisher.py`
**Dapr sidecar**: `http://localhost:{DAPR_HTTP_PORT}` (default 3500)

## Publish Event

### Request

```
POST /v1.0/publish/{pubsubname}/{topic}
Content-Type: application/cloudevents+json
```

**Path Parameters**:

| Parameter | Value |
|-----------|-------|
| `pubsubname` | `pubsub-kafka` |
| `topic` | `task-events` \| `task-updates` \| `reminders` |

**Body**: CloudEvents 1.0 JSON envelope (see data-model.md for full schema)

```json
{
  "specversion": "1.0",
  "id": "<uuid>",
  "source": "pakaura/api",
  "type": "<event-type>",
  "time": "<iso-8601>",
  "subject": "<task-id>",
  "datacontenttype": "application/json",
  "traceid": "<correlation-uuid>",
  "data": { ... }
}
```

### Response

| Status | Meaning |
|--------|---------|
| 204 | Event published successfully (no body) |
| 403 | Pubsub component not found or not allowed |
| 404 | Topic not found |
| 500 | Dapr sidecar internal error |

### Error Handling

- On **204**: Log success at DEBUG level
- On **non-204**: Log error at ERROR level with event type, topic, status code, response body
- On **connection error** (sidecar down): Log at WARNING level, continue without retrying
- On **timeout** (>2s): Log at WARNING level, continue without retrying

### Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `DAPR_HTTP_PORT` | `3500` | Dapr sidecar HTTP port |
| `DAPR_ENABLED` | `false` | Enable/disable event publishing |

When `DAPR_ENABLED` is `false`, the publisher logs events at DEBUG level instead of sending them. This allows the API to run without Dapr (local development, testing).

# API Documentation

## Endpoints (Phase 1)

### `GET /health`
Returns the status of the FastAPI backend application.

#### Request:
```http
GET /health HTTP/1.1
Host: localhost:8000
```

#### Response:
```json
{
  "status": "ok"
}
```

#### Optional Query Parameters:
- `detailed=true`: Returns extended health diagnostics including version, environment, and database connectivity.

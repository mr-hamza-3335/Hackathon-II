# Phase IV: Local Kubernetes Deployment

## Objective

Deploy the PakAura AI-powered task management application to a local Kubernetes cluster using Minikube and Helm charts, demonstrating production-ready containerization and orchestration.

## Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | Latest | Container runtime |
| Minikube | v1.37.0+ | Local Kubernetes cluster |
| Kubernetes | v1.34.0+ | Container orchestration |
| Helm | v3.x | Kubernetes package manager |
| kubectl | v1.34.0+ | Kubernetes CLI |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster (Minikube)                 │
│                         Namespace: pakaura                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Frontend Pod  │  │    API Pod      │  │  PostgreSQL Pod │  │
│  │   (Next.js)     │  │   (FastAPI)     │  │   (postgres:16) │  │
│  │   Port: 3000    │  │   Port: 8000    │  │   Port: 5432    │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │           │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐  │
│  │ Service:NodePort│  │ Service:ClusterIP│  │Service:ClusterIP│  │
│  │   30300:3000    │  │     8000:8000   │  │    5432:5432    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ConfigMap + Secrets                    │   │
│  │  DATABASE_URL, JWT_SECRET, COHERE_API_KEY, FRONTEND_URL  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    kubectl port-forward
                              │
                    ┌─────────┴─────────┐
                    │   localhost:3000  │  (Frontend)
                    │   localhost:8000  │  (API)
                    └───────────────────┘
```

## Project Structure

```
infra/
├── docker/
│   ├── api.Dockerfile         # Multi-stage Python build
│   └── frontend.Dockerfile    # Multi-stage Next.js build
└── helm/
    └── pakaura/
        ├── Chart.yaml         # Helm chart metadata
        ├── values.yaml        # Default configuration
        ├── values-local.yaml  # Minikube-specific overrides
        └── templates/
            ├── _helpers.tpl   # Template helpers
            ├── NOTES.txt      # Post-install instructions
            ├── api/
            │   ├── deployment.yaml
            │   └── service.yaml
            ├── frontend/
            │   ├── deployment.yaml
            │   └── service.yaml
            ├── postgres/
            │   ├── deployment.yaml
            │   ├── service.yaml
            │   └── pvc.yaml
            └── shared/
                ├── configmap.yaml
                └── secrets.yaml
```

## Prerequisites

1. **Docker Desktop** installed and running
2. **Minikube** installed:
   ```bash
   # Windows (chocolatey)
   choco install minikube

   # macOS
   brew install minikube

   # Linux
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

3. **Helm** installed:
   ```bash
   # Windows (chocolatey)
   choco install kubernetes-helm

   # macOS
   brew install helm

   # Linux
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

## Deployment Steps

### 1. Start Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=2
```

### 2. Configure Docker to Use Minikube's Daemon

```bash
# PowerShell (Windows)
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Bash (Linux/macOS)
eval $(minikube docker-env)
```

### 3. Build Docker Images

```bash
# Build API image
cd api
docker build -t pakaura-api:latest -f ../infra/docker/api.Dockerfile .
cd ..

# Build Frontend image
cd frontend
docker build -t pakaura-frontend:latest -f ../infra/docker/frontend.Dockerfile .
cd ..
```

### 4. Deploy with Helm

```bash
# Install the Helm chart
helm install pakaura ./infra/helm/pakaura -f ./infra/helm/pakaura/values-local.yaml

# Or upgrade if already installed
helm upgrade --install pakaura ./infra/helm/pakaura -f ./infra/helm/pakaura/values-local.yaml
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n pakaura

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# api-xxxxx                   1/1     Running   0          1m
# frontend-xxxxx              1/1     Running   0          1m
# postgres-xxxxx              1/1     Running   0          1m

# Check services
kubectl get svc -n pakaura
```

### 6. Access the Application

```bash
# Set up port forwarding
kubectl port-forward -n pakaura svc/frontend 3000:3000 &
kubectl port-forward -n pakaura svc/api 8000:8000 &
```

Open in browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **API Health**: http://localhost:8000/api/v1/health

## Key Features

### Auto-Migration on Deploy

The API deployment includes an init container that automatically runs database migrations:

```yaml
initContainers:
  - name: run-migrations
    image: pakaura-api:latest
    command: ["alembic", "upgrade", "head"]
```

This ensures the database schema is always up-to-date when deploying.

### Health Probes

Both API and Frontend have configured health probes:

```yaml
readinessProbe:
  httpGet:
    path: /api/v1/health  # API
    path: /               # Frontend
  initialDelaySeconds: 10
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /api/v1/health
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Configuration Management

- **ConfigMap**: Non-sensitive configuration (AI model, environment, debug flags)
- **Secrets**: Sensitive data (DATABASE_URL, JWT_SECRET, COHERE_API_KEY)

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod -n pakaura <pod-name>

# Check logs
kubectl logs -n pakaura <pod-name>

# For init container logs
kubectl logs -n pakaura <pod-name> -c run-migrations
```

### Database connection issues

```bash
# Verify postgres is running
kubectl exec -n pakaura deploy/postgres -- pg_isready

# Check tables exist
kubectl exec -n pakaura deploy/postgres -- psql -U pakaura -d pakaura_db -c "\dt"
```

### Reset deployment

```bash
# Uninstall and reinstall
helm uninstall pakaura
kubectl delete namespace pakaura
helm install pakaura ./infra/helm/pakaura -f ./infra/helm/pakaura/values-local.yaml
```

## Clean Up

```bash
# Remove Helm release
helm uninstall pakaura

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Success Criteria

- [x] All pods running (api, frontend, postgres)
- [x] Database migrations run automatically
- [x] Frontend accessible via port-forward
- [x] User registration works
- [x] User login works with JWT cookies
- [x] AI chatbot responds to commands
- [x] Tasks can be created, completed, deleted

## Related Documentation

- [ARCHITECTURE.md](submission-final/ARCHITECTURE.md) - System architecture details
- [DEMO-SCRIPT.md](submission-final/DEMO-SCRIPT.md) - Demo walkthrough for judges
- [README.md](submission-final/README.md) - Full project documentation

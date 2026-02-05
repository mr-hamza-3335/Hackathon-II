# Implementation Plan: Phase IV Kubernetes Deployment

**Branch**: `002-kubernetes-deployment` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/phase-4-kubernetes-deployment/spec.md`

---

## Executive Summary

This plan deploys the AI Todo Chatbot (Phase III) to a local Kubernetes cluster using Minikube. The implementation is divided into **5 logical phases**, each with clear deliverables, validation steps, and AI-assisted tooling.

**Timeline**: ~2-3 hours for complete implementation
**Complexity**: Medium (infrastructure only, no application code changes)
**Risk Level**: Low (local environment, reversible)

---

## Technical Context

| Aspect | Value |
|--------|-------|
| **Platform** | Kubernetes (Minikube) v1.32+ |
| **Container Runtime** | Docker v24.0+ |
| **Package Manager** | Helm v3.14+ |
| **CLI Tools** | kubectl v1.29+, minikube, docker |
| **AI Tooling** | Claude Code (script generation, troubleshooting) |
| **Target Platform** | Local development (Windows/macOS/Linux) |
| **Constraints** | 8GB RAM, 4 CPU cores minimum |
| **Scope** | Infrastructure deployment only |

---

## AI-Assisted DevOps Tools Reference

Throughout this plan, we use AI-assisted tools to accelerate development:

| Tool | Purpose | How Claude Code Helps |
|------|---------|----------------------|
| **Claude Code** | Primary AI assistant | Generates all scripts, manifests, Helm charts |
| **kubectl** | Kubernetes CLI | Claude explains commands, troubleshoots errors |
| **Helm** | Package deployment | Claude creates chart structure, values files |
| **Docker** | Image building | Claude optimizes Dockerfiles, multi-stage builds |
| **minikube** | Local K8s cluster | Claude provides setup commands, addon configuration |

> **Note**: There is no separate "kubectl-ai" or "kagent" tool. Claude Code serves as the AI layer that assists with all DevOps tasks through natural language interaction.

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE IV EXECUTION ROADMAP                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: Environment Setup                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Install prerequisites (Docker, Minikube, kubectl, Helm)           │   │
│  │ • Start Minikube cluster                                            │   │
│  │ • Enable required addons (ingress, metrics-server)                  │   │
│  │ • Validate cluster is healthy                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  PHASE 2: Containerization                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Create optimized Dockerfile for API (multi-stage)                 │   │
│  │ • Create optimized Dockerfile for Frontend (standalone)             │   │
│  │ • Build images in Minikube's Docker daemon                          │   │
│  │ • Verify image sizes meet targets                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  PHASE 3: Kubernetes Manifests                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Create namespace, ConfigMaps, Secrets                             │   │
│  │ • Create PostgreSQL StatefulSet with PVC                            │   │
│  │ • Create API Deployment with health probes                          │   │
│  │ • Create Frontend Deployment                                        │   │
│  │ • Create Services and Ingress                                       │   │
│  │ • Create Migration Job                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  PHASE 4: Helm Chart Creation                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Initialize Helm chart structure                                   │   │
│  │ • Create parameterized templates                                    │   │
│  │ • Define values.yaml with all configurations                        │   │
│  │ • Add helper functions (_helpers.tpl)                               │   │
│  │ • Create NOTES.txt for post-install instructions                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  PHASE 5: Deployment & Validation                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Create AI-assisted deployment script                              │   │
│  │ • Deploy via Helm                                                   │   │
│  │ • Validate all pods running                                         │   │
│  │ • Test end-to-end functionality                                     │   │
│  │ • Document demo workflow                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Environment Setup

### Objective
Prepare the local development environment with all required tools and a running Minikube cluster.

### Duration
~15-20 minutes

### Prerequisites Checklist

| Tool | Version | Check Command | Install Guide |
|------|---------|---------------|---------------|
| Docker | 24.0+ | `docker --version` | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Minikube | 1.32+ | `minikube version` | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.29+ | `kubectl version --client` | [kubernetes.io/docs](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.14+ | `helm version` | [helm.sh/docs](https://helm.sh/docs/intro/install/) |

### Steps

#### Step 1.1: Verify Prerequisites
```bash
# AI-Assisted: Claude Code generates this verification script
# Run these commands to check all tools are installed

docker --version          # Expected: Docker version 24.x+
minikube version          # Expected: minikube version: v1.32+
kubectl version --client  # Expected: Client Version: v1.29+
helm version              # Expected: version.BuildInfo{Version:"v3.14+"}
```

#### Step 1.2: Start Minikube Cluster
```bash
# Start Minikube with sufficient resources for our application
# Using Docker driver for cross-platform compatibility

minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.29.0

# Verify cluster is running
minikube status
```

**Expected Output**:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

#### Step 1.3: Enable Required Addons
```bash
# Enable ingress controller for external access
minikube addons enable ingress

# Enable metrics-server for resource monitoring
minikube addons enable metrics-server

# Verify addons are enabled
minikube addons list | grep -E "ingress|metrics"
```

**Expected Output**:
```
| ingress                     | minikube | enabled ✅   |
| metrics-server              | minikube | enabled ✅   |
```

#### Step 1.4: Configure Docker Environment
```bash
# Point Docker CLI to Minikube's Docker daemon
# This allows us to build images directly in Minikube

eval $(minikube docker-env)

# Verify connection
docker ps  # Should show Minikube system containers
```

### Validation Checkpoint 1

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Minikube Running | `minikube status` | All components "Running" |
| Kubectl Connected | `kubectl cluster-info` | Shows cluster endpoint |
| Ingress Ready | `kubectl get pods -n ingress-nginx` | Controller pod running |
| Docker Connected | `docker info \| grep "Server Version"` | Shows version |

### Error Mitigation: Phase 1

| Error | Cause | Solution |
|-------|-------|----------|
| "minikube start" fails with memory error | Insufficient system RAM | Reduce `--memory=4096` or close other applications |
| "driver docker not found" | Docker not running | Start Docker Desktop or Docker daemon |
| kubectl connection refused | Minikube not started | Run `minikube start` |
| Ingress addon fails | Minikube version too old | Update Minikube: `minikube update-check` |

---

## Phase 2: Containerization

### Objective
Create optimized Docker images for the API and Frontend services, built directly in Minikube's Docker daemon.

### Duration
~20-30 minutes

### Directory Structure to Create
```
infra/
└── docker/
    ├── api.Dockerfile        # FastAPI backend image
    └── frontend.Dockerfile   # Next.js frontend image
```

### Steps

#### Step 2.1: Create API Dockerfile (Backend)
```dockerfile
# File: infra/docker/api.Dockerfile
# AI-Generated: Optimized multi-stage build for FastAPI

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser alembic/ ./alembic/

USER appuser

EXPOSE 8000

# Health check for Kubernetes probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 2.2: Create Frontend Dockerfile
```dockerfile
# File: infra/docker/frontend.Dockerfile
# AI-Generated: Optimized standalone Next.js build

# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js in standalone mode
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only necessary files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

#### Step 2.3: Update Frontend for Standalone Mode
```javascript
// File: frontend/next.config.js (update required)
// Add output: 'standalone' for Docker optimization

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',  // Required for optimized Docker builds
  // ... existing config
}
```

#### Step 2.4: Build Docker Images
```bash
# Ensure Docker is pointed to Minikube
eval $(minikube docker-env)

# Build API image
docker build \
  -t pakaura-api:4.0.0 \
  -f infra/docker/api.Dockerfile \
  ./api

# Build Frontend image
docker build \
  -t pakaura-frontend:4.0.0 \
  -f infra/docker/frontend.Dockerfile \
  ./frontend

# Verify images are built
docker images | grep pakaura
```

**Expected Output**:
```
pakaura-api        4.0.0    abc123def456   10 seconds ago   ~230MB
pakaura-frontend   4.0.0    def456abc789   30 seconds ago   ~140MB
```

### Validation Checkpoint 2

| Check | Command | Expected Result |
|-------|---------|-----------------|
| API Image Built | `docker images pakaura-api` | Image exists, <250MB |
| Frontend Image Built | `docker images pakaura-frontend` | Image exists, <150MB |
| API Runs Locally | `docker run --rm pakaura-api:4.0.0 --version` | No errors |
| Frontend Runs Locally | `docker run --rm -p 3000:3000 pakaura-frontend:4.0.0` | Accessible |

### Error Mitigation: Phase 2

| Error | Cause | Solution |
|-------|-------|----------|
| "COPY failed: file not found" | Wrong build context | Verify Dockerfile path and context directory |
| npm install fails | Missing dependencies | Run `npm ci` in frontend/ first |
| pip install fails | Missing system deps | Ensure gcc, libpq-dev in builder stage |
| Image too large (>300MB) | Inefficient build | Check for dev dependencies, use `--only=production` |
| "standalone output not found" | Missing next.config.js setting | Add `output: 'standalone'` |

---

## Phase 3: Kubernetes Manifests

### Objective
Create all Kubernetes resource manifests for deploying the application stack.

### Duration
~30-40 minutes

### Directory Structure to Create
```
infra/
└── kubernetes/
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    ├── postgresql/
    │   ├── statefulset.yaml
    │   ├── service.yaml
    │   └── pvc.yaml
    ├── api/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── migration-job.yaml
    ├── frontend/
    │   ├── deployment.yaml
    │   └── service.yaml
    └── ingress.yaml
```

### Steps

#### Step 3.1: Create Namespace
```yaml
# File: infra/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pakaura
  labels:
    app.kubernetes.io/name: pakaura
    app.kubernetes.io/version: "4.0.0"
    app.kubernetes.io/managed-by: helm
```

#### Step 3.2: Create ConfigMap
```yaml
# File: infra/kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pakaura-config
  namespace: pakaura
  labels:
    app.kubernetes.io/name: pakaura
data:
  # Database
  DB_NAME: "pakaura"
  DB_USER: "pakaura_user"
  DB_HOST: "postgresql"
  DB_PORT: "5432"

  # JWT
  JWT_ALGORITHM: "HS256"
  JWT_EXPIRATION_HOURS: "24"

  # AI Configuration
  AI_MODEL: "command-a-03-2025"
  AI_TEMPERATURE: "0.3"
  AI_MAX_TOKENS: "300"
  AI_TIMEOUT_SECONDS: "30"
  AI_RATE_LIMIT_PER_MINUTE: "30"
  AI_MAX_INPUT_LENGTH: "10000"

  # URLs (internal K8s DNS)
  FRONTEND_URL: "http://frontend:3000"
  API_URL: "http://api:8000"

  # Environment
  ENVIRONMENT: "production"
  DEBUG: "false"
```

#### Step 3.3: Create Secrets (Template)
```yaml
# File: infra/kubernetes/secrets.yaml
# NOTE: In production, use external secret management
# Values should be base64 encoded
apiVersion: v1
kind: Secret
metadata:
  name: pakaura-secrets
  namespace: pakaura
  labels:
    app.kubernetes.io/name: pakaura
type: Opaque
data:
  # Generate: echo -n "your-password" | base64
  DB_PASSWORD: cGFrYXVyYV9wYXNzd29yZA==  # pakaura_password
  JWT_SECRET: c3VwZXItc2VjcmV0LWp3dC1rZXktY2hhbmdlLWluLXByb2R1Y3Rpb24=
  COHERE_API_KEY: ""  # Optional - empty for demo mode
```

#### Step 3.4: Create PostgreSQL StatefulSet
```yaml
# File: infra/kubernetes/postgresql/statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: pakaura
  labels:
    app: postgresql
    app.kubernetes.io/name: pakaura
    app.kubernetes.io/component: database
spec:
  serviceName: postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
        - name: postgresql
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
              name: postgresql
          env:
            - name: POSTGRES_DB
              valueFrom:
                configMapKeyRef:
                  name: pakaura-config
                  key: DB_NAME
            - name: POSTGRES_USER
              valueFrom:
                configMapKeyRef:
                  name: pakaura-config
                  key: DB_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: pakaura-secrets
                  key: DB_PASSWORD
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          readinessProbe:
            exec:
              command:
                - pg_isready
                - -U
                - pakaura_user
                - -d
                - pakaura
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 5
          livenessProbe:
            exec:
              command:
                - pg_isready
                - -U
                - pakaura_user
                - -d
                - pakaura
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
          resources:
            limits:
              memory: "512Mi"
              cpu: "500m"
            requests:
              memory: "256Mi"
              cpu: "250m"
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

#### Step 3.5: Create PostgreSQL Service
```yaml
# File: infra/kubernetes/postgresql/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgresql
  namespace: pakaura
  labels:
    app: postgresql
spec:
  selector:
    app: postgresql
  ports:
    - port: 5432
      targetPort: 5432
      name: postgresql
  clusterIP: None  # Headless service for StatefulSet
```

#### Step 3.6: Create Migration Job
```yaml
# File: infra/kubernetes/api/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  namespace: pakaura
  labels:
    app: migration
spec:
  ttlSecondsAfterFinished: 300
  backoffLimit: 3
  template:
    spec:
      restartPolicy: OnFailure
      initContainers:
        - name: wait-for-db
          image: busybox:1.36
          command:
            - sh
            - -c
            - |
              until nc -z postgresql 5432; do
                echo "Waiting for PostgreSQL..."
                sleep 2
              done
              echo "PostgreSQL is ready!"
      containers:
        - name: migration
          image: pakaura-api:4.0.0
          command:
            - alembic
            - upgrade
            - head
          env:
            - name: DATABASE_URL
              value: "postgresql+asyncpg://$(DB_USER):$(DB_PASSWORD)@postgresql:5432/$(DB_NAME)"
          envFrom:
            - configMapRef:
                name: pakaura-config
            - secretRef:
                name: pakaura-secrets
          resources:
            limits:
              memory: "256Mi"
              cpu: "250m"
            requests:
              memory: "128Mi"
              cpu: "100m"
```

#### Step 3.7: Create API Deployment
```yaml
# File: infra/kubernetes/api/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: pakaura
  labels:
    app: api
    app.kubernetes.io/name: pakaura
    app.kubernetes.io/component: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      initContainers:
        - name: wait-for-db
          image: busybox:1.36
          command:
            - sh
            - -c
            - |
              until nc -z postgresql 5432; do
                echo "Waiting for PostgreSQL..."
                sleep 2
              done
        - name: wait-for-migration
          image: bitnami/kubectl:latest
          command:
            - sh
            - -c
            - |
              kubectl wait --for=condition=complete job/db-migration -n pakaura --timeout=120s || true
      containers:
        - name: api
          image: pakaura-api:4.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: DATABASE_URL
              value: "postgresql+asyncpg://$(DB_USER):$(DB_PASSWORD)@postgresql:5432/$(DB_NAME)"
          envFrom:
            - configMapRef:
                name: pakaura-config
            - secretRef:
                name: pakaura-secrets
          readinessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          resources:
            limits:
              memory: "512Mi"
              cpu: "500m"
            requests:
              memory: "256Mi"
              cpu: "250m"
```

#### Step 3.8: Create API Service
```yaml
# File: infra/kubernetes/api/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: pakaura
  labels:
    app: api
spec:
  selector:
    app: api
  ports:
    - port: 8000
      targetPort: 8000
      name: http
  type: ClusterIP
```

#### Step 3.9: Create Frontend Deployment
```yaml
# File: infra/kubernetes/frontend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: pakaura
  labels:
    app: frontend
    app.kubernetes.io/name: pakaura
    app.kubernetes.io/component: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: pakaura-frontend:4.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 3000
              name: http
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "http://api:8000"
          readinessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
          livenessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
          resources:
            limits:
              memory: "256Mi"
              cpu: "250m"
            requests:
              memory: "128Mi"
              cpu: "100m"
```

#### Step 3.10: Create Frontend Service
```yaml
# File: infra/kubernetes/frontend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: pakaura
  labels:
    app: frontend
spec:
  selector:
    app: frontend
  ports:
    - port: 3000
      targetPort: 3000
      name: http
  type: ClusterIP
```

#### Step 3.11: Create Ingress
```yaml
# File: infra/kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pakaura-ingress
  namespace: pakaura
  labels:
    app.kubernetes.io/name: pakaura
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
spec:
  ingressClassName: nginx
  rules:
    - host: pakaura.local
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
```

#### Step 3.12: Apply Manifests (Manual Testing)
```bash
# Apply in order (for testing before Helm)
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/configmap.yaml
kubectl apply -f infra/kubernetes/secrets.yaml
kubectl apply -f infra/kubernetes/postgresql/
kubectl apply -f infra/kubernetes/api/migration-job.yaml

# Wait for migration
kubectl wait --for=condition=complete job/db-migration -n pakaura --timeout=120s

kubectl apply -f infra/kubernetes/api/deployment.yaml
kubectl apply -f infra/kubernetes/api/service.yaml
kubectl apply -f infra/kubernetes/frontend/
kubectl apply -f infra/kubernetes/ingress.yaml
```

### Validation Checkpoint 3

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Namespace Created | `kubectl get ns pakaura` | Active |
| ConfigMap Created | `kubectl get cm -n pakaura` | pakaura-config |
| Secrets Created | `kubectl get secrets -n pakaura` | pakaura-secrets |
| PostgreSQL Running | `kubectl get pods -n pakaura -l app=postgresql` | 1/1 Running |
| Migration Complete | `kubectl get jobs -n pakaura` | db-migration Complete |
| API Running | `kubectl get pods -n pakaura -l app=api` | 2/2 Running |
| Frontend Running | `kubectl get pods -n pakaura -l app=frontend` | 2/2 Running |
| Ingress Created | `kubectl get ingress -n pakaura` | pakaura-ingress |

### Error Mitigation: Phase 3

| Error | Cause | Solution |
|-------|-------|----------|
| "ImagePullBackOff" | Image not in Minikube | Run `eval $(minikube docker-env)` before building |
| Pod stuck in "Pending" | Insufficient resources | Check `kubectl describe pod` for events |
| "CrashLoopBackOff" | Application error | Check `kubectl logs <pod>` for errors |
| Migration job fails | DB not ready | Increase init container wait time |
| Ingress not working | Addon not enabled | Run `minikube addons enable ingress` |

---

## Phase 4: Helm Chart Creation

### Objective
Package all Kubernetes manifests into a reusable Helm chart with parameterized values.

### Duration
~30-40 minutes

### Directory Structure to Create
```
infra/
└── helm/
    └── pakaura/
        ├── Chart.yaml
        ├── values.yaml
        ├── .helmignore
        └── templates/
            ├── _helpers.tpl
            ├── namespace.yaml
            ├── configmap.yaml
            ├── secrets.yaml
            ├── postgresql/
            │   ├── statefulset.yaml
            │   └── service.yaml
            ├── api/
            │   ├── deployment.yaml
            │   ├── service.yaml
            │   └── migration-job.yaml
            ├── frontend/
            │   ├── deployment.yaml
            │   └── service.yaml
            ├── ingress.yaml
            └── NOTES.txt
```

### Steps

#### Step 4.1: Create Chart.yaml
```yaml
# File: infra/helm/pakaura/Chart.yaml
apiVersion: v2
name: pakaura
description: AI-powered Todo Chatbot - Cloud Native Deployment
type: application
version: 4.0.0
appVersion: "4.0.0"
keywords:
  - todo
  - chatbot
  - ai
  - kubernetes
  - fastapi
  - nextjs
maintainers:
  - name: PakAura Team
    email: team@pakaura.local
```

#### Step 4.2: Create values.yaml
```yaml
# File: infra/helm/pakaura/values.yaml
# Default values for pakaura Helm chart

# Global settings
global:
  namespace: pakaura
  imageTag: "4.0.0"

# Frontend configuration
frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: pakaura-frontend
    tag: ""  # Defaults to global.imageTag
    pullPolicy: IfNotPresent
  resources:
    limits:
      memory: "256Mi"
      cpu: "250m"
    requests:
      memory: "128Mi"
      cpu: "100m"
  service:
    type: ClusterIP
    port: 3000
  probes:
    readiness:
      initialDelaySeconds: 10
      periodSeconds: 5
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10

# API configuration
api:
  enabled: true
  replicaCount: 2
  image:
    repository: pakaura-api
    tag: ""  # Defaults to global.imageTag
    pullPolicy: IfNotPresent
  resources:
    limits:
      memory: "512Mi"
      cpu: "500m"
    requests:
      memory: "256Mi"
      cpu: "250m"
  service:
    type: ClusterIP
    port: 8000
  probes:
    readiness:
      initialDelaySeconds: 10
      periodSeconds: 5
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
  env:
    jwtAlgorithm: "HS256"
    jwtExpirationHours: "24"
    aiModel: "command-a-03-2025"
    aiTemperature: "0.3"
    aiMaxTokens: "300"
    aiTimeoutSeconds: "30"
    aiRateLimitPerMinute: "30"
    environment: "production"
    debug: "false"

# PostgreSQL configuration
postgresql:
  enabled: true
  image:
    repository: postgres
    tag: "16-alpine"
  persistence:
    enabled: true
    size: 10Gi
    storageClass: ""  # Use default
  resources:
    limits:
      memory: "512Mi"
      cpu: "500m"
    requests:
      memory: "256Mi"
      cpu: "250m"
  auth:
    database: pakaura
    username: pakaura_user
    # Password set via --set or external secret

# Migration job
migration:
  enabled: true
  backoffLimit: 3
  ttlSecondsAfterFinished: 300

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hostname: pakaura.local
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"

# Secrets (MUST be set via --set or external management)
secrets:
  jwtSecret: ""      # REQUIRED
  dbPassword: ""     # REQUIRED
  cohereApiKey: ""   # Optional - empty enables demo mode
```

#### Step 4.3: Create _helpers.tpl
```yaml
# File: infra/helm/pakaura/templates/_helpers.tpl
{{/*
Expand the name of the chart.
*/}}
{{- define "pakaura.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "pakaura.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "pakaura.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "pakaura.labels" -}}
helm.sh/chart: {{ include "pakaura.chart" . }}
app.kubernetes.io/name: {{ include "pakaura.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "pakaura.selectorLabels" -}}
app.kubernetes.io/name: {{ include "pakaura.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Get image tag - uses component tag if set, otherwise global tag
*/}}
{{- define "pakaura.imageTag" -}}
{{- .tag | default $.Values.global.imageTag | default $.Chart.AppVersion }}
{{- end }}

{{/*
Database URL construction
*/}}
{{- define "pakaura.databaseUrl" -}}
postgresql+asyncpg://{{ .Values.postgresql.auth.username }}:$(DB_PASSWORD)@postgresql:5432/{{ .Values.postgresql.auth.database }}
{{- end }}
```

#### Step 4.4: Create Templated Manifests

Each manifest from Phase 3 needs to be converted to Helm templates. Here's the API deployment as an example:

```yaml
# File: infra/helm/pakaura/templates/api/deployment.yaml
{{- if .Values.api.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: {{ .Values.global.namespace }}
  labels:
    app: api
    {{- include "pakaura.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.api.replicaCount }}
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      initContainers:
        - name: wait-for-db
          image: busybox:1.36
          command:
            - sh
            - -c
            - |
              until nc -z postgresql 5432; do
                echo "Waiting for PostgreSQL..."
                sleep 2
              done
      containers:
        - name: api
          image: "{{ .Values.api.image.repository }}:{{ .Values.api.image.tag | default .Values.global.imageTag }}"
          imagePullPolicy: {{ .Values.api.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.api.service.port }}
              name: http
          env:
            - name: DATABASE_URL
              value: {{ include "pakaura.databaseUrl" . | quote }}
          envFrom:
            - configMapRef:
                name: pakaura-config
            - secretRef:
                name: pakaura-secrets
          readinessProbe:
            httpGet:
              path: /api/v1/health
              port: {{ .Values.api.service.port }}
            initialDelaySeconds: {{ .Values.api.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.api.probes.readiness.periodSeconds }}
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: {{ .Values.api.service.port }}
            initialDelaySeconds: {{ .Values.api.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.api.probes.liveness.periodSeconds }}
          resources:
            {{- toYaml .Values.api.resources | nindent 12 }}
{{- end }}
```

#### Step 4.5: Create NOTES.txt
```yaml
# File: infra/helm/pakaura/templates/NOTES.txt
=======================================================
  PakAura AI Todo Chatbot - Deployment Complete!
=======================================================

Your application has been deployed successfully.

1. Get the application URL:
{{- if .Values.ingress.enabled }}
   Access via Ingress:
   http://{{ .Values.ingress.hostname }}

   Add to /etc/hosts (or C:\Windows\System32\drivers\etc\hosts):
   $(minikube ip)  {{ .Values.ingress.hostname }}

   Or use minikube tunnel:
   $ minikube tunnel
{{- else }}
   $ kubectl port-forward svc/frontend 3000:3000 -n {{ .Values.global.namespace }}
   Then access: http://localhost:3000
{{- end }}

2. Check pod status:
   $ kubectl get pods -n {{ .Values.global.namespace }}

3. View logs:
   $ kubectl logs -f -l app=api -n {{ .Values.global.namespace }}
   $ kubectl logs -f -l app=frontend -n {{ .Values.global.namespace }}

4. AI Chatbot Features:
   - "Add a task to buy groceries"
   - "Show my tasks"
   - "Complete the grocery task"
   - "Delete my completed tasks"

=======================================================
  Powered by Claude Code - AI-Assisted DevOps
=======================================================
```

#### Step 4.6: Validate Helm Chart
```bash
# Lint the chart
helm lint infra/helm/pakaura

# Dry-run to see generated manifests
helm template pakaura infra/helm/pakaura \
  --set secrets.jwtSecret="test-jwt-secret" \
  --set secrets.dbPassword="test-db-password"

# Verify no errors
helm template pakaura infra/helm/pakaura --debug 2>&1 | head -50
```

### Validation Checkpoint 4

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Chart Valid | `helm lint infra/helm/pakaura` | No errors |
| Template Renders | `helm template pakaura infra/helm/pakaura` | YAML output |
| Values Substituted | Check template output | No `{{ }}` in output |
| NOTES.txt Works | Visible in template output | Instructions shown |

### Error Mitigation: Phase 4

| Error | Cause | Solution |
|-------|-------|----------|
| "template: ... undefined variable" | Missing value in values.yaml | Add default value or check conditional |
| "YAML parse error" | Invalid YAML syntax | Check indentation, use `helm lint` |
| "cannot range over nil" | Empty list in values | Use `{{- if .Values.list }}` guard |
| Values not substituted | Wrong template syntax | Use `{{ .Values.xxx }}` not `$.Values.xxx` |

---

## Phase 5: Deployment & Validation

### Objective
Deploy the complete application using Helm and validate all functionality for demo readiness.

### Duration
~20-30 minutes

### Steps

#### Step 5.1: Create AI-Assisted Deployment Script
```bash
# File: scripts/ai-deploy.sh
#!/bin/bash
# PakAura AI-Assisted Deployment Script
# Generated by Claude Code for Hackathon Demo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║     PakAura AI Todo Chatbot - Kubernetes Deployment       ║"
    echo "║              AI-Assisted by Claude Code                   ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    print_status "Checking prerequisites..."
    local missing=()

    command -v docker >/dev/null 2>&1 || missing+=("docker")
    command -v minikube >/dev/null 2>&1 || missing+=("minikube")
    command -v kubectl >/dev/null 2>&1 || missing+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing+=("helm")

    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing[*]}"
        echo "Please install missing tools and try again."
        exit 1
    fi

    print_success "All prerequisites satisfied"
}

setup_minikube() {
    print_status "Setting up Minikube cluster..."

    if minikube status 2>/dev/null | grep -q "Running"; then
        print_warning "Minikube already running"
    else
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi

    print_status "Enabling required addons..."
    minikube addons enable ingress
    minikube addons enable metrics-server

    print_success "Minikube ready"
}

build_images() {
    print_status "Building Docker images..."

    # Use Minikube's Docker daemon
    eval $(minikube docker-env)

    print_status "Building API image..."
    docker build -t pakaura-api:4.0.0 \
        -f "$PROJECT_ROOT/infra/docker/api.Dockerfile" \
        "$PROJECT_ROOT/api"

    print_status "Building Frontend image..."
    docker build -t pakaura-frontend:4.0.0 \
        -f "$PROJECT_ROOT/infra/docker/frontend.Dockerfile" \
        "$PROJECT_ROOT/frontend"

    print_success "Images built successfully"
    docker images | grep pakaura
}

deploy_helm() {
    print_status "Deploying via Helm..."

    # Generate secrets if not provided
    local jwt_secret="${JWT_SECRET:-$(openssl rand -base64 32)}"
    local db_password="${DB_PASSWORD:-$(openssl rand -base64 16)}"
    local cohere_key="${COHERE_API_KEY:-}"

    helm upgrade --install pakaura "$PROJECT_ROOT/infra/helm/pakaura" \
        --namespace pakaura \
        --create-namespace \
        --set secrets.jwtSecret="$jwt_secret" \
        --set secrets.dbPassword="$db_password" \
        --set secrets.cohereApiKey="$cohere_key" \
        --wait \
        --timeout 5m

    print_success "Helm deployment complete"
}

show_status() {
    echo ""
    print_status "Cluster Status:"
    echo ""

    echo -e "${CYAN}=== Pods ===${NC}"
    kubectl get pods -n pakaura -o wide
    echo ""

    echo -e "${CYAN}=== Services ===${NC}"
    kubectl get services -n pakaura
    echo ""

    echo -e "${CYAN}=== Ingress ===${NC}"
    kubectl get ingress -n pakaura
    echo ""

    print_status "Access URLs:"
    echo "  Frontend: $(minikube service frontend -n pakaura --url 2>/dev/null || echo 'Run: minikube tunnel')"
    echo "  API:      $(minikube service api -n pakaura --url 2>/dev/null || echo 'Run: minikube tunnel')"
}

run_health_check() {
    print_status "Running health checks..."

    local all_healthy=true

    # Check pods
    local pods_ready=$(kubectl get pods -n pakaura -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | tr ' ' '\n' | grep -c "True" || echo 0)
    local pods_total=$(kubectl get pods -n pakaura --no-headers | wc -l)

    if [ "$pods_ready" -eq "$pods_total" ] && [ "$pods_total" -gt 0 ]; then
        print_success "All pods healthy: $pods_ready/$pods_total"
    else
        print_warning "Pods not ready: $pods_ready/$pods_total"
        all_healthy=false
    fi

    # Check API health endpoint
    local api_url=$(minikube service api -n pakaura --url 2>/dev/null)
    if [ -n "$api_url" ]; then
        if curl -sf "$api_url/api/v1/health" > /dev/null 2>&1; then
            print_success "API health check passed"
        else
            print_warning "API health check failed"
            all_healthy=false
        fi
    fi

    if [ "$all_healthy" = true ]; then
        print_success "All health checks passed!"
    else
        print_warning "Some health checks failed. Check logs with: kubectl logs -l app=api -n pakaura"
    fi
}

destroy() {
    print_warning "Destroying all resources..."

    helm uninstall pakaura -n pakaura 2>/dev/null || true
    kubectl delete namespace pakaura 2>/dev/null || true

    print_success "Resources destroyed"
}

show_help() {
    print_banner
    cat << EOF
Usage: $0 [COMMAND]

Commands:
  setup       Full setup: start Minikube, build images, deploy
  build       Build Docker images only
  deploy      Deploy/upgrade via Helm
  status      Show deployment status
  health      Run health checks
  logs        Stream logs (usage: $0 logs [api|frontend|postgresql])
  destroy     Remove all resources
  help        Show this help message

Environment Variables:
  COHERE_API_KEY  - Cohere API key (optional, enables AI features)
  JWT_SECRET      - JWT signing key (auto-generated if not set)
  DB_PASSWORD     - Database password (auto-generated if not set)

Examples:
  $0 setup                          # Full setup from scratch
  COHERE_API_KEY=xxx $0 deploy      # Deploy with AI features
  $0 logs api                       # Stream API logs
  $0 destroy                        # Clean up everything

EOF
}

main() {
    print_banner

    case "${1:-help}" in
        setup)
            check_prerequisites
            setup_minikube
            build_images
            deploy_helm
            show_status
            run_health_check
            ;;
        build)
            check_prerequisites
            build_images
            ;;
        deploy)
            check_prerequisites
            deploy_helm
            show_status
            ;;
        status)
            show_status
            ;;
        health)
            run_health_check
            ;;
        logs)
            local service="${2:-api}"
            kubectl logs -f -l "app=$service" -n pakaura --all-containers
            ;;
        destroy)
            destroy
            ;;
        help|*)
            show_help
            ;;
    esac
}

main "$@"
```

#### Step 5.2: Deploy the Application
```bash
# Make script executable
chmod +x scripts/ai-deploy.sh

# Run full setup
./scripts/ai-deploy.sh setup

# Or with Cohere API key for full AI features
COHERE_API_KEY=your-api-key ./scripts/ai-deploy.sh setup
```

#### Step 5.3: Access the Application
```bash
# Option 1: Use minikube service (recommended for demo)
minikube service frontend -n pakaura

# Option 2: Use minikube tunnel for ingress
minikube tunnel
# Then access: http://pakaura.local (add to /etc/hosts first)

# Option 3: Port forwarding
kubectl port-forward svc/frontend 3000:3000 -n pakaura
kubectl port-forward svc/api 8000:8000 -n pakaura
# Access: http://localhost:3000
```

#### Step 5.4: End-to-End Validation
```bash
# 1. Verify all pods are running
kubectl get pods -n pakaura
# Expected: 5 pods (postgresql-0, api-xxx, api-yyy, frontend-xxx, frontend-yyy)

# 2. Test API health
curl http://$(minikube service api -n pakaura --url)/api/v1/health
# Expected: {"status":"healthy","version":"3.0.0"}

# 3. Test self-healing
kubectl delete pod -l app=api -n pakaura --wait=false
kubectl get pods -n pakaura -w
# Expected: New pods created within 30 seconds

# 4. Test data persistence
# Create a task via the UI or API
# Delete PostgreSQL pod
kubectl delete pod postgresql-0 -n pakaura
# Wait for pod to restart
kubectl wait --for=condition=ready pod/postgresql-0 -n pakaura --timeout=120s
# Verify task still exists

# 5. View Helm release
helm list -n pakaura
helm status pakaura -n pakaura
```

### Validation Checkpoint 5 (Final)

| Check | Command | Expected Result |
|-------|---------|-----------------|
| All Pods Running | `kubectl get pods -n pakaura` | 5/5 Running |
| API Healthy | `curl <api-url>/api/v1/health` | 200 OK |
| Frontend Accessible | Browser test | Login page loads |
| AI Chatbot Works | Test in UI | Responds to commands |
| Self-Healing | Delete pod, watch recreation | New pod in <60s |
| Data Persists | Delete DB pod, verify data | Tasks preserved |
| Helm Release | `helm list -n pakaura` | pakaura deployed |

### Error Mitigation: Phase 5

| Error | Cause | Solution |
|-------|-------|----------|
| "ImagePullBackOff" | Image not found | Rebuild with `eval $(minikube docker-env)` |
| "CrashLoopBackOff" | App crash | Check `kubectl logs <pod>` |
| Frontend can't reach API | CORS or URL issue | Verify `NEXT_PUBLIC_API_URL` |
| Ingress 404 | Path routing issue | Check ingress rules |
| DB connection refused | PostgreSQL not ready | Wait for StatefulSet |

---

## Demo Workflow for Hackathon

### 5-Minute Quick Demo Script

```bash
# 1. Start fresh (if needed)
./scripts/ai-deploy.sh destroy

# 2. Full deployment (show this to judges)
./scripts/ai-deploy.sh setup

# 3. Show cluster status
kubectl get all -n pakaura

# 4. Access application
minikube service frontend -n pakaura

# 5. Demo AI chatbot
# - Register/login
# - "Add a task to present at hackathon"
# - "Show my tasks"
# - "Complete the hackathon task"

# 6. Demo self-healing
kubectl delete pod -l app=api -n pakaura
kubectl get pods -n pakaura -w  # Watch new pod creation

# 7. Show Helm release
helm list -n pakaura
```

### Talking Points for Judges

1. **Cloud-Native Architecture**: "We deployed a full-stack AI application to Kubernetes with proper separation of concerns—frontend, backend, and database are independently scalable."

2. **AI-Assisted DevOps**: "All deployment scripts, Dockerfiles, and Helm charts were generated by Claude Code, demonstrating AI-assisted infrastructure as code."

3. **Production Patterns**: "We implemented ConfigMaps for configuration, Secrets for sensitive data, health probes for self-healing, and persistent volumes for data durability."

4. **One-Command Deployment**: "The entire application deploys with a single command: `./scripts/ai-deploy.sh setup`"

5. **Reproducibility**: "Using Helm ensures that this deployment is version-controlled, parameterized, and reproducible across environments."

---

## Appendix: Quick Reference

### Common Commands

```bash
# Deployment
./scripts/ai-deploy.sh setup      # Full setup
./scripts/ai-deploy.sh deploy     # Deploy only
./scripts/ai-deploy.sh destroy    # Cleanup

# Monitoring
kubectl get pods -n pakaura -w    # Watch pods
kubectl logs -f -l app=api -n pakaura
kubectl describe pod <name> -n pakaura

# Troubleshooting
kubectl exec -it <pod> -n pakaura -- /bin/sh
kubectl get events -n pakaura --sort-by='.lastTimestamp'

# Helm
helm list -n pakaura
helm history pakaura -n pakaura
helm rollback pakaura 1 -n pakaura
```

### File Structure Summary

```
infra/
├── docker/
│   ├── api.Dockerfile
│   └── frontend.Dockerfile
├── kubernetes/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── postgresql/
│   ├── api/
│   ├── frontend/
│   └── ingress.yaml
└── helm/
    └── pakaura/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/

scripts/
└── ai-deploy.sh
```

---

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| No manual coding by user | ✅ PASS | All code AI-generated |
| AI-assisted workflow | ✅ PASS | Claude Code generates all artifacts |
| Production-like but local | ✅ PASS | Uses Minikube with production patterns |
| Hackathon-judging friendly | ✅ PASS | One-command deploy, clear demo script |
| Reproducible | ✅ PASS | Helm chart ensures repeatability |
| Demo-ready | ✅ PASS | All validation steps included |

---

*Plan generated by Claude Code - AI-Assisted Cloud-Native Architect*
*Version: 4.0.0 | Date: 2026-01-18*

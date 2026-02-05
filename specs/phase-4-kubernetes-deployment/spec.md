# Phase IV: Cloud-Native Kubernetes Deployment

## Feature Overview

**Feature Name**: Cloud-Native AI Todo Chatbot - Local Kubernetes Deployment
**Version**: 4.0.0
**Status**: Draft
**Created**: 2026-01-18
**Branch**: `002-kubernetes-deployment`
**Input**: Deploy Phase III AI-powered Todo Chatbot to local Kubernetes (Minikube)

---

## Executive Summary

Phase IV transforms the existing AI-powered Todo Chatbot application into a production-grade, cloud-native deployment running on a local Kubernetes cluster using Minikube. This phase focuses exclusively on infrastructure, containerization, orchestration, and AI-assisted DevOps tooling—**no application code changes required**.

### Key Deliverables
1. Production-ready Docker images for all services
2. Kubernetes manifests for complete deployment
3. Helm chart for parameterized, repeatable deployments
4. AI-assisted DevOps automation scripts
5. Comprehensive documentation for hackathon demonstration

---

## Problem Statement

The Phase III application runs via Docker Compose, which is suitable for local development but lacks:
- **Orchestration**: No self-healing, rolling updates, or resource management
- **Scalability**: Cannot scale individual services independently
- **Cloud-Native Patterns**: Missing ConfigMaps, Secrets, health probes, resource limits
- **Production Readiness**: No ingress, service discovery, or proper networking
- **Reproducibility**: Docker Compose lacks the declarative, version-controlled infrastructure of Kubernetes

### Business Context
For the hackathon, judges expect to see:
- Cloud-native architecture demonstrated locally
- Professional deployment practices
- AI-assisted automation throughout the DevOps pipeline
- Reproducible, one-command deployment

---

## Solution Overview

Deploy the complete application stack to Minikube using Kubernetes best practices:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MINIKUBE CLUSTER                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         NAMESPACE: pakaura                            │  │
│  │                                                                       │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐   │  │
│  │  │   INGRESS   │    │  ConfigMap  │    │        Secrets          │   │  │
│  │  │  (nginx)    │    │  (app-cfg)  │    │ (db-creds, jwt, cohere) │   │  │
│  │  └──────┬──────┘    └─────────────┘    └─────────────────────────┘   │  │
│  │         │                                                             │  │
│  │         ▼                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                        SERVICES (ClusterIP)                     │  │  │
│  │  │  ┌───────────┐    ┌───────────┐    ┌───────────────────────┐   │  │  │
│  │  │  │ frontend  │    │    api    │    │      postgresql       │   │  │  │
│  │  │  │  :3000    │    │   :8000   │    │        :5432          │   │  │  │
│  │  │  └─────┬─────┘    └─────┬─────┘    └───────────┬───────────┘   │  │  │
│  │  └────────┼────────────────┼──────────────────────┼───────────────┘  │  │
│  │           │                │                      │                   │  │
│  │           ▼                ▼                      ▼                   │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                      DEPLOYMENTS / STATEFULSETS                 │  │  │
│  │  │                                                                 │  │  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │  │  │
│  │  │  │   frontend      │  │      api        │  │   postgresql    │  │  │  │
│  │  │  │   Deployment    │  │   Deployment    │  │  StatefulSet    │  │  │  │
│  │  │  │   replicas: 2   │  │   replicas: 2   │  │   replicas: 1   │  │  │  │
│  │  │  │                 │  │                 │  │                 │  │  │  │
│  │  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  │  │
│  │  │  │  │  Pod 1    │  │  │  │  Pod 1    │  │  │  │  Pod 0    │  │  │  │  │
│  │  │  │  │  Next.js  │  │  │  │  FastAPI  │  │  │  │  PG 16    │  │  │  │  │
│  │  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │  │  │  │
│  │  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │       │         │  │  │  │
│  │  │  │  │  Pod 2    │  │  │  │  Pod 2    │  │  │       ▼         │  │  │  │
│  │  │  │  │  Next.js  │  │  │  │  FastAPI  │  │  │  ┌─────────┐   │  │  │  │
│  │  │  │  └───────────┘  │  │  └───────────┘  │  │  │   PVC   │   │  │  │  │
│  │  │  └─────────────────┘  └─────────────────┘  │  │  (10Gi) │   │  │  │  │
│  │  │                                            │  └─────────┘   │  │  │  │
│  │  │                                            └─────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │   LOCAL HOST    │
                            │                 │
                            │  http://pakaura │
                            │     .local      │
                            └─────────────────┘
```

---

## User Scenarios & Testing

### User Story 1 - One-Command Deployment (Priority: P1)

As a **hackathon judge or developer**, I want to deploy the entire application with a single command so that I can quickly evaluate the cloud-native architecture.

**Why this priority**: This is the primary demonstration scenario. Judges have limited time and need immediate, reliable deployment.

**Independent Test**: Run `helm install pakaura ./helm/pakaura` and verify all services are accessible within 3 minutes.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster with ingress enabled, **When** I run `helm install pakaura ./helm/pakaura`, **Then** all pods reach Running status within 3 minutes.

2. **Given** a deployed application, **When** I run `minikube service frontend --url`, **Then** the application is accessible in my browser.

3. **Given** a deployed application, **When** I interact with the AI chatbot, **Then** I can create, list, complete, and delete tasks via natural language.

---

### User Story 2 - Health Monitoring & Self-Healing (Priority: P2)

As a **DevOps engineer**, I want Kubernetes to automatically restart unhealthy pods so that the application maintains high availability.

**Why this priority**: Demonstrates production-grade resilience expected in cloud-native applications.

**Independent Test**: Delete a running pod and verify Kubernetes recreates it automatically.

**Acceptance Scenarios**:

1. **Given** a running API pod, **When** I run `kubectl delete pod api-xxx`, **Then** a new pod is created within 30 seconds.

2. **Given** a running application, **When** a health probe fails, **Then** the pod is restarted automatically.

3. **Given** database connectivity issues, **When** the API pod cannot reach PostgreSQL, **Then** the readiness probe fails and traffic is not routed to that pod.

---

### User Story 3 - Configuration Management (Priority: P2)

As a **developer**, I want environment-specific configuration managed through Kubernetes ConfigMaps and Secrets so that sensitive data is secured and configuration is centralized.

**Why this priority**: Demonstrates proper secret management and twelve-factor app principles.

**Independent Test**: Verify Secrets are base64-encoded and not exposed in pod specs.

**Acceptance Scenarios**:

1. **Given** the deployed application, **When** I inspect the API deployment, **Then** all sensitive values (DB password, JWT secret, Cohere API key) come from Secrets.

2. **Given** configuration changes needed, **When** I update a ConfigMap and restart pods, **Then** the application uses the new configuration.

---

### User Story 4 - Persistent Data Storage (Priority: P1)

As a **user**, I want my tasks and conversation history to persist across pod restarts so that I don't lose my data.

**Why this priority**: Data persistence is critical for a functional demo.

**Independent Test**: Create tasks, delete all pods, verify tasks exist after pods restart.

**Acceptance Scenarios**:

1. **Given** I have created tasks in the application, **When** the PostgreSQL pod restarts, **Then** my tasks are still available.

2. **Given** a conversation history, **When** I delete and redeploy the application, **Then** the conversation history is preserved.

---

### User Story 5 - AI-Assisted Deployment Automation (Priority: P3)

As a **developer**, I want AI-generated scripts to automate common DevOps tasks so that I can focus on development rather than infrastructure.

**Why this priority**: Demonstrates AI-assisted DevOps, a key hackathon theme.

**Independent Test**: Run `./scripts/ai-deploy.sh` and verify it handles the complete deployment workflow.

**Acceptance Scenarios**:

1. **Given** the AI deployment script, **When** I run it with `--setup`, **Then** it initializes Minikube, enables addons, and deploys the application.

2. **Given** a deployed application, **When** I run the script with `--status`, **Then** it displays health of all services using AI-formatted output.

---

### Edge Cases

- **What happens when** Minikube runs out of resources? → Resource limits prevent OOM, pods are evicted gracefully.
- **What happens when** the Cohere API key is invalid? → Application falls back to demo mode (keyword-based responses).
- **What happens when** PostgreSQL is unavailable during startup? → API pods fail readiness probes and retry with exponential backoff.
- **What happens when** ingress controller is not enabled? → Helm chart pre-install hook checks and provides clear error message.

---

## Requirements

### Functional Requirements

#### FR-001: Container Images
- **FR-001.1**: System MUST build optimized Docker images for frontend (Next.js standalone)
- **FR-001.2**: System MUST build optimized Docker images for backend (Python 3.11 slim)
- **FR-001.3**: System MUST use multi-stage builds to minimize image size
- **FR-001.4**: System MUST tag images with semantic versioning (e.g., `pakaura-api:4.0.0`)

#### FR-002: Kubernetes Resources
- **FR-002.1**: System MUST deploy frontend as a Deployment with 2 replicas
- **FR-002.2**: System MUST deploy API backend as a Deployment with 2 replicas
- **FR-002.3**: System MUST deploy PostgreSQL as a StatefulSet with 1 replica
- **FR-002.4**: System MUST use PersistentVolumeClaim (10Gi) for PostgreSQL data
- **FR-002.5**: System MUST expose services via ClusterIP (internal) and Ingress (external)

#### FR-003: Configuration & Secrets
- **FR-003.1**: System MUST store non-sensitive configuration in ConfigMaps
- **FR-003.2**: System MUST store sensitive data (DB password, JWT secret, API keys) in Secrets
- **FR-003.3**: System MUST inject configuration via environment variables (not files)
- **FR-003.4**: System MUST support Cohere API key as optional (demo mode fallback)

#### FR-004: Health & Readiness
- **FR-004.1**: API pods MUST have liveness probe at `/api/v1/health`
- **FR-004.2**: API pods MUST have readiness probe verifying database connectivity
- **FR-004.3**: Frontend pods MUST have liveness probe at `/`
- **FR-004.4**: PostgreSQL pods MUST have readiness probe via `pg_isready`

#### FR-005: Networking
- **FR-005.1**: System MUST use Ingress with nginx controller for external access
- **FR-005.2**: System MUST support custom hostname (default: `pakaura.local`)
- **FR-005.3**: System MUST configure CORS to allow frontend-to-API communication
- **FR-005.4**: System MUST use internal DNS for service discovery (e.g., `postgresql.pakaura.svc.cluster.local`)

#### FR-006: Database Migrations
- **FR-006.1**: System MUST run Alembic migrations as a Kubernetes Job before API startup
- **FR-006.2**: Migration Job MUST wait for PostgreSQL readiness
- **FR-006.3**: Migration Job MUST be idempotent (safe to re-run)

#### FR-007: Helm Chart
- **FR-007.1**: System MUST provide Helm chart for parameterized deployment
- **FR-007.2**: Helm chart MUST support value overrides for all configurable options
- **FR-007.3**: Helm chart MUST include hooks for pre-install validation and migration
- **FR-007.4**: Helm chart MUST generate release notes on install

### Key Entities

- **Deployment**: Manages stateless pods (frontend, API)
- **StatefulSet**: Manages stateful pods (PostgreSQL) with stable network identity
- **Service**: Exposes pods within cluster (ClusterIP) or externally (NodePort/Ingress)
- **ConfigMap**: Non-sensitive configuration data
- **Secret**: Sensitive configuration (passwords, tokens, API keys)
- **PersistentVolumeClaim**: Storage request for database data
- **Ingress**: HTTP(S) routing from external traffic to services
- **Job**: One-time tasks (database migrations)
- **HorizontalPodAutoscaler**: (Optional) Auto-scaling based on metrics

---

## Technical Architecture

### Component Overview

| Component | Type | Replicas | Image | Resources |
|-----------|------|----------|-------|-----------|
| Frontend | Deployment | 2 | `pakaura-frontend:4.0.0` | 256Mi RAM, 0.25 CPU |
| API | Deployment | 2 | `pakaura-api:4.0.0` | 512Mi RAM, 0.5 CPU |
| PostgreSQL | StatefulSet | 1 | `postgres:16-alpine` | 512Mi RAM, 0.5 CPU |
| Migration | Job | 1 | `pakaura-api:4.0.0` | 256Mi RAM, 0.25 CPU |

### Directory Structure

```
infra/
├── docker/
│   ├── api.Dockerfile           # Optimized FastAPI image
│   └── frontend.Dockerfile      # Optimized Next.js image
├── kubernetes/
│   ├── namespace.yaml           # pakaura namespace
│   ├── configmap.yaml           # Application configuration
│   ├── secrets.yaml             # Sensitive data (template)
│   ├── postgresql/
│   │   ├── statefulset.yaml     # PostgreSQL StatefulSet
│   │   ├── service.yaml         # PostgreSQL Service
│   │   └── pvc.yaml             # Persistent Volume Claim
│   ├── api/
│   │   ├── deployment.yaml      # FastAPI Deployment
│   │   ├── service.yaml         # API Service
│   │   └── migration-job.yaml   # Alembic migration Job
│   ├── frontend/
│   │   ├── deployment.yaml      # Next.js Deployment
│   │   └── service.yaml         # Frontend Service
│   └── ingress.yaml             # Nginx Ingress
└── helm/
    └── pakaura/
        ├── Chart.yaml           # Helm chart metadata
        ├── values.yaml          # Default configuration values
        ├── values-dev.yaml      # Development overrides
        ├── templates/
        │   ├── _helpers.tpl     # Template helpers
        │   ├── namespace.yaml
        │   ├── configmap.yaml
        │   ├── secrets.yaml
        │   ├── postgresql/
        │   │   ├── statefulset.yaml
        │   │   ├── service.yaml
        │   │   └── pvc.yaml
        │   ├── api/
        │   │   ├── deployment.yaml
        │   │   ├── service.yaml
        │   │   └── migration-job.yaml
        │   ├── frontend/
        │   │   ├── deployment.yaml
        │   │   └── service.yaml
        │   ├── ingress.yaml
        │   └── NOTES.txt        # Post-install instructions
        └── .helmignore

scripts/
├── ai-deploy.sh                 # AI-assisted deployment script
├── build-images.sh              # Docker image builder
├── minikube-setup.sh            # Minikube initialization
└── health-check.sh              # Service health verification
```

### Helm Chart Configuration (values.yaml)

```yaml
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

# API configuration
api:
  enabled: true
  replicaCount: 2
  image:
    repository: pakaura-api
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
  env:
    aiModel: "command-a-03-2025"
    aiTemperature: "0.3"
    aiMaxTokens: "300"
    aiTimeoutSeconds: "30"
    jwtExpirationHours: "24"

# PostgreSQL configuration
postgresql:
  enabled: true
  image:
    repository: postgres
    tag: "16-alpine"
  persistence:
    enabled: true
    size: 10Gi
    storageClass: standard
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
    # Password should be set via --set or secrets

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hostname: pakaura.local
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"

# Secrets (override via --set or external secret management)
secrets:
  jwtSecret: ""           # MUST be set
  dbPassword: ""          # MUST be set
  cohereApiKey: ""        # Optional (demo mode if empty)
```

---

## Containerization Strategy

### API Dockerfile (Optimized)

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser alembic.ini .

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile (Optimized)

```dockerfile
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

ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

### Image Size Targets

| Image | Target Size | Optimization |
|-------|-------------|--------------|
| `pakaura-api` | < 250MB | Multi-stage, slim base, no dev deps |
| `pakaura-frontend` | < 150MB | Standalone mode, alpine base |
| `postgres:16-alpine` | ~240MB | Official alpine image |

---

## Kubernetes Deployment Strategy

### Deployment Order (Dependencies)

```
1. Namespace
   └── 2. Secrets & ConfigMaps
       └── 3. PostgreSQL (StatefulSet + Service + PVC)
           └── 4. Migration Job (waits for PostgreSQL)
               └── 5. API (Deployment + Service)
                   └── 6. Frontend (Deployment + Service)
                       └── 7. Ingress
```

### Resource Manifests

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pakaura
  labels:
    app.kubernetes.io/name: pakaura
    app.kubernetes.io/version: "4.0.0"
```

#### PostgreSQL StatefulSet
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: pakaura
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
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "$(POSTGRES_USER)", "-d", "$(POSTGRES_DB)"]
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            exec:
              command: ["pg_isready", "-U", "$(POSTGRES_USER)", "-d", "$(POSTGRES_DB)"]
            initialDelaySeconds: 30
            periodSeconds: 10
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

#### API Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: pakaura
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
          command: ['sh', '-c', 'until nc -z postgresql 5432; do echo waiting for postgresql; sleep 2; done']
      containers:
        - name: api
          image: pakaura-api:4.0.0
          ports:
            - containerPort: 8000
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
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          resources:
            limits:
              memory: "512Mi"
              cpu: "500m"
            requests:
              memory: "256Mi"
              cpu: "250m"
```

---

## AI-Assisted DevOps Tooling

### Overview

All deployment automation is AI-assisted, meaning Claude Code generates and maintains the scripts based on natural language requirements.

### AI Deployment Script (`ai-deploy.sh`)

```bash
#!/bin/bash
# AI-Assisted Deployment Script for PakAura
# Generated and maintained by Claude Code

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# AI-generated help text
show_help() {
    cat << EOF
PakAura AI-Assisted Deployment Tool v4.0.0

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  setup       Initialize Minikube and deploy application
  deploy      Deploy or upgrade application via Helm
  status      Show health status of all services
  logs        Stream logs from specified service
  destroy     Remove all resources
  help        Show this help message

Options:
  --namespace    Kubernetes namespace (default: pakaura)
  --values       Path to custom values file
  --dry-run      Preview changes without applying

Examples:
  $0 setup                    # Full setup from scratch
  $0 deploy --values prod.yaml
  $0 status
  $0 logs api
  $0 destroy

AI-Generated by Claude Code for Hackathon demonstration.
EOF
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    local missing=()
    command -v docker >/dev/null 2>&1 || missing+=("docker")
    command -v minikube >/dev/null 2>&1 || missing+=("minikube")
    command -v kubectl >/dev/null 2>&1 || missing+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing+=("helm")

    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing[*]}"
        exit 1
    fi

    print_success "All prerequisites satisfied"
}

# Setup Minikube
setup_minikube() {
    print_status "Setting up Minikube..."

    if minikube status | grep -q "Running"; then
        print_warning "Minikube already running"
    else
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi

    # Enable required addons
    minikube addons enable ingress
    minikube addons enable metrics-server

    # Configure Docker to use Minikube's daemon
    eval $(minikube docker-env)

    print_success "Minikube ready"
}

# Build images
build_images() {
    print_status "Building Docker images..."

    eval $(minikube docker-env)

    docker build -t pakaura-api:4.0.0 -f "$PROJECT_ROOT/infra/docker/api.Dockerfile" "$PROJECT_ROOT/api"
    docker build -t pakaura-frontend:4.0.0 -f "$PROJECT_ROOT/infra/docker/frontend.Dockerfile" "$PROJECT_ROOT/frontend"

    print_success "Images built successfully"
}

# Deploy via Helm
deploy_helm() {
    local values_file="${1:-$PROJECT_ROOT/infra/helm/pakaura/values.yaml}"

    print_status "Deploying via Helm..."

    helm upgrade --install pakaura "$PROJECT_ROOT/infra/helm/pakaura" \
        --namespace pakaura \
        --create-namespace \
        --values "$values_file" \
        --set secrets.jwtSecret="$(openssl rand -base64 32)" \
        --set secrets.dbPassword="$(openssl rand -base64 16)" \
        --wait \
        --timeout 5m

    print_success "Deployment complete!"
}

# Show status
show_status() {
    print_status "Service Status:"

    echo ""
    kubectl get pods -n pakaura -o wide
    echo ""
    kubectl get services -n pakaura
    echo ""
    kubectl get ingress -n pakaura

    echo ""
    print_status "Access URL:"
    minikube service frontend -n pakaura --url 2>/dev/null || echo "Run: minikube tunnel"
}

# Main entry point
main() {
    case "${1:-help}" in
        setup)
            check_prerequisites
            setup_minikube
            build_images
            deploy_helm "${2:-}"
            show_status
            ;;
        deploy)
            check_prerequisites
            build_images
            deploy_helm "${2:-}"
            ;;
        status)
            show_status
            ;;
        logs)
            kubectl logs -f -l "app=${2:-api}" -n pakaura
            ;;
        destroy)
            print_warning "Destroying all resources..."
            helm uninstall pakaura -n pakaura 2>/dev/null || true
            kubectl delete namespace pakaura 2>/dev/null || true
            print_success "Resources destroyed"
            ;;
        help|*)
            show_help
            ;;
    esac
}

main "$@"
```

### AI-Assisted Capabilities

| Capability | Description | AI Contribution |
|------------|-------------|-----------------|
| Script Generation | Complete deployment scripts | Generated from spec requirements |
| Error Messages | User-friendly error handling | AI-crafted contextual help |
| Status Reporting | Formatted health dashboards | AI-designed output format |
| Documentation | Inline help and comments | Comprehensive AI-written docs |
| Troubleshooting | Common issue detection | AI-suggested fixes |

---

## Non-Functional Requirements

### NFR-001: Reproducibility
- **Requirement**: Deployment MUST be fully reproducible from a clean state
- **Metric**: `helm install` produces identical results every time
- **Verification**: Script includes idempotency checks

### NFR-002: Demo-Ready
- **Requirement**: Application MUST be fully functional within 5 minutes of deployment
- **Metric**: All pods Running, ingress accessible, AI chatbot responsive
- **Verification**: Automated health check script validates end-to-end

### NFR-003: Stability
- **Requirement**: Application MUST remain stable under normal demo conditions
- **Metric**: No pod restarts during 30-minute demo window
- **Verification**: Resource limits prevent OOM, health probes ensure recovery

### NFR-004: Resource Efficiency
- **Requirement**: Total cluster resource usage MUST fit within 8GB RAM, 4 CPU cores
- **Metric**: Verified via `kubectl top nodes`
- **Verification**: Resource requests/limits enforce boundaries

### NFR-005: Security
- **Requirement**: No secrets exposed in manifests, logs, or pod specs
- **Metric**: All sensitive data in Kubernetes Secrets, base64-encoded
- **Verification**: `kubectl get secret -o yaml` shows encoded values only

### NFR-006: Observability
- **Requirement**: Ability to view logs and pod status for all services
- **Metric**: `kubectl logs` and `kubectl describe` work for all pods
- **Verification**: AI deployment script includes status command

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Complete deployment via `helm install` succeeds in < 5 minutes
- **SC-002**: All pods (frontend×2, api×2, postgresql×1) reach Running status
- **SC-003**: Ingress provides external access to the application
- **SC-004**: AI chatbot responds to natural language task commands
- **SC-005**: Data persists across pod restarts (PostgreSQL PVC)
- **SC-006**: Self-healing: deleted pod is recreated within 60 seconds
- **SC-007**: Zero hardcoded secrets in version control

### Demonstration Checklist

- [ ] One-command setup: `./scripts/ai-deploy.sh setup`
- [ ] Application accessible via browser
- [ ] Create task via AI chatbot: "Add a task to demo Kubernetes"
- [ ] List tasks: "Show my tasks"
- [ ] Complete task: "Mark demo Kubernetes as done"
- [ ] Delete API pod, verify recreation
- [ ] Show `kubectl get pods` with all Running
- [ ] Show Helm release: `helm list -n pakaura`

---

## Out of Scope

- Cloud provider deployments (AWS EKS, GCP GKE, Azure AKS)
- TLS/SSL certificate management
- External secret management (Vault, AWS Secrets Manager)
- CI/CD pipeline integration
- Production-grade monitoring (Prometheus, Grafana)
- Log aggregation (ELK stack, Loki)
- Service mesh (Istio, Linkerd)
- GitOps (ArgoCD, Flux)
- Horizontal Pod Autoscaling
- Network policies
- Pod disruption budgets

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Minikube resource constraints | Demo failure | Medium | Document minimum requirements, test on target hardware |
| Docker image build failures | Blocked deployment | Low | Use multi-stage builds with caching, test locally first |
| Database migration failures | Data inconsistency | Low | Idempotent migrations, pre-deployment backup |
| Ingress not accessible | Demo blocked | Medium | Fallback to NodePort, document `minikube tunnel` |
| Cohere API unavailable | AI features degraded | Low | Demo mode fallback works without API key |

---

## Dependencies

### Required Tools

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Docker | 24.0+ | Container runtime |
| Minikube | 1.32+ | Local Kubernetes cluster |
| kubectl | 1.29+ | Kubernetes CLI |
| Helm | 3.14+ | Package manager |

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 6 cores |
| RAM | 8 GB | 12 GB |
| Disk | 20 GB | 40 GB |
| OS | Windows 10+, macOS 12+, Linux (kernel 5.4+) | Same |

---

## Acceptance Criteria

### Infrastructure
- [ ] Optimized Dockerfiles for API and Frontend
- [ ] Kubernetes manifests for all components
- [ ] Helm chart with parameterized values
- [ ] AI-assisted deployment scripts

### Deployment
- [ ] One-command deployment works from clean state
- [ ] All pods reach Running status within 5 minutes
- [ ] PostgreSQL data persists across restarts
- [ ] Ingress routes traffic correctly

### Verification
- [ ] Health probes configured and working
- [ ] Secrets not exposed in manifests or logs
- [ ] Resource limits prevent resource exhaustion
- [ ] Self-healing verified (pod deletion/recreation)

### Documentation
- [ ] README with quick start instructions
- [ ] Helm values documented
- [ ] Troubleshooting guide included

---

## Appendix A: Quick Reference Commands

```bash
# Setup & Deploy
./scripts/ai-deploy.sh setup

# Check Status
kubectl get all -n pakaura
kubectl get pods -n pakaura -w
helm list -n pakaura

# Access Application
minikube service frontend -n pakaura --url
# Or: minikube tunnel (then access via ingress hostname)

# View Logs
kubectl logs -f -l app=api -n pakaura
kubectl logs -f -l app=frontend -n pakaura

# Debug
kubectl describe pod <pod-name> -n pakaura
kubectl exec -it <pod-name> -n pakaura -- /bin/sh

# Cleanup
helm uninstall pakaura -n pakaura
minikube delete
```

---

## Appendix B: Environment Variables Reference

| Variable | Component | Source | Description |
|----------|-----------|--------|-------------|
| `DATABASE_URL` | API | ConfigMap+Secret | PostgreSQL connection string |
| `JWT_SECRET` | API | Secret | JWT signing key |
| `JWT_ALGORITHM` | API | ConfigMap | HS256 |
| `JWT_EXPIRATION_HOURS` | API | ConfigMap | 24 |
| `FRONTEND_URL` | API | ConfigMap | CORS origin |
| `COHERE_API_KEY` | API | Secret | AI API key (optional) |
| `AI_MODEL` | API | ConfigMap | command-a-03-2025 |
| `AI_TEMPERATURE` | API | ConfigMap | 0.3 |
| `NEXT_PUBLIC_API_URL` | Frontend | ConfigMap | Backend URL |
| `POSTGRES_DB` | PostgreSQL | ConfigMap | Database name |
| `POSTGRES_USER` | PostgreSQL | ConfigMap | Database user |
| `POSTGRES_PASSWORD` | PostgreSQL | Secret | Database password |

---

*Document generated by Claude Code - AI-Assisted Cloud-Native Architect*
*Version: 4.0.0 | Date: 2026-01-18*

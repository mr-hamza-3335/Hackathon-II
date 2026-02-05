# Tasks: Phase IV Kubernetes Deployment

**Input**: Design documents from `specs/phase-4-kubernetes-deployment/`
**Prerequisites**: spec.md (required), plan.md (required)
**Branch**: `002-kubernetes-deployment`
**Date**: 2026-01-18

---

## Task Format Legend

| Symbol | Meaning |
|--------|---------|
| `[P]` | Can run in parallel (no dependencies) |
| `[US#]` | User Story reference (US1=One-Command Deploy, US2=Self-Healing, etc.) |
| `[BLOCK]` | Blocking task - must complete before dependent tasks |

## AI-Assisted Tool Reference

| Tool Label | Actual Tool | Purpose |
|------------|-------------|---------|
| **Claude Code** | AI Assistant | Generates files, scripts, troubleshoots |
| **Docker** | Container CLI | Build/manage images |
| **Minikube** | Local K8s | Cluster management |
| **kubectl** | K8s CLI | Resource management |
| **Helm** | Package Manager | Chart deployment |

---

## Phase 1: Environment Setup (Foundation)

**Purpose**: Prepare local environment with required tools and running Minikube cluster
**Duration**: ~15-20 minutes
**User Stories Supported**: All (US1-US5)

### Tasks

---

#### T001 [BLOCK] Verify Prerequisites Installation

| Attribute | Value |
|-----------|-------|
| **Task Name** | Verify Prerequisites Installation |
| **Description** | Check that Docker, Minikube, kubectl, and Helm are installed with correct versions |
| **Tool Used** | Claude Code (generates verification script) |
| **Files Created** | `scripts/check-prerequisites.sh` |
| **Expected Output** | All tools report correct versions |
| **Validation Command** | `docker --version && minikube version && kubectl version --client && helm version` |

**Acceptance Criteria**:
- [ ] Docker version 24.0+
- [ ] Minikube version 1.32+
- [ ] kubectl version 1.29+
- [ ] Helm version 3.14+

---

#### T002 [BLOCK] Start Minikube Cluster

| Attribute | Value |
|-----------|-------|
| **Task Name** | Start Minikube Cluster |
| **Description** | Initialize Minikube with 4 CPUs, 8GB RAM, Docker driver |
| **Tool Used** | Minikube CLI |
| **Files Created** | None (cluster state) |
| **Expected Output** | Minikube status shows all components "Running" |
| **Validation Command** | `minikube status` |

**Command**:
```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker --kubernetes-version=v1.29.0
```

**Acceptance Criteria**:
- [ ] host: Running
- [ ] kubelet: Running
- [ ] apiserver: Running
- [ ] kubeconfig: Configured

---

#### T003 [P] Enable Ingress Addon

| Attribute | Value |
|-----------|-------|
| **Task Name** | Enable Ingress Addon |
| **Description** | Enable nginx ingress controller for external traffic routing |
| **Tool Used** | Minikube CLI |
| **Files Created** | None (addon enabled) |
| **Expected Output** | Ingress controller pod running in ingress-nginx namespace |
| **Validation Command** | `kubectl get pods -n ingress-nginx` |

**Command**:
```bash
minikube addons enable ingress
```

**Acceptance Criteria**:
- [ ] ingress-nginx-controller pod is Running
- [ ] `minikube addons list | grep ingress` shows enabled

---

#### T004 [P] Enable Metrics Server Addon

| Attribute | Value |
|-----------|-------|
| **Task Name** | Enable Metrics Server Addon |
| **Description** | Enable metrics-server for resource monitoring |
| **Tool Used** | Minikube CLI |
| **Files Created** | None (addon enabled) |
| **Expected Output** | Metrics server enabled |
| **Validation Command** | `minikube addons list \| grep metrics-server` |

**Command**:
```bash
minikube addons enable metrics-server
```

**Acceptance Criteria**:
- [ ] metrics-server shows enabled in addons list

---

#### T005 Configure Docker Environment for Minikube

| Attribute | Value |
|-----------|-------|
| **Task Name** | Configure Docker Environment |
| **Description** | Point Docker CLI to Minikube's internal Docker daemon |
| **Tool Used** | Minikube CLI, Docker |
| **Files Created** | None (environment variables) |
| **Expected Output** | Docker commands target Minikube's daemon |
| **Validation Command** | `docker ps \| grep kube` |

**Command**:
```bash
eval $(minikube docker-env)
```

**Acceptance Criteria**:
- [ ] `docker ps` shows Minikube system containers
- [ ] `docker info | grep "Name:"` shows minikube

---

### Phase 1 Checkpoint

| Validation | Command | Expected |
|------------|---------|----------|
| Cluster Running | `minikube status` | All "Running" |
| kubectl Connected | `kubectl cluster-info` | Shows endpoint |
| Ingress Ready | `kubectl get pods -n ingress-nginx` | Controller Running |
| Docker Connected | `docker ps \| grep kube` | Shows K8s containers |

---

## Phase 2: Containerization (Docker Images)

**Purpose**: Create optimized Docker images for API and Frontend
**Duration**: ~20-30 minutes
**User Stories Supported**: US1 (One-Command Deployment)

### Tasks

---

#### T006 [BLOCK] Create Infrastructure Directory Structure

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Infrastructure Directory Structure |
| **Description** | Create `infra/docker/` directory for Dockerfiles |
| **Tool Used** | Claude Code (file system) |
| **Files Created** | `infra/docker/` directory |
| **Expected Output** | Directory exists |
| **Validation Command** | `ls -la infra/docker/` |

**Acceptance Criteria**:
- [ ] `infra/docker/` directory created

---

#### T007 [P] [US1] Create API Dockerfile

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Optimized API Dockerfile |
| **Description** | Create multi-stage Dockerfile for FastAPI backend with health check |
| **Tool Used** | Claude Code (generates Dockerfile) |
| **Files Created** | `infra/docker/api.Dockerfile` |
| **Expected Output** | Valid Dockerfile with builder and runtime stages |
| **Validation Command** | `cat infra/docker/api.Dockerfile \| grep -E "FROM\|HEALTHCHECK"` |

**Key Features**:
- Multi-stage build (builder + runtime)
- Non-root user (appuser)
- Health check endpoint
- Python wheels for fast install
- Target size: <250MB

**Acceptance Criteria**:
- [ ] File exists at `infra/docker/api.Dockerfile`
- [ ] Contains multi-stage build (FROM ... AS builder, FROM ... AS runtime)
- [ ] Contains HEALTHCHECK directive
- [ ] Contains USER directive for non-root

---

#### T008 [P] [US1] Create Frontend Dockerfile

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Optimized Frontend Dockerfile |
| **Description** | Create multi-stage Dockerfile for Next.js standalone build |
| **Tool Used** | Claude Code (generates Dockerfile) |
| **Files Created** | `infra/docker/frontend.Dockerfile` |
| **Expected Output** | Valid Dockerfile with deps, builder, and runner stages |
| **Validation Command** | `cat infra/docker/frontend.Dockerfile \| grep -E "FROM\|standalone"` |

**Key Features**:
- Multi-stage build (deps + builder + runner)
- Non-root user (nextjs)
- Health check endpoint
- Standalone Next.js output
- Target size: <150MB

**Acceptance Criteria**:
- [ ] File exists at `infra/docker/frontend.Dockerfile`
- [ ] Contains 3-stage build (deps, builder, runner)
- [ ] Contains HEALTHCHECK directive
- [ ] Contains standalone copy

---

#### T009 [US1] Update Frontend Next.js Config for Standalone

| Attribute | Value |
|-----------|-------|
| **Task Name** | Update Next.js Config for Standalone Mode |
| **Description** | Add `output: 'standalone'` to next.config.js for Docker optimization |
| **Tool Used** | Claude Code (edit file) |
| **Files Modified** | `frontend/next.config.js` or `frontend/next.config.mjs` |
| **Expected Output** | Config includes standalone output |
| **Validation Command** | `grep -r "standalone" frontend/next.config.*` |

**Acceptance Criteria**:
- [ ] `output: 'standalone'` present in next.config

---

#### T010 [US1] Build API Docker Image

| Attribute | Value |
|-----------|-------|
| **Task Name** | Build API Docker Image |
| **Description** | Build pakaura-api:4.0.0 image in Minikube's Docker daemon |
| **Tool Used** | Docker CLI |
| **Files Created** | Docker image in Minikube |
| **Expected Output** | Image built successfully, size <250MB |
| **Validation Command** | `docker images pakaura-api:4.0.0` |

**Command**:
```bash
eval $(minikube docker-env)
docker build -t pakaura-api:4.0.0 -f infra/docker/api.Dockerfile ./api
```

**Acceptance Criteria**:
- [ ] Image exists: `pakaura-api:4.0.0`
- [ ] Image size < 250MB
- [ ] No build errors

---

#### T011 [US1] Build Frontend Docker Image

| Attribute | Value |
|-----------|-------|
| **Task Name** | Build Frontend Docker Image |
| **Description** | Build pakaura-frontend:4.0.0 image in Minikube's Docker daemon |
| **Tool Used** | Docker CLI |
| **Files Created** | Docker image in Minikube |
| **Expected Output** | Image built successfully, size <150MB |
| **Validation Command** | `docker images pakaura-frontend:4.0.0` |

**Command**:
```bash
eval $(minikube docker-env)
docker build -t pakaura-frontend:4.0.0 -f infra/docker/frontend.Dockerfile ./frontend
```

**Acceptance Criteria**:
- [ ] Image exists: `pakaura-frontend:4.0.0`
- [ ] Image size < 150MB
- [ ] No build errors

---

### Phase 2 Checkpoint

| Validation | Command | Expected |
|------------|---------|----------|
| API Image | `docker images pakaura-api:4.0.0 --format "{{.Size}}"` | <250MB |
| Frontend Image | `docker images pakaura-frontend:4.0.0 --format "{{.Size}}"` | <150MB |
| Images in Minikube | `docker images \| grep pakaura` | Both images listed |

---

## Phase 3: Kubernetes Manifests (Raw YAML)

**Purpose**: Create all Kubernetes resource manifests
**Duration**: ~30-40 minutes
**User Stories Supported**: US1, US2, US3, US4

### Tasks

---

#### T012 [BLOCK] Create Kubernetes Directory Structure

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Kubernetes Directory Structure |
| **Description** | Create directory structure for K8s manifests |
| **Tool Used** | Claude Code (file system) |
| **Files Created** | `infra/kubernetes/`, subdirectories |
| **Expected Output** | Directory tree created |
| **Validation Command** | `find infra/kubernetes -type d` |

**Structure**:
```
infra/kubernetes/
├── postgresql/
├── api/
└── frontend/
```

**Acceptance Criteria**:
- [ ] All directories created

---

#### T013 [P] [US1] Create Namespace Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Namespace Manifest |
| **Description** | Create pakaura namespace definition |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/namespace.yaml` |
| **Expected Output** | Valid namespace YAML |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/namespace.yaml` |

**Acceptance Criteria**:
- [ ] File creates namespace "pakaura"
- [ ] Contains appropriate labels

---

#### T014 [P] [US3] Create ConfigMap Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create ConfigMap Manifest |
| **Description** | Create ConfigMap with non-sensitive configuration |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/configmap.yaml` |
| **Expected Output** | Valid ConfigMap with DB, JWT, AI settings |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/configmap.yaml` |

**Required Keys**:
- DB_NAME, DB_USER, DB_HOST, DB_PORT
- JWT_ALGORITHM, JWT_EXPIRATION_HOURS
- AI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS
- FRONTEND_URL, API_URL
- ENVIRONMENT, DEBUG

**Acceptance Criteria**:
- [ ] Contains all required configuration keys
- [ ] No sensitive data (passwords, secrets)

---

#### T015 [P] [US3] Create Secrets Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Secrets Manifest |
| **Description** | Create Secrets template for sensitive data |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/secrets.yaml` |
| **Expected Output** | Valid Secret with base64 placeholders |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/secrets.yaml` |

**Required Keys**:
- DB_PASSWORD (base64 encoded)
- JWT_SECRET (base64 encoded)
- COHERE_API_KEY (base64 encoded, optional)

**Acceptance Criteria**:
- [ ] All values base64 encoded
- [ ] Type: Opaque

---

#### T016 [P] [US4] Create PostgreSQL StatefulSet Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create PostgreSQL StatefulSet |
| **Description** | Create StatefulSet for PostgreSQL with PVC |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/postgresql/statefulset.yaml` |
| **Expected Output** | Valid StatefulSet with volume claim template |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/postgresql/statefulset.yaml` |

**Key Features**:
- Image: postgres:16-alpine
- Replicas: 1
- PVC: 10Gi
- Readiness/Liveness probes with pg_isready
- Resource limits: 512Mi RAM, 500m CPU

**Acceptance Criteria**:
- [ ] Contains volumeClaimTemplates
- [ ] Contains readinessProbe and livenessProbe
- [ ] Uses env from ConfigMap and Secret

---

#### T017 [P] [US4] Create PostgreSQL Service Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create PostgreSQL Service |
| **Description** | Create headless Service for PostgreSQL |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/postgresql/service.yaml` |
| **Expected Output** | Valid headless Service |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/postgresql/service.yaml` |

**Acceptance Criteria**:
- [ ] clusterIP: None (headless)
- [ ] Port: 5432

---

#### T018 [US1] Create Database Migration Job Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Migration Job |
| **Description** | Create Kubernetes Job for Alembic migrations |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/api/migration-job.yaml` |
| **Expected Output** | Valid Job with init container waiting for DB |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/api/migration-job.yaml` |

**Key Features**:
- Init container: wait-for-db (busybox)
- Command: alembic upgrade head
- backoffLimit: 3
- ttlSecondsAfterFinished: 300

**Acceptance Criteria**:
- [ ] Contains initContainer for DB readiness
- [ ] Runs alembic upgrade head
- [ ] Uses pakaura-api image

---

#### T019 [US2] Create API Deployment Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create API Deployment |
| **Description** | Create Deployment for FastAPI backend with health probes |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/api/deployment.yaml` |
| **Expected Output** | Valid Deployment with 2 replicas |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/api/deployment.yaml` |

**Key Features**:
- Image: pakaura-api:4.0.0
- Replicas: 2
- Readiness probe: /api/v1/health
- Liveness probe: /api/v1/health
- Init container: wait-for-db
- Resource limits: 512Mi RAM, 500m CPU

**Acceptance Criteria**:
- [ ] Replicas: 2
- [ ] Contains readinessProbe and livenessProbe
- [ ] Contains initContainer

---

#### T020 [P] [US1] Create API Service Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create API Service |
| **Description** | Create ClusterIP Service for API |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/api/service.yaml` |
| **Expected Output** | Valid ClusterIP Service |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/api/service.yaml` |

**Acceptance Criteria**:
- [ ] Type: ClusterIP
- [ ] Port: 8000

---

#### T021 [US2] Create Frontend Deployment Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Frontend Deployment |
| **Description** | Create Deployment for Next.js frontend |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/frontend/deployment.yaml` |
| **Expected Output** | Valid Deployment with 2 replicas |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/frontend/deployment.yaml` |

**Key Features**:
- Image: pakaura-frontend:4.0.0
- Replicas: 2
- Readiness probe: /
- Liveness probe: /
- Resource limits: 256Mi RAM, 250m CPU

**Acceptance Criteria**:
- [ ] Replicas: 2
- [ ] Contains readinessProbe and livenessProbe

---

#### T022 [P] [US1] Create Frontend Service Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Frontend Service |
| **Description** | Create ClusterIP Service for Frontend |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/frontend/service.yaml` |
| **Expected Output** | Valid ClusterIP Service |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/frontend/service.yaml` |

**Acceptance Criteria**:
- [ ] Type: ClusterIP
- [ ] Port: 3000

---

#### T023 [US1] Create Ingress Manifest

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Ingress |
| **Description** | Create Ingress for external access via nginx |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/kubernetes/ingress.yaml` |
| **Expected Output** | Valid Ingress with path routing |
| **Validation Command** | `kubectl apply --dry-run=client -f infra/kubernetes/ingress.yaml` |

**Key Features**:
- ingressClassName: nginx
- Host: pakaura.local
- Paths: / → frontend, /api → api

**Acceptance Criteria**:
- [ ] Routes /api to API service
- [ ] Routes / to Frontend service
- [ ] Contains nginx annotations

---

### Phase 3 Checkpoint

| Validation | Command | Expected |
|------------|---------|----------|
| All YAMLs Valid | `kubectl apply --dry-run=client -f infra/kubernetes/ -R` | No errors |
| File Count | `find infra/kubernetes -name "*.yaml" \| wc -l` | 9 files |

---

## Phase 4: Helm Chart Creation

**Purpose**: Package manifests into reusable Helm chart
**Duration**: ~30-40 minutes
**User Stories Supported**: US1, US5

### Tasks

---

#### T024 [BLOCK] Create Helm Chart Directory Structure

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Helm Chart Structure |
| **Description** | Initialize Helm chart directory structure |
| **Tool Used** | Claude Code (file system) |
| **Files Created** | `infra/helm/pakaura/` with subdirectories |
| **Expected Output** | Standard Helm chart structure |
| **Validation Command** | `find infra/helm/pakaura -type f` |

**Structure**:
```
infra/helm/pakaura/
├── Chart.yaml
├── values.yaml
├── .helmignore
└── templates/
    ├── _helpers.tpl
    ├── postgresql/
    ├── api/
    ├── frontend/
    └── NOTES.txt
```

**Acceptance Criteria**:
- [ ] All directories created
- [ ] Chart.yaml exists

---

#### T025 [P] [US1] Create Chart.yaml

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Helm Chart Metadata |
| **Description** | Create Chart.yaml with metadata |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/helm/pakaura/Chart.yaml` |
| **Expected Output** | Valid Chart.yaml |
| **Validation Command** | `helm lint infra/helm/pakaura 2>&1 \| grep -i chart` |

**Acceptance Criteria**:
- [ ] apiVersion: v2
- [ ] name: pakaura
- [ ] version: 4.0.0
- [ ] appVersion: "4.0.0"

---

#### T026 [US1] Create values.yaml

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Helm Values File |
| **Description** | Create default values with all configurable options |
| **Tool Used** | Claude Code (generates YAML) |
| **Files Created** | `infra/helm/pakaura/values.yaml` |
| **Expected Output** | Comprehensive values file |
| **Validation Command** | `helm lint infra/helm/pakaura` |

**Required Sections**:
- global (namespace, imageTag)
- frontend (enabled, replicas, image, resources, probes)
- api (enabled, replicas, image, resources, probes, env)
- postgresql (enabled, image, persistence, resources, auth)
- ingress (enabled, className, hostname, annotations)
- secrets (jwtSecret, dbPassword, cohereApiKey)

**Acceptance Criteria**:
- [ ] All components configurable
- [ ] Sensible defaults provided
- [ ] Secrets marked as required

---

#### T027 [US5] Create _helpers.tpl

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Helm Template Helpers |
| **Description** | Create helper functions for templates |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/_helpers.tpl` |
| **Expected Output** | Valid template helpers |
| **Validation Command** | `helm template pakaura infra/helm/pakaura --debug 2>&1 \| head -20` |

**Required Helpers**:
- pakaura.name
- pakaura.fullname
- pakaura.chart
- pakaura.labels
- pakaura.selectorLabels
- pakaura.databaseUrl

**Acceptance Criteria**:
- [ ] All helpers defined
- [ ] Templates render without errors

---

#### T028 [P] [US1] Create Templated Namespace

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated Namespace |
| **Description** | Convert namespace.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/namespace.yaml` |
| **Expected Output** | Namespace template using values |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep "kind: Namespace"` |

**Acceptance Criteria**:
- [ ] Uses {{ .Values.global.namespace }}
- [ ] Includes Helm labels

---

#### T029 [P] [US3] Create Templated ConfigMap

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated ConfigMap |
| **Description** | Convert configmap.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/configmap.yaml` |
| **Expected Output** | ConfigMap template using values |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep "kind: ConfigMap"` |

**Acceptance Criteria**:
- [ ] Uses values for all configuration
- [ ] Namespace from values

---

#### T030 [P] [US3] Create Templated Secrets

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated Secrets |
| **Description** | Convert secrets.yaml to Helm template with b64enc |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/secrets.yaml` |
| **Expected Output** | Secrets template with base64 encoding |
| **Validation Command** | `helm template pakaura infra/helm/pakaura --set secrets.jwtSecret=test --set secrets.dbPassword=test \| grep "kind: Secret"` |

**Acceptance Criteria**:
- [ ] Uses {{ .Values.secrets.xxx | b64enc }}
- [ ] Handles empty values gracefully

---

#### T031 [P] [US4] Create Templated PostgreSQL StatefulSet

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated PostgreSQL StatefulSet |
| **Description** | Convert postgresql/statefulset.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/postgresql/statefulset.yaml` |
| **Expected Output** | StatefulSet template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep "kind: StatefulSet"` |

**Acceptance Criteria**:
- [ ] Uses values for image, resources, persistence
- [ ] Conditional on {{ .Values.postgresql.enabled }}

---

#### T032 [P] [US4] Create Templated PostgreSQL Service

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated PostgreSQL Service |
| **Description** | Convert postgresql/service.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/postgresql/service.yaml` |
| **Expected Output** | Service template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep -A5 "name: postgresql"` |

**Acceptance Criteria**:
- [ ] Headless service (clusterIP: None)

---

#### T033 [US1] Create Templated Migration Job

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated Migration Job |
| **Description** | Convert api/migration-job.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/api/migration-job.yaml` |
| **Expected Output** | Job template with hooks |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep "kind: Job"` |

**Acceptance Criteria**:
- [ ] Uses api image from values
- [ ] Conditional on {{ .Values.migration.enabled }}

---

#### T034 [US2] Create Templated API Deployment

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated API Deployment |
| **Description** | Convert api/deployment.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/api/deployment.yaml` |
| **Expected Output** | Deployment template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep -A10 "name: api"` |

**Acceptance Criteria**:
- [ ] Uses values for replicas, image, resources
- [ ] Conditional on {{ .Values.api.enabled }}

---

#### T035 [P] [US1] Create Templated API Service

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated API Service |
| **Description** | Convert api/service.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/api/service.yaml` |
| **Expected Output** | Service template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep -A5 "name: api"` |

**Acceptance Criteria**:
- [ ] Port from values

---

#### T036 [US2] Create Templated Frontend Deployment

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated Frontend Deployment |
| **Description** | Convert frontend/deployment.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/frontend/deployment.yaml` |
| **Expected Output** | Deployment template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep -A10 "name: frontend"` |

**Acceptance Criteria**:
- [ ] Uses values for replicas, image, resources
- [ ] Conditional on {{ .Values.frontend.enabled }}

---

#### T037 [P] [US1] Create Templated Frontend Service

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated Frontend Service |
| **Description** | Convert frontend/service.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/frontend/service.yaml` |
| **Expected Output** | Service template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep -A5 "name: frontend"` |

**Acceptance Criteria**:
- [ ] Port from values

---

#### T038 [US1] Create Templated Ingress

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Templated Ingress |
| **Description** | Convert ingress.yaml to Helm template |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/ingress.yaml` |
| **Expected Output** | Ingress template |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| grep "kind: Ingress"` |

**Acceptance Criteria**:
- [ ] Uses values for hostname, className, annotations
- [ ] Conditional on {{ .Values.ingress.enabled }}

---

#### T039 [US5] Create NOTES.txt

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Post-Install Notes |
| **Description** | Create NOTES.txt with access instructions |
| **Tool Used** | Claude Code (generates template) |
| **Files Created** | `infra/helm/pakaura/templates/NOTES.txt` |
| **Expected Output** | Helpful post-install instructions |
| **Validation Command** | `helm template pakaura infra/helm/pakaura \| tail -30` |

**Acceptance Criteria**:
- [ ] Shows access URL
- [ ] Shows kubectl commands
- [ ] Shows AI chatbot features

---

#### T040 [P] Create .helmignore

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Helm Ignore File |
| **Description** | Create .helmignore to exclude unnecessary files |
| **Tool Used** | Claude Code (generates file) |
| **Files Created** | `infra/helm/pakaura/.helmignore` |
| **Expected Output** | Valid .helmignore |
| **Validation Command** | `cat infra/helm/pakaura/.helmignore` |

**Acceptance Criteria**:
- [ ] Ignores .git, *.md, tests/

---

#### T041 Validate Helm Chart

| Attribute | Value |
|-----------|-------|
| **Task Name** | Validate Helm Chart |
| **Description** | Lint and template the chart to verify correctness |
| **Tool Used** | Helm CLI |
| **Files Created** | None |
| **Expected Output** | No errors or warnings |
| **Validation Command** | `helm lint infra/helm/pakaura && helm template pakaura infra/helm/pakaura --set secrets.jwtSecret=test --set secrets.dbPassword=test` |

**Acceptance Criteria**:
- [ ] `helm lint` passes with no errors
- [ ] `helm template` generates valid YAML
- [ ] No undefined variables

---

### Phase 4 Checkpoint

| Validation | Command | Expected |
|------------|---------|----------|
| Lint Passes | `helm lint infra/helm/pakaura` | 0 chart(s) linted, 0 chart(s) failed |
| Template Renders | `helm template pakaura infra/helm/pakaura --set secrets.jwtSecret=x --set secrets.dbPassword=x \| wc -l` | >200 lines |
| All Resources | `helm template pakaura infra/helm/pakaura \| grep "^kind:" \| sort -u` | 7+ resource types |

---

## Phase 5: Deployment & Validation

**Purpose**: Deploy application and validate all functionality
**Duration**: ~20-30 minutes
**User Stories Supported**: All (US1-US5)

### Tasks

---

#### T042 [BLOCK] Create Scripts Directory

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Scripts Directory |
| **Description** | Create scripts/ directory for deployment automation |
| **Tool Used** | Claude Code (file system) |
| **Files Created** | `scripts/` directory |
| **Expected Output** | Directory exists |
| **Validation Command** | `ls -la scripts/` |

**Acceptance Criteria**:
- [ ] scripts/ directory created

---

#### T043 [US5] Create AI-Assisted Deployment Script

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create AI Deployment Script |
| **Description** | Create comprehensive deployment script with setup, deploy, status, destroy commands |
| **Tool Used** | Claude Code (generates bash script) |
| **Files Created** | `scripts/ai-deploy.sh` |
| **Expected Output** | Executable bash script with all commands |
| **Validation Command** | `bash scripts/ai-deploy.sh help` |

**Commands to Support**:
- setup: Full setup (minikube + build + deploy)
- build: Build Docker images only
- deploy: Helm install/upgrade
- status: Show pod/service status
- health: Run health checks
- logs: Stream logs
- destroy: Cleanup everything
- help: Show usage

**Acceptance Criteria**:
- [ ] Script is executable
- [ ] All commands implemented
- [ ] Color-coded output
- [ ] Error handling

---

#### T044 [US1] Deploy Application via Helm

| Attribute | Value |
|-----------|-------|
| **Task Name** | Deploy Application |
| **Description** | Install the Helm chart to create all resources |
| **Tool Used** | Helm CLI |
| **Files Created** | Kubernetes resources in cluster |
| **Expected Output** | All pods running |
| **Validation Command** | `helm list -n pakaura && kubectl get pods -n pakaura` |

**Command**:
```bash
helm upgrade --install pakaura infra/helm/pakaura \
  --namespace pakaura \
  --create-namespace \
  --set secrets.jwtSecret="$(openssl rand -base64 32)" \
  --set secrets.dbPassword="$(openssl rand -base64 16)" \
  --wait \
  --timeout 5m
```

**Acceptance Criteria**:
- [ ] Helm release created
- [ ] All pods reach Running status
- [ ] No restarts or errors

---

#### T045 [US1] Verify All Pods Running

| Attribute | Value |
|-----------|-------|
| **Task Name** | Verify Pods Running |
| **Description** | Confirm all 5 pods are in Running state |
| **Tool Used** | kubectl CLI |
| **Files Created** | None |
| **Expected Output** | 5 pods Running |
| **Validation Command** | `kubectl get pods -n pakaura` |

**Expected Pods**:
- postgresql-0 (1/1 Running)
- api-xxx (1/1 Running) x2
- frontend-xxx (1/1 Running) x2

**Acceptance Criteria**:
- [ ] postgresql-0 Running
- [ ] 2 API pods Running
- [ ] 2 Frontend pods Running

---

#### T046 [US2] Test API Health Endpoint

| Attribute | Value |
|-----------|-------|
| **Task Name** | Test API Health |
| **Description** | Verify API health endpoint responds correctly |
| **Tool Used** | curl, kubectl |
| **Files Created** | None |
| **Expected Output** | 200 OK with healthy status |
| **Validation Command** | `kubectl exec -n pakaura deploy/api -- curl -s localhost:8000/api/v1/health` |

**Acceptance Criteria**:
- [ ] Returns HTTP 200
- [ ] JSON contains "status": "healthy"

---

#### T047 [US1] Test Frontend Accessibility

| Attribute | Value |
|-----------|-------|
| **Task Name** | Test Frontend Access |
| **Description** | Verify frontend is accessible via service |
| **Tool Used** | minikube, browser |
| **Files Created** | None |
| **Expected Output** | Login page loads |
| **Validation Command** | `minikube service frontend -n pakaura --url` |

**Acceptance Criteria**:
- [ ] URL returned
- [ ] Page loads in browser
- [ ] Login form visible

---

#### T048 [US2] Test Self-Healing (Pod Recreation)

| Attribute | Value |
|-----------|-------|
| **Task Name** | Test Self-Healing |
| **Description** | Delete API pod and verify Kubernetes recreates it |
| **Tool Used** | kubectl CLI |
| **Files Created** | None |
| **Expected Output** | New pod created within 60 seconds |
| **Validation Command** | `kubectl delete pod -l app=api -n pakaura && kubectl get pods -n pakaura -w` |

**Acceptance Criteria**:
- [ ] Old pod terminated
- [ ] New pod created automatically
- [ ] New pod reaches Running within 60s

---

#### T049 [US4] Test Data Persistence

| Attribute | Value |
|-----------|-------|
| **Task Name** | Test Data Persistence |
| **Description** | Create data, restart PostgreSQL, verify data persists |
| **Tool Used** | kubectl, psql |
| **Files Created** | None |
| **Expected Output** | Data survives pod restart |
| **Validation Command** | See procedure below |

**Procedure**:
1. Create a user/task via the UI
2. `kubectl delete pod postgresql-0 -n pakaura`
3. Wait for pod to restart
4. Verify user/task still exists

**Acceptance Criteria**:
- [ ] PostgreSQL pod restarts
- [ ] PVC maintains data
- [ ] Application shows existing data

---

#### T050 [US3] Verify Secrets Not Exposed

| Attribute | Value |
|-----------|-------|
| **Task Name** | Verify Secrets Security |
| **Description** | Confirm secrets are base64 encoded and not in pod specs |
| **Tool Used** | kubectl CLI |
| **Files Created** | None |
| **Expected Output** | Secrets properly encoded |
| **Validation Command** | `kubectl get secret pakaura-secrets -n pakaura -o yaml` |

**Acceptance Criteria**:
- [ ] All values base64 encoded
- [ ] No plaintext passwords
- [ ] Pod specs reference secretKeyRef (not inline values)

---

#### T051 [US5] Verify Helm Release

| Attribute | Value |
|-----------|-------|
| **Task Name** | Verify Helm Release |
| **Description** | Confirm Helm release is properly installed |
| **Tool Used** | Helm CLI |
| **Files Created** | None |
| **Expected Output** | Release status: deployed |
| **Validation Command** | `helm list -n pakaura && helm status pakaura -n pakaura` |

**Acceptance Criteria**:
- [ ] Release name: pakaura
- [ ] Status: deployed
- [ ] Chart version: pakaura-4.0.0

---

#### T052 [US1] Test AI Chatbot End-to-End

| Attribute | Value |
|-----------|-------|
| **Task Name** | Test AI Chatbot |
| **Description** | Verify AI chatbot responds to task commands |
| **Tool Used** | Browser, Application UI |
| **Files Created** | None |
| **Expected Output** | AI responds to natural language |
| **Validation Command** | Manual UI test |

**Test Scenarios**:
1. "Add a task to demo Kubernetes" → Task created
2. "Show my tasks" → List displayed
3. "Complete the Kubernetes task" → Task marked complete
4. "Delete completed tasks" → Task removed

**Acceptance Criteria**:
- [ ] Add task works
- [ ] List tasks works
- [ ] Complete task works
- [ ] Delete task works

---

#### T053 Create Demo Documentation

| Attribute | Value |
|-----------|-------|
| **Task Name** | Create Demo Documentation |
| **Description** | Document demo workflow for hackathon judges |
| **Tool Used** | Claude Code (generates markdown) |
| **Files Created** | `docs/DEMO.md` |
| **Expected Output** | Step-by-step demo guide |
| **Validation Command** | `cat docs/DEMO.md` |

**Acceptance Criteria**:
- [ ] Quick start commands
- [ ] 5-minute demo script
- [ ] Talking points for judges
- [ ] Troubleshooting guide

---

### Phase 5 Checkpoint (Final)

| Validation | Command | Expected |
|------------|---------|----------|
| All Pods Running | `kubectl get pods -n pakaura \| grep Running \| wc -l` | 5 |
| Helm Release | `helm list -n pakaura -o json \| jq '.[0].status'` | "deployed" |
| API Health | `kubectl exec deploy/api -n pakaura -- curl -s localhost:8000/api/v1/health \| jq .status` | "healthy" |
| Self-Healing | Delete pod, watch recreation | New pod in <60s |
| Data Persistence | Restart DB, check data | Data preserved |

---

## Task Summary

| Phase | Task Range | Count | Duration |
|-------|------------|-------|----------|
| 1. Environment Setup | T001-T005 | 5 | ~15-20 min |
| 2. Containerization | T006-T011 | 6 | ~20-30 min |
| 3. Kubernetes Manifests | T012-T023 | 12 | ~30-40 min |
| 4. Helm Chart Creation | T024-T041 | 18 | ~30-40 min |
| 5. Deployment & Validation | T042-T053 | 12 | ~20-30 min |
| **TOTAL** | T001-T053 | **53** | **~2-3 hours** |

---

## Parallel Execution Opportunities

### Phase 1 (After T002)
```
T003 [P] Enable Ingress ──┬── T004 [P] Enable Metrics
                          │
                          ▼
                       T005 Configure Docker
```

### Phase 2 (After T006)
```
T007 [P] API Dockerfile ──┬── T008 [P] Frontend Dockerfile
                          │
                          ▼
                       T009 Update Next.js Config
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
T010 Build API Image              T011 Build Frontend Image
```

### Phase 3 (After T012)
```
T013 [P] Namespace ──┬── T014 [P] ConfigMap ──┬── T015 [P] Secrets
                     │                        │
                     ▼                        ▼
T016 [P] PostgreSQL SS ──── T017 [P] PostgreSQL Svc
                     │
                     ▼
              T018 Migration Job
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
T019 API Deployment      T021 Frontend Deployment
T020 [P] API Service     T022 [P] Frontend Service
          │                     │
          └──────────┬──────────┘
                     ▼
              T023 Ingress
```

### Phase 4 (After T024)
```
All T028-T040 can run in parallel after T024-T027 complete
```

---

## Dependencies Graph

```
T001 ──▶ T002 ──▶ T003, T004 ──▶ T005
                      │
                      ▼
T006 ──▶ T007, T008 ──▶ T009 ──▶ T010, T011
                                    │
                                    ▼
T012 ──▶ T013-T023 (manifests) ──▶ T024 (Helm)
                                    │
                                    ▼
T024 ──▶ T025-T041 (templates) ──▶ T042 (scripts)
                                    │
                                    ▼
T042 ──▶ T043 ──▶ T044 ──▶ T045-T053 (validation)
```

---

## Acceptance Criteria Summary

### Must Have (Blocking)
- [ ] Minikube cluster running with ingress
- [ ] Docker images built (<250MB API, <150MB Frontend)
- [ ] All Kubernetes manifests valid
- [ ] Helm chart lints successfully
- [ ] All 5 pods Running
- [ ] API health check passes
- [ ] Frontend accessible

### Should Have (Demo Quality)
- [ ] Self-healing verified
- [ ] Data persistence verified
- [ ] AI chatbot functional
- [ ] Secrets properly secured
- [ ] AI deployment script working

### Nice to Have (Polish)
- [ ] Demo documentation complete
- [ ] Talking points prepared
- [ ] Troubleshooting guide included

---

*Tasks generated by Claude Code - AI-Assisted DevOps Engineer*
*Version: 4.0.0 | Date: 2026-01-18*

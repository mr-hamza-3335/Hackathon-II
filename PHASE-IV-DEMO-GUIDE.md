# Phase IV Demo Guide - Quick Reference

## 🚀 One-Line Demo Start

```bash
minikube service frontend -n pakaura
```

This opens the application in your browser!

---

## 📋 Pre-Demo Checklist

```bash
# Verify everything is running
kubectl get pods -n pakaura
# Expected: All pods should show 1/1 READY

# Check services
kubectl get svc -n pakaura
# Expected: frontend (30300), api (30800), postgres (5432)

# Test API
curl http://192.168.49.2:30800/api/v1/health
# Expected: {"status":"healthy","version":"1.0.0","phase":3}
```

---

## 🎬 Judge Demo Flow (3 minutes)

### 1. Show Kubernetes Deployment (30 seconds)
```bash
kubectl get all -n pakaura
```
**Point out**: 3 deployments, 3 services, all running

### 2. Show Secrets Management (20 seconds)
```bash
kubectl get secrets -n pakaura
kubectl describe secret pakaura-secrets -n pakaura
```
**Point out**: DATABASE_URL, JWT_SECRET stored securely

### 3. Open Application (10 seconds)
```bash
minikube service frontend -n pakaura
```
Browser opens automatically

### 4. Demo Authentication (60 seconds)
- Click **Register**
- Email: `judge@pakaura.com`
- Password: `Judge123!`
- Click **Register** button → Success!
- **Login** with same credentials → Dashboard appears

### 5. Demo AI Assistant (60 seconds)
- Click **AI Assistant** tab
- Type: `Add a task to buy groceries`
- Press Enter → AI confirms task created
- Type: `Show my tasks`
- AI displays the task
- Type: `Complete the grocery task`
- AI marks it complete

---

## 💡 Key Points to Emphasize

1. **Kubernetes Native**
   - All services running as pods
   - Secrets managed by Kubernetes
   - Service discovery via DNS

2. **Production-Ready Architecture**
   - Health probes configured
   - Proper service types (ClusterIP vs NodePort)
   - Database in cluster for local dev

3. **Phase IV Requirements Met**
   - ✅ No manual configuration needed
   - ✅ Uses Helm for deployment
   - ✅ Secrets properly managed
   - ✅ Services exposed correctly

4. **Authentication Working**
   - PostgreSQL database in cluster
   - User registration functional
   - JWT-based authentication
   - No security compromises

---

## 🔧 If Something Goes Wrong

### Pod Not Ready
```bash
kubectl describe pod -n pakaura <pod-name>
kubectl logs -n pakaura <pod-name> --tail=50
```

### Database Issues
```bash
kubectl logs -n pakaura -l app=postgres
kubectl exec -n pakaura deployment/postgres -- psql -U pakaura -l
```

### Quick Reset
```bash
kubectl rollout restart deployment/api -n pakaura
kubectl rollout restart deployment/frontend -n pakaura
```

---

## 📊 Technical Architecture

```
┌─────────────────────────────────────────┐
│           Browser (Judge)               │
│  http://192.168.49.2:30300 (Frontend)   │
│  http://192.168.49.2:30800 (API)        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Minikube Cluster                │
│  ┌───────────────────────────────────┐  │
│  │  Namespace: pakaura               │  │
│  │                                   │  │
│  │  ┌──────────┐  ┌──────────┐     │  │
│  │  │ Frontend │  │   API    │     │  │
│  │  │ NodePort │  │ NodePort │     │  │
│  │  │  :30300  │  │  :30800  │     │  │
│  │  └──────────┘  └──────────┘     │  │
│  │                      ↓            │  │
│  │              ┌──────────┐        │  │
│  │              │PostgreSQL│        │  │
│  │              │ClusterIP │        │  │
│  │              │  :5432   │        │  │
│  │              └──────────┘        │  │
│  │                                   │  │
│  │  Secrets: DATABASE_URL,           │  │
│  │           JWT_SECRET              │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🎯 Success Criteria

| Criteria | Status | Evidence |
|----------|--------|----------|
| All pods Running | ✅ | `kubectl get pods -n pakaura` |
| Frontend accessible | ✅ | Browser opens to http://192.168.49.2:30300 |
| API responds | ✅ | Health check returns 200 OK |
| Registration works | ✅ | New user created in database |
| Login works | ✅ | JWT token issued, dashboard loads |
| AI Chatbot works | ✅ | Tasks created/listed/completed via natural language |
| Secrets managed | ✅ | Kubernetes Secrets, not hardcoded |
| No manual steps | ✅ | Helm install + upgrade only |

---

## 📝 Commands Cheat Sheet

```bash
# View everything
kubectl get all -n pakaura

# View logs
kubectl logs -n pakaura -l app=api --tail=50
kubectl logs -n pakaura -l app=frontend --tail=50

# Execute command in pod
kubectl exec -n pakaura deployment/api -- <command>

# Port forward (alternative access)
kubectl port-forward -n pakaura svc/frontend 8080:3000

# Helm status
helm status pakaura

# Restart service
kubectl rollout restart deployment/api -n pakaura

# Delete everything (start over)
helm uninstall pakaura
kubectl delete namespace pakaura
```

---

**Phase IV**: ✅ **COMPLETE**
**Demo Ready**: ✅ **YES**
**Time to Demo**: ⏱️ **~3 minutes**

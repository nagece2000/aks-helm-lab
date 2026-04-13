**dev.yaml** (Lower resources, fewer replicas):
```yaml
replicaCount: 1
resources:
  limits:
    cpu: 250m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

**prod.yaml** (Higher resources, more replicas):
```yaml
replicaCount: 5
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

**Deployment:**
```bash
# Deploy dev environment
helm upgrade webapp ./helm-charts/webapp -f ./helm-charts/webapp/values/dev.yaml

# Deploy prod environment
helm upgrade webapp ./helm-charts/webapp -f ./helm-charts/webapp/values/prod.yaml

# Deploy with default values
helm upgrade webapp ./helm-charts/webapp
```

## Key Learnings

### Helm Hooks
- Hooks run at specific lifecycle events (pre/post install/upgrade/delete)
- Useful for automation tasks that need to run at deployment time
- `hook-delete-policy` controls cleanup behavior

### Rollbacks
- Every `helm upgrade` creates a new revision
- Revisions are automatically saved
- Rollback is instant and safe
- Critical for production deployments

### Values Management
- Base values.yaml provides defaults
- Environment files override specific values
- Multiple `-f` flags can be combined
- `--set` flags have highest priority
- Same chart, multiple configurations

## Real-World Environment Strategy

**Separate Clusters (Recommended):**
- Dev AKS Cluster
- Staging AKS Cluster  
- Production AKS Cluster

**Each environment has:**
- Different Azure resources
- Different databases
- Different URLs/domains
- Different configurations
- Complete isolation

**Apps distinguish environments via:**
- Environment variables (ENVIRONMENT=dev/staging/prod)
- Different database connections
- Different ingress hosts
- Different secrets

## Commands Reference

```bash
# Hooks
kubectl get jobs                    # View hook jobs
kubectl logs job/<job-name>         # View hook output

# History & Rollbacks
helm history <release>              # View all revisions
helm rollback <release>             # Rollback to previous
helm rollback <release> <revision>  # Rollback to specific revision

# Values Management
helm upgrade <release> <chart> -f values/dev.yaml      # Use dev values
helm upgrade <release> <chart> -f values/prod.yaml     # Use prod values
helm upgrade <release> <chart>                         # Use default values

# Combining values
helm upgrade <release> <chart> -f values.yaml -f overrides.yaml --set image.tag=v3
```

## What's Next

- Return to Phase 4 to add Grafana monitoring
- Create final comprehensive deployment guide
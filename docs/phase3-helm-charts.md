# Phase 3: Helm Chart Development

## Helm Charts Created

### Webapp Chart
- **Location**: `helm-charts/webapp/`
- **Components**:
  - Flask application deployment (2 replicas)
  - PostgreSQL deployment
  - Services (LoadBalancer for webapp, ClusterIP for PostgreSQL)
  - Secrets for database credentials

## Configuration

### values.yaml
- Image: `acrhelmlab.azurecr.io/flask-webapp:v2`
- Replicas: 2
- Service Type: LoadBalancer
- Database: PostgreSQL 16 (official image)
- Resources: CPU/Memory limits configured

### Templates
- `deployment.yaml` - Flask app deployment with env vars
- `service.yaml` - LoadBalancer service
- `secret.yaml` - Database password
- `postgres-deployment.yaml` - PostgreSQL deployment and service

## Deployment
```bash
helm install webapp ./helm-charts/webapp
```

## Result

- **Application URL**: http://4.255.4.198
- **Database**: Connected ✅
- **Visitor Counter**: Working ✅
- **Replicas**: 2 Flask pods, 1 PostgreSQL pod

## Key Learnings

1. Helm simplifies multi-service deployments
2. Templates allow configuration through values.yaml
3. One command deploys entire stack
4. Easy upgrades: `helm upgrade webapp ./helm-charts/webapp`
5. Easy rollbacks: `helm rollback webapp`
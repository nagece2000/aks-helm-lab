# Phase 6 Addendum: Grafana Monitoring

## Setup

Installed kube-prometheus-stack which includes:
- **Prometheus** - Metrics collection
- **Grafana** - Visualization dashboards
- **Alertmanager** - Alert management
- **Node Exporter** - Node metrics
- **Kube State Metrics** - Kubernetes metrics

## Installation

```bash
# Add prometheus community repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install monitoring stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --set grafana.service.type=LoadBalancer
```

## Access

- **URL**: http://104.45.181.102
- **Username**: admin
- **Password**: Retrieved from Kubernetes secret

```bash
# Get password (PowerShell)
$secret = kubectl get secrets monitoring-grafana -o jsonpath="{.data.admin-password}"
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secret))
```

## Pre-Built Dashboards

The stack includes ~20 pre-configured dashboards:

**Key Dashboards:**
- **Kubernetes / Compute Resources / Cluster** - Overall cluster health
- **Kubernetes / Compute Resources / Namespace (Pods)** - Per-namespace metrics
- **Kubernetes / Compute Resources / Pod** - Individual pod metrics
- **Node Exporter / Nodes** - Node-level system metrics

**Metrics Available:**
- CPU usage (per pod, namespace, cluster)
- Memory consumption
- Network I/O
- Disk I/O
- Pod restart counts
- Container states
- Resource requests vs limits

## Screenshots Captured

- Dashboard overview
- Namespace (default) pod metrics
- Cluster resource utilization

## Notes

- Grafana uses LoadBalancer (additional Azure LB cost)
- Prometheus stores metrics in-cluster (no persistent volume configured)
- Default retention: 15 days
- For production: Add persistent storage, configure alerts, set up retention policies
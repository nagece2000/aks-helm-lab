# Phase 2: Application Development & Containerization

## Application Created

- **Type**: Python Flask web application
- **Features**:
  - Home page with visitor counter
  - PostgreSQL integration (tracks visits)
  - Health check endpoint for Kubernetes
  - Responsive UI with gradient design

## Files Created

- `app/app.py` - Flask application code
- `app/templates/index.html` - Web interface
- `app/requirements.txt` - Python dependencies
- `app/Dockerfile` - Container build instructions

## Container Image

- **Registry**: acrhelmlab.azurecr.io
- **Image**: flask-webapp:v1
- **Built**: Using `az acr build` (cloud-based build)

## Testing

- Deployed test pod to AKS
- Verified image pulls from ACR successfully
- Confirmed app runs (database disconnected as expected)
- External IP: Accessible via LoadBalancer

## Next Steps

Phase 3 will create Helm charts to deploy both the Flask app and PostgreSQL together.
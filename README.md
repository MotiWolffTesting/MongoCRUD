## Enemy Soldiers CRUD API (FastAPI + MongoDB)

A small FastAPI service exposing CRUD over MongoDB for an enemy soldiers dataset.

### What’s inside
- `main.py`: FastAPI app and routes under `/soldiersdb/`
- `services/data_loader/dal.py`: PyMongo DAL (sync)
- `services/data_loader/models.py`: Pydantic models
- `Dockerfile`: container image for the API
- `scripts/commands.bat`: read-only copy/paste guide for Docker + OpenShift commands

### Requirements
- Python 3.11+
- Docker with Buildx
- oc (OpenShift CLI) and access to a project
- MongoDB reachable by the API (service name `mongodb` on OpenShift)

### Install (local dev)
```bash
pip install -r requirements.txt
export MONGODB_URI="mongodb://localhost:27017"   # or your Mongo connection string
python main.py
# API on http://localhost:8000
```

### Run MongoDB locally (optional)
```bash
docker run -d --name mongodb -p 27017:27017 mongo:7.0
export MONGODB_URI="mongodb://localhost:27017"
python main.py
```

### Build and push Docker image (amd64)
Replace `YOUR_USER`.
```bash
docker login
docker buildx create --use 2>/dev/null || true
docker buildx build --platform linux/amd64 \
  -t docker.io/YOUR_USER/enemy-soldiers-api:v1-amd64 --push .
```

### OpenShift quick deploy (using Docker Hub image)
Assumes you already deployed MongoDB as a Service named `mongodb` (for example with the official image). Set the Mongo URI to match your DB, DB name, and credentials.
```bash
oc project YOUR_PROJECT || oc new-project YOUR_PROJECT

oc new-app docker.io/YOUR_USER/enemy-soldiers-api:v1-amd64 \
  --name=enemy-soldiers-api \
  -e MONGODB_URI="mongodb://admin:adminpass@mongodb:27017/enemy_soldiers?authSource=admin"

oc expose deploy enemy-soldiers-api --port=8000 --target-port=8000 --name=enemy-soldiers-api || true
oc expose svc enemy-soldiers-api || true
oc rollout status -w deploy/enemy-soldiers-api

ROUTE=$(oc get route enemy-soldiers-api -o jsonpath='{.spec.host}')
echo "http://$ROUTE"
```

### Test
```bash
# List all
curl "http://$ROUTE/soldiersdb/"

# Create
curl -X POST "http://$ROUTE/soldiersdb/" -H "Content-Type: application/json" \
  -d '{"first_name":"Tal","last_name":"Shapiro","phone_number":"+972-50-0000005","rank":"Private"}'

# Get by ID
curl "http://$ROUTE/soldiersdb/1"

# Update
curl -X PUT "http://$ROUTE/soldiersdb/1" -H "Content-Type: application/json" -d '{"rank":"Lieutenant"}'

# Delete
curl -X DELETE "http://$ROUTE/soldiersdb/1"
```

### Troubleshooting
- Image won’t start on OpenShift: build amd64 or multi-arch
  - `docker buildx build --platform linux/amd64 ... --push .`
- ImagePullBackOff from Docker Hub: ensure repo is public or link a pull secret to the `default` serviceaccount
- 500 with BSON/ObjectId: this project drops `_id` and serializes results explicitly; ensure you redeployed the latest image
- Route 503/“Application not available”: verify Service/port `8000`, endpoints exist, and pod is Ready

### Full command reference (copy/paste)
See `scripts/commands.bat`. It lists Docker build/push, MongoDB deploy (ephemeral or PVC), seeding, API deploy, exposure, testing, and cleanup, as commented commands you can copy into your terminal.

### License
Educational use only.

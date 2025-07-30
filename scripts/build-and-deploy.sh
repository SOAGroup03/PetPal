# Google Cloud Configuration
PROJECT_ID="petpal-467223"
REGION="us-central1"
CLUSTER_NAME="petpal-cluster"

echo "🚀 Starting PetPal deployment to Google Cloud..."

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling required Google Cloud APIs..."
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Authenticate Docker with GCR
gcloud auth configure-docker

# Create GKE cluster if it doesn't exist
echo "🏗️ Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --num-nodes=3 \
    --machine-type=e2-standard-2 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10 \
    --enable-network-policy \
    --enable-ip-alias \
    --disk-size=50GB

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Build and push Docker images
echo "🐳 Building and pushing Docker images..."

docker build -t gcr.io/$PROJECT_ID/user-service:latest ./microservices/user-service/
docker push gcr.io/$PROJECT_ID/user-service:latest

docker build -t gcr.io/$PROJECT_ID/pet-service:latest ./microservices/pet-service/
docker push gcr.io/$PROJECT_ID/pet-service:latest

docker build -t gcr.io/$PROJECT_ID/appointment-service:latest ./microservices/appointment-service/
docker push gcr.io/$PROJECT_ID/appointment-service:latest

docker build -t gcr.io/$PROJECT_ID/medical-service:latest ./microservices/medical-service/
docker push gcr.io/$PROJECT_ID/medical-service:latest

docker build -t gcr.io/$PROJECT_ID/frontend:latest ./frontend/
docker push gcr.io/$PROJECT_ID/frontend:latest

# Deploy to Kubernetes
echo "☸️ Deploying to Kubernetes..."
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/user-service-deployment.yaml
kubectl apply -f kubernetes/pet-service-deployment.yaml
kubectl apply -f kubernetes/appointment-service-deployment.yaml
kubectl apply -f kubernetes/medical-service-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/prometheus-deployment.yaml
kubectl apply -f kubernetes/grafana-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/user-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/pet-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/appointment-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/medical-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n petpal

# Get external IPs
echo "🌐 Getting external IP addresses..."
kubectl get services -n petpal

echo ""
echo "✅ Deployment completed successfully!"
echo "📱 Frontend URL: http://$(kubectl get service frontend -n petpal -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "📊 Prometheus URL: http://$(kubectl get service prometheus -n petpal -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):9090"
echo "📈 Grafana URL: http://$(kubectl get service grafana -n petpal -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"
echo "🔐 Grafana Credentials: admin/petpal123"
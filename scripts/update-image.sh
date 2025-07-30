PROJECT_ID="petpal-467223"

echo "🔄 Building updated Docker images..."

# Build and push updated images
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

# Restart deployments to pull new images
echo "🔄 Restarting deployments..."
kubectl rollout restart deployment/user-service -n petpal
kubectl rollout restart deployment/pet-service -n petpal
kubectl rollout restart deployment/appointment-service -n petpal
kubectl rollout restart deployment/medical-service -n petpal
kubectl rollout restart deployment/frontend -n petpal

# Wait for rollout to complete
kubectl rollout status deployment/user-service -n petpal
kubectl rollout status deployment/pet-service -n petpal
kubectl rollout status deployment/appointment-service -n petpal
kubectl rollout status deployment/medical-service -n petpal
kubectl rollout status deployment/frontend -n petpal

echo "✅ Images updated and deployments restarted successfully!"
PROJECT_ID="petpal-467223"
REGION="us-central1"
CLUSTER_NAME="petpal-cluster"

echo "🧹 Cleaning up PetPal resources..."

# Delete Kubernetes resources
kubectl delete namespace petpal

# Delete GKE cluster
gcloud container clusters delete $CLUSTER_NAME --region=$REGION --quiet

# Delete Docker images
echo "🗑️ Deleting Docker images..."
gcloud container images delete gcr.io/$PROJECT_ID/user-service:latest --quiet
gcloud container images delete gcr.io/$PROJECT_ID/pet-service:latest --quiet
gcloud container images delete gcr.io/$PROJECT_ID/appointment-service:latest --quiet
gcloud container images delete gcr.io/$PROJECT_ID/medical-service:latest --quiet
gcloud container images delete gcr.io/$PROJECT_ID/frontend:latest --quiet

echo "✅ Cleanup completed!"
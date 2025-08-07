#!/bin/bash

# PetPal Kubernetes Deployment Script
# This script deploys PetPal to a Kubernetes cluster

set -e

# Configuration
NAMESPACE="petpal"
KUBECTL_TIMEOUT="300s"

echo "🐾 Deploying PetPal to Kubernetes..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

echo "✅ kubectl is installed and cluster is accessible"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f kubernetes/namespace.yaml

# Deploy services
echo "🚀 Deploying services..."

# Deploy in dependency order
echo "   Deploying User Service..."
kubectl apply -f kubernetes/user-service.yaml

echo "   Waiting for User Service to be ready..."
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/user-service -n $NAMESPACE

echo "   Deploying Pet Service..."
kubectl apply -f kubernetes/pet-service.yaml

echo "   Waiting for Pet Service to be ready..."
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/pet-service -n $NAMESPACE

echo "   Deploying Appointment Service..."
kubectl apply -f kubernetes/appointment-service.yaml

echo "   Waiting for Appointment Service to be ready..."
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/appointment-service -n $NAMESPACE

echo "   Deploying Medical Service..."
kubectl apply -f kubernetes/medical-service.yaml

echo "   Waiting for Medical Service to be ready..."
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/medical-service -n $NAMESPACE

echo "   Deploying Frontend..."
kubectl apply -f kubernetes/frontend.yaml

echo "   Waiting for Frontend to be ready..."
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/frontend -n $NAMESPACE

# Deploy monitoring
echo "📊 Deploying monitoring stack..."
kubectl apply -f kubernetes/prometheus.yaml
kubectl apply -f kubernetes/grafana.yaml

echo "   Waiting for monitoring services to be ready..."
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/prometheus -n $NAMESPACE || true
kubectl wait --for=condition=available --timeout=$KUBECTL_TIMEOUT deployment/grafana -n $NAMESPACE || true

# Get service information
echo "🔍 Getting service information..."
echo ""
echo "📋 Deployed Services:"
kubectl get deployments -n $NAMESPACE
echo ""
echo "🌐 Service Endpoints:"
kubectl get services -n $NAMESPACE

# Get frontend external IP/URL
echo ""
echo "🎯 Frontend Access:"
FRONTEND_SERVICE=$(kubectl get service frontend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
if [ -n "$FRONTEND_SERVICE" ]; then
    echo "   Frontend URL: http://$FRONTEND_SERVICE:3000"
else
    echo "   Frontend URL: Use 'kubectl port-forward service/frontend 3000:3000 -n $NAMESPACE' for local access"
fi

# Display pod status
echo ""
echo "📦 Pod Status:"
kubectl get pods -n $NAMESPACE

# Check pod health
echo ""
echo "🔍 Checking pod health..."
UNHEALTHY_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
if [ -n "$UNHEALTHY_PODS" ]; then
    echo "⚠️  Unhealthy pods detected: $UNHEALTHY_PODS"
    echo "   Check logs with: kubectl logs <pod-name> -n $NAMESPACE"
else
    echo "✅ All pods are healthy"
fi

echo ""
echo "🎉 PetPal deployment completed!"
echo ""
echo "🔧 Useful commands:"
echo "   View pods:           kubectl get pods -n $NAMESPACE"
echo "   View services:       kubectl get services -n $NAMESPACE"
echo "   View logs:           kubectl logs -f deployment/<service-name> -n $NAMESPACE"
echo "   Port forward:        kubectl port-forward service/frontend 3000:3000 -n $NAMESPACE"
echo "   Delete deployment:   kubectl delete namespace $NAMESPACE"
echo ""
echo "📊 Monitoring:"
echo "   Prometheus:          kubectl port-forward service/prometheus 9090:9090 -n $NAMESPACE"
echo "   Grafana:            kubectl port-forward service/grafana 3001:3000 -n $NAMESPACE"
echo ""

# Optional: Open frontend if on macOS/Linux with xdg-open or open
if command -v open &> /dev/null && [ -n "$FRONTEND_SERVICE" ]; then
    echo "🌍 Opening frontend in browser..."
    open "http://$FRONTEND_SERVICE:3000"
elif command -v xdg-open &> /dev/null && [ -n "$FRONTEND_SERVICE" ]; then
    echo "🌍 Opening frontend in browser..."
    xdg-open "http://$FRONTEND_SERVICE:3000"
fi
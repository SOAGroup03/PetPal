#!/bin/bash
# scripts/deploy-local-k8s.sh - Deploy to local Kubernetes

set -e

echo "🚀 Deploying PetPal to local Kubernetes cluster..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

# Check if we have a Kubernetes cluster
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ No Kubernetes cluster found. Please start minikube or Docker Desktop Kubernetes"
    echo "To start minikube: minikube start"
    echo "To enable Docker Desktop K8s: Docker Desktop > Settings > Kubernetes > Enable"
    exit 1
fi

echo "✅ Kubernetes cluster found"

# Get current context
CONTEXT=$(kubectl config current-context)
echo "📍 Using context: $CONTEXT"

# Build Docker images locally
echo "🐳 Building Docker images..."

# Build all services
docker build -t petpal/user-service:latest ./microservices/user-service/ || {
    echo "❌ Failed to build user-service"
    exit 1
}

docker build -t petpal/pet-service:latest ./microservices/pet-service/ || {
    echo "❌ Failed to build pet-service"
    exit 1
}

docker build -t petpal/appointment-service:latest ./microservices/appointment-service/ || {
    echo "❌ Failed to build appointment-service"
    exit 1
}

docker build -t petpal/medical-service:latest ./microservices/medical-service/ || {
    echo "❌ Failed to build medical-service"
    exit 1
}

docker build -t petpal/frontend:latest ./frontend/ || {
    echo "❌ Failed to build frontend"
    exit 1
}

echo "✅ All Docker images built successfully"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: petpal
EOF

# Create secrets
echo "🔐 Creating secrets..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: petpal-secrets
  namespace: petpal
type: Opaque
data:
  # mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/petpal
  mongo-uri: bW9uZ29kYitzcnY6Ly9hY3N1amFuNjk6cGV0cGFsMTIzQHBldHBhbC45azZkOXF1Lm1vbmdvZGIubmV0L3BldHBhbA==
  # petpal-secret-key-2024
  secret-key: cGV0cGFsLXNlY3JldC1rZXktMjAyNA==
EOF

# Deploy User Service
echo "👤 Deploying User Service..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: petpal/user-service:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 5001
        env:
        - name: MONGO_URI
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: mongo-uri
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: petpal
spec:
  selector:
    app: user-service
  ports:
  - port: 5001
    targetPort: 5001
  type: ClusterIP
EOF

# Deploy Pet Service
echo "🐕 Deploying Pet Service..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pet-service
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pet-service
  template:
    metadata:
      labels:
        app: pet-service
    spec:
      containers:
      - name: pet-service
        image: petpal/pet-service:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 5002
        env:
        - name: MONGO_URI
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: mongo-uri
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: pet-service
  namespace: petpal
spec:
  selector:
    app: pet-service
  ports:
  - port: 5002
    targetPort: 5002
  type: ClusterIP
EOF

# Deploy Appointment Service
echo "📅 Deploying Appointment Service..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: appointment-service
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: appointment-service
  template:
    metadata:
      labels:
        app: appointment-service
    spec:
      containers:
      - name: appointment-service
        image: petpal/appointment-service:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 5003
        env:
        - name: MONGO_URI
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: mongo-uri
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: appointment-service
  namespace: petpal
spec:
  selector:
    app: appointment-service
  ports:
  - port: 5003
    targetPort: 5003
  type: ClusterIP
EOF

# Deploy Medical Service
echo "🏥 Deploying Medical Service..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medical-service
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: medical-service
  template:
    metadata:
      labels:
        app: medical-service
    spec:
      containers:
      - name: medical-service
        image: petpal/medical-service:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 5004
        env:
        - name: MONGO_URI
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: mongo-uri
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: medical-service
  namespace: petpal
spec:
  selector:
    app: medical-service
  ports:
  - port: 5004
    targetPort: 5004
  type: ClusterIP
EOF

# Deploy Frontend
echo "🌐 Deploying Frontend..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: petpal/frontend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 5000
        env:
        - name: USER_SERVICE_URL
          value: "http://user-service:5001"
        - name: PET_SERVICE_URL
          value: "http://pet-service:5002"
        - name: APPOINTMENT_SERVICE_URL
          value: "http://appointment-service:5003"
        - name: MEDICAL_SERVICE_URL
          value: "http://medical-service:5004"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: petpal-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: petpal
spec:
  selector:
    app: frontend
  ports:
  - port: 5000
    targetPort: 5000
  type: LoadBalancer
EOF

# Deploy Prometheus
echo "📊 Deploying Prometheus..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: petpal
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'user-service'
      static_configs:
      - targets: ['user-service:5001']
    - job_name: 'pet-service'
      static_configs:
      - targets: ['pet-service:5002']
    - job_name: 'appointment-service'
      static_configs:
      - targets: ['appointment-service:5003']
    - job_name: 'medical-service'
      static_configs:
      - targets: ['medical-service:5004']
    - job_name: 'frontend'
      static_configs:
      - targets: ['frontend:5000']
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus/prometheus.yml
          subPath: prometheus.yml
        args:
        - '--config.file=/etc/prometheus/prometheus.yml'
        - '--storage.tsdb.path=/prometheus'
        - '--web.console.libraries=/usr/share/prometheus/console_libraries'
        - '--web.console.templates=/usr/share/prometheus/consoles'
        - '--web.enable-lifecycle'
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: petpal
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: LoadBalancer
EOF

# Deploy Grafana
echo "📈 Deploying Grafana..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: petpal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "petpal123"
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: petpal
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
EOF

echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/user-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/pet-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/appointment-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/medical-service -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n petpal
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n petpal

echo ""
echo "✅ PetPal deployed successfully to local Kubernetes!"
echo ""
echo "📋 Deployment Summary:"
echo "===================="
kubectl get pods -n petpal
echo ""
kubectl get services -n petpal
echo ""
echo "🌐 Access URLs:"
echo "Frontend: http://localhost:$(kubectl get service frontend -n petpal -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo '5000')"
echo "Prometheus: http://localhost:$(kubectl get service prometheus -n petpal -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo '9090')"
echo "Grafana: http://localhost:$(kubectl get service grafana -n petpal -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo '3000') (admin/petpal123)"
echo ""
echo "🔍 To check status:"
echo "kubectl get pods -n petpal"
echo "kubectl get services -n petpal"
echo "kubectl logs -f deployment/frontend -n petpal"
# Todo Chatbot Phase 4

## Deployment Instructions

1. Install Minikube & Docker Desktop
2. Start Minikube:
   minikube start --driver=docker
3. Load Docker images into Minikube:
   minikube image load todo-backend:latest
   minikube image load todo-frontend:latest
4. Deploy Helm charts:
   helm upgrade --install backend backend-chart
   helm upgrade --install frontend frontend-chart
5. Access frontend:
   minikube service frontend-frontend-chart

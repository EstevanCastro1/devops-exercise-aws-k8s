# DevOps Exercise – AWS + Kubernetes

Este proyecto implementa un microservicio en **FastAPI** preparado para ejecutarse en un entorno moderno de **contenedores**, **Kubernetes**, **CI/CD** y **Terraform**.  
Incluye todo lo necesario para construir, probar, desplegar y operar la API en AWS ECR/EKS.

---

## Tabla de contenido

- [Arquitectura](#arquitectura)
- [Requisitos previos](#requisitos-previos)
- [Instalación y entorno local](#instalación-y-entorno-local)
- [Ejecución de la API](#ejecución-de-la-api)
  - [Endpoint `/DevOps` (POST)](#endpoint-devops-post)
  - [Otros métodos `/DevOps` (GET/PUT/DELETE/PATCH)](#otros-métodos-devops-getputdeletepatch)
- [Pruebas](#pruebas)
- [Docker](#docker)
- [CI/CD con GitHub Actions](#cicd-con-github-actions)
- [Despliegue en Kubernetes](#despliegue-en-kubernetes)
- [Infraestructura con Terraform](#infraestructura-con-terraform)
- [Variables importantes y secretos](#variables-importantes-y-secretos)

---

## Arquitectura

- **Aplicación**
  - Framework: FastAPI (`app/main.py`)
  - Servidor: uvicorn
- **Pruebas**: pytest (`tests/`)
- **Calidad de código**: flake8
- **Contenedor**: Dockerfile basado en `python:3.13-slim`
- **Orquestación**: Kubernetes (manifiestos en `k8s/`)
- **Infraestructura**: Terraform (AWS VPC + EKS)
- **CI/CD**: GitHub Actions (pipeline en `.github/workflows/ci-cd.yml`)

---

## Requisitos previos

### Local
- Python 3.11+
- pip
- virtualenv (opcional)

### Docker
- Docker Engine instalado

### AWS / Kubernetes
- Cuenta de AWS
- Credenciales configuradas (`aws configure`)
- kubectl
- terraform ≥ 1.8.0
- Repositorio ECR creado o permisos para crearlo

---

## Instalación y entorno local

```bash
git clone <url-del-repo>
cd devops-exercise-aws-k8s

python -m venv venv
source venv/bin/activate   # Linux/Mac
# .\venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## Ejecución de la API

### Ejecutar localmente

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en:  
`http://localhost:8000`

---

### Endpoint `/DevOps` (POST)

**Headers obligatorios**

```
X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c
X-JWT-KWY: <jwt>
Content-Type: application/json
```

**Body**

```json
{
  "message": "This is a test",
  "to": "Juan Perez",
  "from": "Rita Asturia",
  "timeToLifeSec": 45
}
```

**Respuesta**

```json
{
  "message": "Hello Juan Perez your message will be send"
}
```

### Otros métodos `/DevOps` (GET/PUT/DELETE/PATCH)

- Respuesta: `"ERROR"` (200 OK)

---

## Pruebas

```bash
pytest
```

Incluyen validación de:
- POST correcto
- Headers faltantes
- API Key inválida
- Otros métodos → `"ERROR"`

---

## Docker

Build de la imagen:

```bash
docker build -t devops-exercise-api:local .
```

Ejecutar contenedor:

```bash
docker run --rm -p 8000:8000 devops-exercise-api:local
```

---

## CI/CD con GitHub Actions

Pipeline ubicado en `.github/workflows/ci-cd.yml`.

Incluye:

### 1. build-and-test (todas las ramas)
- Instala dependencias
- Ejecuta flake8
- Ejecuta pytest

### 2. build-and-push-image (solo main)
- Login en AWS ECR
- Construcción de imagen
- Push a ECR

### 3. deploy (solo main)
- Configura kubectl para EKS
- Aplica namespace, deployment, service y HPA
- Actualiza la imagen del deployment

---

## Despliegue en Kubernetes

Archivos en `k8s/`:

- `namespace.yaml`
- `deployment.yaml`
- `service.yaml`
- `hpa.yaml`

Aplicación manual:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

---

## Infraestructura con Terraform

Carpeta `terraform/`:

- `main.tf` – VPC + EKS
- `variables.tf`
- `outputs.tf`

Uso:

```bash
terraform init
terraform plan
terraform apply
```

---

## Variables importantes y secretos

### En la aplicación
- API Key fija:
  ```
  2f5ae96c-b558-4c7b-a590-a501ae1c3f6c
  ```

### En GitHub Actions
Secretos:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`

Variables:

- `AWS_REGION`
- `ECR_REPOSITORY`
- `EKS_CLUSTER_NAME`
- `K8S_NAMESPACE`

---


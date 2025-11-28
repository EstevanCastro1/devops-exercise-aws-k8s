# DevOps Exercise – AWS + Kubernetes

Este proyecto es una API sencilla construida con **FastAPI** que expone un endpoint `/DevOps` y está preparada para un flujo completo de **CI/CD** con GitHub Actions, despliegue en **AWS ECR/EKS**, manifiestos de **Kubernetes** y **Terraform** para provisionar la infraestructura.

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

- **Aplicación**:
  - Framework: `FastAPI` (`app/main.py`)
  - Servidor ASGI: `uvicorn`
- **Tests**: `pytest` + `fastapi.testclient` (carpeta `tests/`)
- **Estático de código**: `flake8`
- **Contenedor**:
  - `Dockerfile` basado en `python:3.13-slim`
- **Orquestación**:
  - Manifiestos Kubernetes en `k8s/`:
    - `deployment.yaml`
    - `service.yaml`
    - `hpa.yaml`
    - `namespace.yaml`
- **Infraestructura**:
  - Terraform en `terraform/` para crear:
    - VPC
    - Subredes públicas/privadas
    - Cluster EKS (AWS)
- **CI/CD**:
  - Workflow GitHub Actions en `.github/workflows/ci-cd.yml`:
    - Build & test
    - Build y push de imagen a ECR
    - Deploy a EKS (Kubernetes)

---

## Requisitos previos

Para trabajar localmente:

- Python **3.11**+ (recomendado 3.11, usado en CI)
- `pip`
- (Opcional) `virtualenv` o similar

Para Docker:

- Docker Engine instalado

Para despliegue en AWS/EKS:

- Cuenta de AWS
- `awscli` configurado con credenciales válidas
- `kubectl` instalado
- `terraform` >= 1.8.0
- Repositorio ECR creado (o permisos para crearlo desde CI)

---

## Instalación y entorno local

1. Clonar el repositorio:

    git clone <url-del-repo>
    cd devops-exercise-aws-k8s

2. Crear y activar un entorno virtual (opcional pero recomendado):

    python -m venv venv
    source venv/bin/activate    # Linux/Mac
    # .\venv\Scripts\activate   # Windows

3. Instalar dependencias:

    pip install -r requirements.txt

---

## Ejecución de la API

### Ejecutar localmente con uvicorn

Desde la raíz del proyecto:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

La API quedará disponible en `http://localhost:8000`.

### Endpoint `/DevOps` (POST)

- **Ruta**: `POST /DevOps`
- **Headers obligatorios**:
  - `X-Parse-REST-API-Key`: debe ser exactamente `2f5ae96c-b558-4c7b-a590-a501ae1c3f6c`
  - `X-JWT-KWY`: token JWT (cualquier string no vacío para efectos de esta demo)
  - `Content-Type: application/json`
- **Body (JSON)**:

    {
      "message": "This is a test",
      "to": "Juan Perez",
      "from": "Rita Asturia",
      "timeToLifeSec": 45
    }

- **Respuesta OK (200)**:

    {
      "message": "Hello Juan Perez your message will be send"
    }

- **Errores**:
  - `401 Unauthorized` si `X-Parse-REST-API-Key` es distinto al esperado.
  - `400 Bad Request` si falta el header `X-JWT-KWY`.

### Otros métodos `/DevOps` (GET/PUT/DELETE/PATCH)

- **Rutas**:
  - `GET /DevOps`
  - `PUT /DevOps`
  - `DELETE /DevOps`
  - `PATCH /DevOps`
- **Respuesta**:
  - Código 200
  - Cuerpo: texto plano `"ERROR"`

---

## Pruebas

Las pruebas están en `tests/test_devops_endpoint.py`.

Para ejecutarlas:

    pytest

El pipeline de CI también ejecuta:

- `flake8 app tests`
- `pytest`

---

## Docker

### Build de la imagen

Desde la raíz del proyecto:

    docker build -t devops-exercise-api:local .

### Ejecutar el contenedor

    docker run --rm -p 8000:8000 devops-exercise-api:local

La API quedará disponible en `http://localhost:8000`.

---

## CI/CD con GitHub Actions

Workflow: `.github/workflows/ci-cd.yml`.

### 1. Job `build-and-test` (todas las ramas)

- Instala Python 3.11.
- Instala dependencias con `pip install -r requirements.txt`.
- Ejecuta:
  - `flake8 app tests`
  - `pytest`

### 2. Job `build-and-push-image` (solo `main`)

- Necesita `build-and-test`.
- Usa `aws-actions/configure-aws-credentials` para autenticarse en AWS.
- Hace login en ECR.
- Construye la imagen Docker y la etiqueta como:

    <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/devops-exercise-api:<GITHUB_SHA>

- Empuja la imagen a ECR.
- Exporta el `image_uri` como output.

### 3. Job `deploy` (solo `main`)

- Necesita `build-and-push-image`.
- Configura credenciales de AWS.
- Instala `kubectl`.
- Actualiza `kubeconfig` contra el cluster EKS (`devops-exercise-cluster`).
- Aplica:
  - `k8s/namespace.yaml`
  - Actualiza la imagen del deployment:

        kubectl set image deployment/devops-api devops-api=$IMAGE_URI -n devops-exercise

  - Aplica `k8s/service.yaml` y `k8s/hpa.yaml`.

---

## Despliegue en Kubernetes

Manifiestos ubicados en `k8s/`:

- `namespace.yaml`
  - Crea el namespace `devops-exercise`.
- `deployment.yaml`
  - `Deployment` `devops-api` con:
    - 2 réplicas iniciales.
    - Contenedor escuchando en el puerto `8000`.
    - Probes de liveness y readiness sobre `/DevOps`.
    - Requests/limits de CPU y memoria.
- `service.yaml`
  - `Service` tipo `LoadBalancer`:
    - Puerto `80` externo → `8000` interno.
- `hpa.yaml`
  - `HorizontalPodAutoscaler`:
    - Escala de 2 a 5 réplicas según uso de CPU (50% de media).

Aplicar manualmente (si ya tienes el cluster creado y `kubeconfig` configurado):

    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/hpa.yaml

---

## Infraestructura con Terraform

Archivos en `terraform/`:

- `main.tf`
  - Configura provider `aws` (región `var.aws_region`).
  - Usa módulo oficial `terraform-aws-modules/vpc/aws` para crear la VPC y subredes.
  - Usa módulo `terraform-aws-modules/eks/aws` para crear un cluster EKS:
    - Nombre: `<project_name>-cluster` (por defecto `devops-exercise-cluster`).
    - Versión: `var.cluster_version` (por defecto `1.30`).
    - Node group administrado con `t3.small`, min 1, max 3.
- `variables.tf`
  - `project_name` (default `devops-exercise`)
  - `aws_region` (default `us-east-1`)
  - CIDRs de subredes públicas y privadas.
- `outputs.tf`
  - Exporta:
    - `cluster_name`
    - `cluster_endpoint`
    - `cluster_certificate_authority_data`
    - `region`

### Uso básico de Terraform

Desde la carpeta `terraform/`:

    terraform init
    terraform plan
    terraform apply

Asegúrate de tener las credenciales de AWS configuradas (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).

---

## Variables importantes y secretos

### Constantes en la aplicación

En `app/main.py`:

- `API_KEY_HEADER = "X-Parse-REST-API-Key"`
- `API_KEY = "2f5ae96c-b558-4c7b-a590-a501ae1c3f6c"`

Estas se usan para validar el acceso al endpoint `/DevOps`.

### Variables de entorno / GitHub Actions

En `.github/workflows/ci-cd.yml`:

- Variables de entorno:
  - `AWS_REGION` (por defecto `us-east-1`)
  - `ECR_REPOSITORY` (`devops-exercise-api`)
  - `EKS_CLUSTER_NAME` (`devops-exercise-cluster`)
  - `K8S_NAMESPACE` (`devops-exercise`)
- Secretos requeridos:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_ACCOUNT_ID`

Estos secretos deben configurarse en **Settings > Secrets and variables > Actions** del repositorio de GitHub.

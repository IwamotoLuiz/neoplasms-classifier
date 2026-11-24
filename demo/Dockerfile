# Demonstração para dias de apresentação: API e interface na mesma porta.
# Construir a partir da raiz do repositório: docker build -f demo/Dockerfile -t tcc-demo .
FROM node:22 AS interface
WORKDIR /interface
COPY VueJS/classificador-melanoma/package.json VueJS/classificador-melanoma/package-lock.json ./
RUN npm ci
COPY VueJS/classificador-melanoma/ ./
RUN VITE_API_URL=/predict npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TORCH_HOME=/opt/torch
RUN pip install --no-cache-dir torch==2.15.0 torchvision==0.29.2 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir fastapi==0.165.0 starlette==1.10.0 "uvicorn[standard]==0.54.0" python-multipart pillow
# O model_load.py pede os pesos da ImageNet ao iniciar; ficam na imagem para não depender da internet
RUN python -c "from torchvision import models; models.efficientnet_v2_s(weights='DEFAULT')"
WORKDIR /app
COPY Backend/main.py ./
COPY Backend/Model/model_load.py Backend/Model/neoplasm_classifier.pth ./Model/
COPY demo/servidor.py ./
COPY --from=interface /interface/dist ./interface
RUN chmod -R a+rX,go-w /app /opt/torch
USER nobody
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "servidor:app", "--host", "0.0.0.0", "--port", "8000"]

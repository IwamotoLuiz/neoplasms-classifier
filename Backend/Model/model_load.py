# backend/model/predictor.py

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from collections import OrderedDict

# Parâmetros globais
imgSize = 112
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Transforms
val_transformer = transforms.Compose([
    transforms.Resize(size=(imgSize, imgSize), antialias=True),
    transforms.CenterCrop(size=(imgSize, imgSize)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


# Função para carregar o modelo (carregado uma vez)
def load_model():
    model = models.efficientnet_v2_s(weights="DEFAULT")
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 1)

    # Corrige nomes se foi treinado com DataParallel
    state_dict = torch.load("model/neoplasm_classifier.pth", map_location=device)
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k.replace("module.", "")
        new_state_dict[name] = v

    model.load_state_dict(new_state_dict, strict=False)
    model.to(device)
    model.eval()

    return model


# Carrega uma vez ao importar o módulo
model = load_model()


#Função de predição principal
def predict_image(image: Image.Image) -> str:
    image = image.convert("RGB")
    tensor = val_transformer(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(tensor)
        prediction = torch.sigmoid(output).item()  # como é 1 saída (sigmóide)

    # Simples binarização (ajuste conforme necessidade)
    if prediction >= 0.5:
        return "Maligno"
    else:
        return "Benigno"

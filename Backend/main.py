from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from Model.model_load import label_for, predict_probability
from PIL import Image
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    print("📥 Recebendo imagem:", file.filename)
    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        print("🧠 Chamando modelo...")
        probability = predict_probability(image)
        prediction = label_for(probability)
        print("✅ Predição:", prediction)
        return {"prediction": prediction, "probability": probability}
    except Exception as e:
        print("❌ Erro no backend:", str(e))
        return {"prediction": "Erro interno no servidor"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from Model import model_load
from main import app

client = TestClient(app)


def png_bytes(color):
    buffer = io.BytesIO()
    Image.new("RGB", (224, 224), color).save(buffer, format="PNG")
    return buffer.getvalue()


def post_image(color):
    return client.post(
        "/predict", files={"file": ("lesion.png", png_bytes(color), "image/png")}
    )


COLORS = ["white", "black", (181, 120, 95), (70, 35, 25)]


@pytest.mark.parametrize("color", COLORS)
def test_predict_returns_malignant_probability(color):
    probability = post_image(color).json()["probability"]
    assert isinstance(probability, float)
    assert 0.0 <= probability <= 1.0


@pytest.mark.parametrize("color", COLORS)
def test_label_matches_probability(color):
    body = post_image(color).json()
    expected = "Maligno" if body["probability"] >= 0.5 else "Benigno"
    assert body["prediction"] == expected


@pytest.mark.parametrize(
    "probability,label",
    [(0.0, "Benigno"), (0.4999, "Benigno"), (0.5, "Maligno"), (1.0, "Maligno")],
)
def test_label_uses_cutoff_of_one_half(probability, label):
    assert model_load.label_for(probability) == label


def test_predict_image_still_returns_only_the_label():
    image = Image.new("RGB", (224, 224), "white")
    assert model_load.predict_image(image) in {"Maligno", "Benigno"}


def test_grayscale_image_is_accepted():
    buffer = io.BytesIO()
    Image.new("L", (300, 180), 128).save(buffer, format="PNG")
    response = client.post(
        "/predict", files={"file": ("gray.png", buffer.getvalue(), "image/png")}
    )
    assert 0.0 <= response.json()["probability"] <= 1.0


def test_invalid_file_keeps_error_message_without_probability():
    response = client.post(
        "/predict", files={"file": ("notes.txt", b"not an image", "text/plain")}
    )
    assert response.status_code == 200
    assert response.json() == {"prediction": "Erro interno no servidor"}

import pytest
from fastapi.testclient import TestClient

from servidor import app

client = TestClient(app)


def classify(name):
    image = client.get(f"/amostras/{name}").content
    return client.post("/predict", files={"file": (name, image, "image/jpeg")}).json()


def test_root_serves_the_compiled_interface():
    response = client.get("/")
    assert response.status_code == 200
    assert "Classificação de neoplasmas cutâneos" in response.text


def test_interface_calls_the_api_on_the_same_address():
    page = client.get("/").text
    script = page.split('src="/assets/')[1].split('"')[0]
    code = client.get(f"/assets/{script}").text
    assert 'VITE_API_URL:"/predict"' in code


def test_ping_still_answers():
    assert client.get("/ping").json() == {"message": "pong"}


@pytest.mark.parametrize("name", ["amostra-1.jpg", "amostra-2.jpg"])
def test_samples_are_served_as_jpeg(name):
    response = client.get(f"/amostras/{name}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


def test_samples_cover_both_results():
    benign, malignant = classify("amostra-1.jpg"), classify("amostra-2.jpg")
    assert benign["prediction"] == "Benigno" and benign["probability"] < 0.01
    assert malignant["prediction"] == "Maligno" and malignant["probability"] > 0.99


def test_unknown_path_is_not_found():
    assert client.get("/nao-existe").status_code == 404

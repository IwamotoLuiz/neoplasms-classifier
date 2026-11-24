"""Serve a API e a interface compilada na mesma porta, para as apresentações."""
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from main import app

# Montada por último: /predict e /ping continuam respondendo pela API
app.mount("/", StaticFiles(directory=Path(__file__).parent / "interface", html=True), name="interface")

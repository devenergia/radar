"""
API 3 - Quantitativo de Demandas Diversas

PLACEHOLDER - Implementacao futura (Etapa 3)
Prazo ANEEL: Maio/2026
"""

from fastapi import FastAPI

app = FastAPI(
    title="RADAR API - Demandas Diversas",
    description="[PLACEHOLDER] API para quantitativo agregado de demandas",
    version="0.0.1",
)


@app.get("/")
async def root() -> dict:
    return {
        "api": "RADAR - Demandas Diversas",
        "status": "placeholder",
        "prazo_aneel": "Maio/2026",
    }


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()

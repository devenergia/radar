"""
API 2 - Dados de Demanda

PLACEHOLDER - Implementacao futura (Etapa 2)
Prazo ANEEL: Abril/2026
"""

from fastapi import FastAPI

app = FastAPI(
    title="RADAR API - Dados de Demanda",
    description="[PLACEHOLDER] API para consulta de dados de uma demanda especifica",
    version="0.0.1",
)


@app.get("/")
async def root() -> dict:
    return {
        "api": "RADAR - Dados de Demanda",
        "status": "placeholder",
        "prazo_aneel": "Abril/2026",
    }


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()

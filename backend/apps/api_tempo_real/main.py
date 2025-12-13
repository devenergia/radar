"""
API 4 - Tempo Real (REN 1.137 Art. 113)

PLACEHOLDER - Aguardando especificacoes da ANEEL (Etapa 4)
Prazo ANEEL: 60 dias apos instrucoes
"""

from fastapi import FastAPI

app = FastAPI(
    title="RADAR API - Tempo Real",
    description="[PLACEHOLDER] API para extracao de dados em tempo real pela ANEEL",
    version="0.0.1",
)


@app.get("/")
async def root() -> dict:
    return {
        "api": "RADAR - Tempo Real",
        "status": "placeholder",
        "prazo_aneel": "60 dias apos instrucoes da ANEEL",
        "base_legal": "REN 1.137/2025 - Art. 113",
    }


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)


if __name__ == "__main__":
    main()

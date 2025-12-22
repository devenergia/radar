# Plano de Implementacao: Mapa de Interrupcoes Roraima

**Data:** 2025-12-19
**Status:** Planejado
**Base Legal:** REN 1.137/2025 - Art. 106-107
**Prazo:** 180 dias apos vigencia (2026)
**Referencia:** [PowerOutage.us](https://poweroutage.us/)

---

## IMPORTANTE: Obrigatoriedade e Arquitetura

### Este Mapa e OBRIGATORIO

O Portal Publico de Interrupcoes e uma **exigencia legal** da REN 1.137/2025 (Art. 106-107).
Prazo: 180 dias apos vigencia (~28/04/2026).
Penalidade: Grupo III - Deixar de prestar informacoes de interrupcoes aos consumidores.

### Relacao com a API de Interrupcoes

O Mapa **NAO e um projeto separado** - e uma aplicacao dentro do mesmo backend que
**DEVE usar os mesmos dados** da API de Interrupcoes (RAD-100 a RAD-130).

Ambos consultam a mesma fonte: Oracle/DBLink (INSERVICE.AGENCY_EVENT).

A diferenca esta no **consumidor**:
- API ANEEL: sistemas (JSON REST com autenticacao API Key)
- Mapa Publico: pessoas (interface web sem autenticacao)

### Estrutura no Projeto

```
backend/
  apps/
    api_interrupcoes/      # API para ANEEL (RAD-100 a RAD-130)
    mapa_interrupcoes/     # Mapa Publico (RAD-200 a RAD-230)
  shared/                  # Codigo compartilhado (REUTILIZADO)
    domain/                # Value Objects, Entities, Repositories
    infrastructure/        # Oracle Connection, Cache
frontend/
  mapa-interrupcoes/       # React + Leaflet
```

### Codigo Reutilizado do shared/

- Value Objects: CodigoIBGE (RAD-100), TipoInterrupcao (RAD-101)
- Infrastructure: Oracle Connection (RAD-108), Cache (RAD-110)
- Repositories: InterrupcaoRepository (consulta mesma fonte de dados)
- Logica de agregacao de interrupcoes

### Por que Apps Separadas?

A separacao em `apps/` diferentes segue Clean Architecture porque:
1. Endpoints diferentes (rotas, autenticacao, formato de resposta)
2. Consumidores diferentes (sistemas ANEEL vs publico geral)
3. Requisitos nao-funcionais diferentes (rate limit, cache, etc.)
4. Mas compartilham o mesmo dominio e infraestrutura

---

## Visao Geral

Portal publico com mapa interativo de interrupcoes de fornecimento de energia eletrica no estado de Roraima, seguindo os requisitos da REN 1.137/2025 e o modelo de referencia PowerOutage.us.

### Objetivos

1. Transparencia para consumidores e poder publico
2. Mapa georreferenciado dos 15 municipios de Roraima
3. Dashboard com metricas em tempo real
4. Atualizacao a cada 30 minutos (Art. 107)
5. Acesso publico sem autenticacao

---

## Stack Tecnica

| Componente | Tecnologia |
|------------|------------|
| Frontend | React + TypeScript |
| Mapas | Leaflet + GeoJSON |
| Graficos | Recharts |
| Backend | FastAPI (Python 3.11+) |
| Banco de Dados | Oracle 19c (via DBLink) |
| Cache | Redis |
| Scheduler | Celery Beat |

---

## Requisitos REN 1.137/2025

### Art. 106 - Portal Publico

- [ ] Mapa georreferenciado de Roraima
- [ ] Informacoes de interrupcoes ativas
- [ ] Acesso publico sem autenticacao
- [ ] Atualizacao a cada 30 minutos

### Art. 107 - Conteudo Obrigatorio

| Requisito | Descricao | Task |
|-----------|-----------|------|
| Faixas de duracao | <1h, 1-3h, 3-6h, 6-12h, 12-24h, 24-48h, >48h | RAD-201 |
| UCs por faixa | Quantidade de UCs afetadas | RAD-202 |
| Status ocorrencia | Em preparacao / Deslocamento / Em execucao | RAD-203 |
| CHI | Consumidor Hora Interrompido | RAD-204 |
| Equipes em campo | Quantidade de equipes | RAD-205 |

---

## Tasks de Implementacao

### Fase 1: Backend - Domain Layer (RAD-200 a RAD-204)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-200 | Value Object FaixaDuracao | Alta | [RAD-200.md](./RAD-200.md) |
| RAD-201 | Value Object StatusOcorrencia | Alta | [RAD-201.md](./RAD-201.md) |
| RAD-202 | Value Object Coordenadas (Lat/Lng) | Alta | [RAD-202.md](./RAD-202.md) |
| RAD-203 | Entity InterrupcaoMapa | Alta | [RAD-203.md](./RAD-203.md) |
| RAD-204 | Domain Service CalculadorCHI | Alta | [RAD-204.md](./RAD-204.md) |

### Fase 2: Backend - Application Layer (RAD-205 a RAD-207)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-205 | Protocol MapaRepository | Alta | [RAD-205.md](./RAD-205.md) |
| RAD-206 | Use Case GetInterrupcoesMapa | Alta | [RAD-206.md](./RAD-206.md) |
| RAD-207 | Use Case GetEquipesEmCampo | Media | [RAD-207.md](./RAD-207.md) |

### Fase 3: Backend - Infrastructure Layer (RAD-208 a RAD-211)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-208 | Oracle MapaRepository | Alta | [RAD-208.md](./RAD-208.md) |
| RAD-209 | Materialized View MV_PORTAL_PUBLICO | Alta | [RAD-209.md](./RAD-209.md) |
| RAD-210 | Scheduler Celery (30 min) | Alta | [RAD-210.md](./RAD-210.md) |
| RAD-211 | GeoJSON dos Municipios Roraima | Alta | [RAD-211.md](./RAD-211.md) |

### Fase 4: Backend - API Endpoints (RAD-212 a RAD-215)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-212 | Schemas Pydantic (Mapa) | Alta | [RAD-212.md](./RAD-212.md) |
| RAD-213 | Endpoint GET /api/mapa/interrupcoes | Alta | [RAD-213.md](./RAD-213.md) |
| RAD-214 | Endpoint GET /api/mapa/municipios | Alta | [RAD-214.md](./RAD-214.md) |
| RAD-215 | Endpoint GET /api/mapa/estatisticas | Alta | [RAD-215.md](./RAD-215.md) |

### Fase 5: Frontend - Componentes (RAD-216 a RAD-222)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-216 | Setup React + TypeScript + Vite | Alta | [RAD-216.md](./RAD-216.md) |
| RAD-217 | Componente MapaRoraima (Leaflet) | Alta | [RAD-217.md](./RAD-217.md) |
| RAD-218 | Componente PainelEstatisticas | Alta | [RAD-218.md](./RAD-218.md) |
| RAD-219 | Componente ListaInterrupcoes | Media | [RAD-219.md](./RAD-219.md) |
| RAD-220 | Componente FiltroFaixaDuracao | Media | [RAD-220.md](./RAD-220.md) |
| RAD-221 | Componente GraficoEvolucao | Baixa | [RAD-221.md](./RAD-221.md) |
| RAD-222 | Layout Responsivo (Mobile) | Alta | [RAD-222.md](./RAD-222.md) |

### Fase 6: Integracao e Testes (RAD-223 a RAD-227)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-223 | Testes Unit - Value Objects | Critica | [RAD-223.md](./RAD-223.md) |
| RAD-224 | Testes Unit - Use Cases | Critica | [RAD-224.md](./RAD-224.md) |
| RAD-225 | Testes Integration - Repository | Critica | [RAD-225.md](./RAD-225.md) |
| RAD-226 | Testes E2E - Frontend | Alta | [RAD-226.md](./RAD-226.md) |
| RAD-227 | Testes Acessibilidade (WCAG) | Media | [RAD-227.md](./RAD-227.md) |

### Fase 7: Deploy e Operacao (RAD-228 a RAD-230)

| Task | Descricao | Prioridade | Arquivo |
|------|-----------|------------|---------|
| RAD-228 | Configuracao NGINX (SSL, Cache) | Alta | [RAD-228.md](./RAD-228.md) |
| RAD-229 | Monitoramento (Health Check) | Alta | [RAD-229.md](./RAD-229.md) |
| RAD-230 | Documentacao Usuario Final | Media | [RAD-230.md](./RAD-230.md) |

---

## Grafo de Dependencias

```
RAD-200 (FaixaDuracao)
RAD-201 (StatusOcorrencia)
RAD-202 (Coordenadas)
    |
    +---> RAD-203 (Entity InterrupcaoMapa)
    |         |
    +---> RAD-204 (CalculadorCHI)
              |
              +---> RAD-205 (Protocol MapaRepository)
              |         |
              |         +---> RAD-206 (Use Case GetInterrupcoesMapa)
              |         |
              |         +---> RAD-207 (Use Case GetEquipesEmCampo)
              |
              +---> RAD-208 (Oracle MapaRepository)
              |         |
              |         +---> RAD-209 (Materialized View)
              |
              +---> RAD-210 (Scheduler Celery)
              |
              +---> RAD-211 (GeoJSON Municipios)
                        |
                        +---> RAD-212 (Schemas Pydantic)
                        |         |
                        |         +---> RAD-213 a RAD-215 (Endpoints)
                        |
                        +---> RAD-216 (Setup React)
                                  |
                                  +---> RAD-217 a RAD-222 (Componentes)
                                            |
                                            +---> RAD-223 a RAD-227 (Testes)
                                                      |
                                                      +---> RAD-228 a RAD-230 (Deploy)
```

---

## Mapa de Roraima - 15 Municipios

```
                    VENEZUELA
        ┌─────────────────────────────────┐
        │         (4) UIRAMUTA            │
        │    ┌───────────────────┐        │
        │    │ (3) PACARAIMA     │        │
   G    │    │    ┌─────────┐    │   G    │
   U    │    │    │  (2)    │    │   U    │
   I    │ ┌──┴────┤ AMAJARI ├────┴──┐ I    │
   A    │ │       └─────────┘       │ A    │
   N    │ │  (5)      (6)      (7)  │ N    │
   A    │ │NORMANDIA  BOA    BONFIM │ A    │
        │ │           VISTA         │      │
        │ │  ┌────────┬────────┐   │      │
        │ │  │   (8)  │  (9)   │   │      │
        │ │  │ ALTO   │ CANTA  │   │      │
        │ │  │ ALEGRE │        │   │      │
        │ │  ├────────┼────────┤   │      │
        │ │  │  (10)  │  (11)  │   │      │
        │ │  │MUCAJAI │IRACEMA │   │      │
        │ │  │        │        │   │      │
        │ │  ├────────┼────────┤   │      │
        │ │  │  (12)  │  (13)  │   │      │
        │ │  │CARACARAI│ CAROEBE│   │      │
        │ │  │        │        │   │      │
        │ │  ├────────┴────────┤   │      │
        │ │  │      (14)       │   │      │
        │ │  │  RORAINOPOLIS   │   │      │
        │ │  │  ┌──────────┐   │   │      │
        │ │  │  │(15) S.JOAO│   │   │      │
        │ └──┴──┤  BALIZA   ├───┴───┘      │
        │       │(16)S.LUIZ │              │
        └───────┴───────────┴──────────────┘
                    AMAZONAS
```

| # | Municipio | Codigo IBGE | Latitude | Longitude |
|---|-----------|-------------|----------|-----------|
| 1 | Boa Vista | 1400100 | 2.8235 | -60.6758 |
| 2 | Amajari | 1400027 | 3.6481 | -61.3656 |
| 3 | Pacaraima | 1400456 | 4.4797 | -61.1478 |
| 4 | Uiramuta | 1400704 | 4.5972 | -60.1844 |
| 5 | Normandia | 1400407 | 3.8797 | -59.6225 |
| 6 | Bonfim | 1400159 | 3.3614 | -59.8331 |
| 7 | Alto Alegre | 1400050 | 2.9889 | -61.3114 |
| 8 | Canta | 1400175 | 2.6097 | -60.5986 |
| 9 | Mucajai | 1400308 | 2.4336 | -60.9125 |
| 10 | Iracema | 1400282 | 2.1831 | -61.0450 |
| 11 | Caracarai | 1400209 | 1.8267 | -61.1278 |
| 12 | Caroebe | 1400233 | 0.8842 | -59.6958 |
| 13 | Rorainopolis | 1400472 | 0.9419 | -60.4394 |
| 14 | Sao Joao da Baliza | 1400506 | 1.0256 | -59.9089 |
| 15 | Sao Luiz | 1400605 | 1.0131 | -60.0392 |

---

## Faixas de Duracao (Art. 107)

| Faixa | Condicao | Cor Heat Map |
|-------|----------|--------------|
| < 1 hora | duracao_horas < 1 | Verde |
| 1 a 3 horas | 1 <= duracao < 3 | Verde Claro |
| 3 a 6 horas | 3 <= duracao < 6 | Amarelo |
| 6 a 12 horas | 6 <= duracao < 12 | Laranja |
| 12 a 24 horas | 12 <= duracao < 24 | Laranja Escuro |
| 24 a 48 horas | 24 <= duracao < 48 | Vermelho |
| > 48 horas | duracao >= 48 | Vermelho Escuro |

---

## Status de Ocorrencia (Art. 107)

| Status | Descricao | Icone |
|--------|-----------|-------|
| EM_PREPARACAO | Equipe sendo designada | Relogio |
| DESLOCAMENTO | Equipe a caminho | Caminhao |
| EM_EXECUCAO | Trabalho em andamento | Ferramentas |
| CONCLUIDA | Energia restabelecida | Check Verde |

---

## Formato de Resposta API

### GET /api/mapa/interrupcoes

```json
{
  "dataAtualizacao": "2025-12-19T14:30:00-04:00",
  "totalInterrupcoes": 15,
  "totalUCsAfetadas": 2500,
  "chiTotal": 5200.5,
  "interrupcoes": [
    {
      "id": "INT-001",
      "municipio": {
        "codigoIbge": 1400100,
        "nome": "Boa Vista"
      },
      "coordenadas": {
        "latitude": 2.8235,
        "longitude": -60.6758
      },
      "faixaDuracao": "1a3h",
      "ucsAfetadas": 500,
      "chi": 850.5,
      "status": "EM_EXECUCAO",
      "equipesDesignadas": 2,
      "causa": "Descarga atmosferica",
      "causaConhecida": true,
      "previsaoRestabelecimento": "2025-12-19T16:00:00-04:00"
    }
  ]
}
```

### GET /api/mapa/estatisticas

```json
{
  "dataAtualizacao": "2025-12-19T14:30:00-04:00",
  "porFaixa": {
    "ate1h": 5,
    "1a3h": 3,
    "3a6h": 2,
    "6a12h": 2,
    "12a24h": 1,
    "24a48h": 1,
    "mais48h": 1
  },
  "porMunicipio": [
    {"codigoIbge": 1400100, "nome": "Boa Vista", "interrupcoes": 8, "ucsAfetadas": 1500},
    {"codigoIbge": 1400209, "nome": "Caracarai", "interrupcoes": 3, "ucsAfetadas": 400}
  ],
  "equipesEmCampo": {
    "total": 12,
    "disponiveis": 3,
    "emDeslocamento": 4,
    "emCampo": 5
  }
}
```

---

## Metricas de Qualidade

| Metrica | Meta | Bloqueante |
|---------|------|------------|
| Coverage de Testes | >= 80% | Sim |
| Tempo de Carregamento | < 3s | Sim |
| Atualizacao | 30 min | Sim (REN 1.137) |
| Acessibilidade | WCAG 2.1 AA | Sim |
| Mobile Responsivo | 100% | Sim |

---

## Referencias

### Documentacao Interna
- [VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md](../VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md)
- [DIAGRAMAS_MERMAID_RADAR_RR.md](../../design/DIAGRAMAS_MERMAID_RADAR_RR.md) - Diagrama 17 (Dashboard PowerOutage Style)
- [DESIGN_ARQUITETURA_RADAR_RR.md](../../design/DESIGN_ARQUITETURA_RADAR_RR.md) - Secao 5 (Portal Publico)
- [RELATORIO_COMPARATIVO_POWEROUTAGE_US.md](../../reports/RELATORIO_COMPARATIVO_POWEROUTAGE_US.md)

### Regulamentacao
- REN 1.137/2025 - Art. 106-107 (Portal Publico)

---

**Proximo Passo:** Ver [INDEX.md](./INDEX.md) para navegacao detalhada das tasks.

# Indice de Tasks - Mapa de Interrupcoes Roraima

**Projeto:** RADAR - Portal Publico de Interrupcoes
**Total de Tasks:** 31 (RAD-200 a RAD-230)
**Base Legal:** REN 1.137/2025 - Art. 106-107
**Referencia:** [PowerOutage.us](https://poweroutage.us/)

---

## Navegacao Rapida

| Documento | Descricao |
|-----------|-----------|
| [PLAN.md](./PLAN.md) | Plano geral de implementacao |
| [../VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md](../VISIBILIDADE_INTEGRADA_PROJETO_RADAR.md) | Visao completa do projeto |

---

## Fase 1: Backend - Domain Layer

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-200 | Value Object FaixaDuracao | PENDENTE | Alta |
| RAD-201 | Value Object StatusOcorrencia | PENDENTE | Alta |
| RAD-202 | Value Object Coordenadas (Lat/Lng) | PENDENTE | Alta |
| RAD-203 | Entity InterrupcaoMapa | PENDENTE | Alta |
| RAD-204 | Domain Service CalculadorCHI | PENDENTE | Alta |

### RAD-200: Value Object FaixaDuracao

**Objetivo:** Criar Value Object para classificar interrupcoes por faixa de duracao.

**Faixas (REN 1.137 Art. 107):**
- `ATE_1H` - Menos de 1 hora
- `DE_1_A_3H` - De 1 a 3 horas
- `DE_3_A_6H` - De 3 a 6 horas
- `DE_6_A_12H` - De 6 a 12 horas
- `DE_12_A_24H` - De 12 a 24 horas
- `DE_24_A_48H` - De 24 a 48 horas
- `MAIS_48H` - Mais de 48 horas

**Arquivo:** `backend/shared/domain/value_objects/faixa_duracao.py`

---

### RAD-201: Value Object StatusOcorrencia

**Objetivo:** Criar Value Object para status da ocorrencia.

**Status (REN 1.137 Art. 107):**
- `EM_PREPARACAO` - Equipe sendo designada
- `DESLOCAMENTO` - Equipe a caminho
- `EM_EXECUCAO` - Trabalho em andamento
- `CONCLUIDA` - Energia restabelecida

**Arquivo:** `backend/shared/domain/value_objects/status_ocorrencia.py`

---

### RAD-202: Value Object Coordenadas

**Objetivo:** Criar Value Object para coordenadas geograficas (Lat/Lng).

**Validacoes:**
- Latitude: -90 a +90
- Longitude: -180 a +180
- Dentro do estado de Roraima (aproximado)

**Arquivo:** `backend/shared/domain/value_objects/coordenadas.py`

---

### RAD-203: Entity InterrupcaoMapa

**Objetivo:** Criar Entity para representar interrupcao no mapa.

**Atributos:**
- id: str
- municipio: CodigoIBGE
- coordenadas: Coordenadas
- faixa_duracao: FaixaDuracao
- status: StatusOcorrencia
- ucs_afetadas: int
- chi: float
- equipes_designadas: int
- causa: str | None
- causa_conhecida: bool
- previsao_restabelecimento: datetime | None
- data_inicio: datetime

**Arquivo:** `backend/shared/domain/entities/interrupcao_mapa.py`

---

### RAD-204: Domain Service CalculadorCHI

**Objetivo:** Criar servico para calcular CHI (Consumidor Hora Interrompido).

**Formula:**
```
CHI = qtd_ucs_afetadas × duracao_horas
```

**Arquivo:** `backend/shared/domain/services/calculador_chi.py`

---

## Fase 2: Backend - Application Layer

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-205 | Protocol MapaRepository | PENDENTE | Alta |
| RAD-206 | Use Case GetInterrupcoesMapa | PENDENTE | Alta |
| RAD-207 | Use Case GetEquipesEmCampo | PENDENTE | Media |

---

## Fase 3: Backend - Infrastructure Layer

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-208 | Oracle MapaRepository | PENDENTE | Alta |
| RAD-209 | Materialized View MV_PORTAL_PUBLICO | PENDENTE | Alta |
| RAD-210 | Scheduler Celery (30 min) | PENDENTE | Alta |
| RAD-211 | GeoJSON dos Municipios Roraima | PENDENTE | Alta |

### RAD-211: GeoJSON dos Municipios Roraima

**Objetivo:** Criar arquivo GeoJSON com os limites geograficos dos 15 municipios.

**Fonte:** IBGE - Malhas Municipais 2023

**Arquivo:** `frontend/public/geojson/roraima-municipios.geojson`

---

## Fase 4: Backend - API Endpoints

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-212 | Schemas Pydantic (Mapa) | PENDENTE | Alta |
| RAD-213 | Endpoint GET /api/mapa/interrupcoes | PENDENTE | Alta |
| RAD-214 | Endpoint GET /api/mapa/municipios | PENDENTE | Alta |
| RAD-215 | Endpoint GET /api/mapa/estatisticas | PENDENTE | Alta |

---

## Fase 5: Frontend - Componentes React

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-216 | Setup React + TypeScript + Vite | PENDENTE | Alta |
| RAD-217 | Componente MapaRoraima (Leaflet) | PENDENTE | Alta |
| RAD-218 | Componente PainelEstatisticas | PENDENTE | Alta |
| RAD-219 | Componente ListaInterrupcoes | PENDENTE | Media |
| RAD-220 | Componente FiltroFaixaDuracao | PENDENTE | Media |
| RAD-221 | Componente GraficoEvolucao | PENDENTE | Baixa |
| RAD-222 | Layout Responsivo (Mobile) | PENDENTE | Alta |

### RAD-217: Componente MapaRoraima

**Objetivo:** Criar componente de mapa interativo usando Leaflet.

**Funcionalidades:**
- Renderizar GeoJSON dos municipios
- Heat map por severidade (cor)
- Popup com detalhes da interrupcao
- Zoom/Pan
- Localizacao do usuario (opcional)

**Bibliotecas:**
- `react-leaflet`
- `leaflet`

**Arquivo:** `frontend/src/components/MapaRoraima/MapaRoraima.tsx`

---

### RAD-218: Componente PainelEstatisticas

**Objetivo:** Criar painel com metricas principais.

**Metricas:**
- Total de interrupcoes ativas
- Total de UCs afetadas
- CHI total
- Equipes em campo
- Grafico por faixa de duracao

**Arquivo:** `frontend/src/components/PainelEstatisticas/PainelEstatisticas.tsx`

---

## Fase 6: Integracao e Testes

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-223 | Testes Unit - Value Objects | PENDENTE | Critica |
| RAD-224 | Testes Unit - Use Cases | PENDENTE | Critica |
| RAD-225 | Testes Integration - Repository | PENDENTE | Critica |
| RAD-226 | Testes E2E - Frontend | PENDENTE | Alta |
| RAD-227 | Testes Acessibilidade (WCAG) | PENDENTE | Media |

---

## Fase 7: Deploy e Operacao

| Task | Descricao | Status | Prioridade |
|------|-----------|--------|------------|
| RAD-228 | Configuracao NGINX (SSL, Cache) | PENDENTE | Alta |
| RAD-229 | Monitoramento (Health Check) | PENDENTE | Alta |
| RAD-230 | Documentacao Usuario Final | PENDENTE | Media |

---

## Resumo de Progresso

| Fase | Tasks | Concluidas | Progresso |
|------|-------|------------|-----------|
| Fase 1 - Domain | 5 | 0 | 0% |
| Fase 2 - Application | 3 | 0 | 0% |
| Fase 3 - Infrastructure | 4 | 0 | 0% |
| Fase 4 - API | 4 | 0 | 0% |
| Fase 5 - Frontend | 7 | 0 | 0% |
| Fase 6 - Testes | 5 | 0 | 0% |
| Fase 7 - Deploy | 3 | 0 | 0% |
| **TOTAL** | **31** | **0** | **0%** |

---

## Dependencias entre APIs

```
API 1 (Interrupcoes ANEEL)
    |
    +---> Mapa de Interrupcoes
          (Reutiliza Value Objects: CodigoIBGE, TipoInterrupcao)
          (Reutiliza Infrastructure: Oracle Connection, Cache)
```

**Tasks Compartilhadas:**
- RAD-100 (CodigoIBGE) -> RAD-203 (InterrupcaoMapa)
- RAD-101 (TipoInterrupcao) -> RAD-203 (InterrupcaoMapa)
- RAD-108 (Oracle Connection) -> RAD-208 (Oracle MapaRepository)
- RAD-110 (Memory Cache) -> RAD-210 (Scheduler)

---

## Checklist REN 1.137/2025

### Art. 106 - Portal Publico
- [ ] Mapa georreferenciado de Roraima
- [ ] Informacoes de interrupcoes ativas
- [ ] Acesso publico sem autenticacao
- [ ] Atualizacao a cada 30 minutos

### Art. 107 - Conteudo Obrigatorio
- [ ] Classificacao por faixa de duracao
- [ ] Quantidade de UCs por faixa
- [ ] Status de cada ocorrencia
- [ ] CHI (Consumidor Hora Interrompido)
- [ ] Quantidade de equipes em campo

---

**Proximo Passo:** Iniciar com RAD-200 (FaixaDuracao) e RAD-201 (StatusOcorrencia).

# Plano de Testes - API 1 (Quantitativo de Interrupções Ativas)

## 1. Informações do Documento

| Campo | Valor |
|-------|-------|
| **Projeto** | RADAR - Roraima Energia |
| **API** | API 1 - Quantitativo de Interrupções Ativas |
| **Versão** | 1.0.0 |
| **Data** | Dezembro 2025 |
| **Responsável** | Equipe RADAR |

## 2. Escopo

### 2.1 Objetivos

- Garantir conformidade com especificação ANEEL (Ofício Circular nº 14/2025-SFE/ANEEL)
- Validar funcionamento correto de todos os componentes
- Verificar integridade de dados e performance
- Assegurar segurança e resiliência da API

### 2.2 Funcionalidades Testadas

| ID | Funcionalidade | Prioridade |
|----|----------------|------------|
| F01 | Endpoint `/quantitativointerrupcoesativas` | Alta |
| F02 | Autenticação via API Key (x-api-key) | Alta |
| F03 | Rate Limiting (12 req/min) | Média |
| F04 | Cache de dados (5 minutos) | Média |
| F05 | Health Check `/health` | Alta |
| F06 | Formato de resposta ANEEL | Alta |

### 2.3 Fora do Escopo

- Testes de infraestrutura de rede
- Testes de banco de dados Oracle SISTEC (origem)
- Testes de frontend (não aplicável)

## 3. Estratégia de Testes

### 3.1 Pirâmide de Testes

```
                    ┌─────────┐
                    │   E2E   │  ← 10%
                   ─┴─────────┴─
                  ┌─────────────┐
                  │ Integration │  ← 30%
                 ─┴─────────────┴─
                ┌─────────────────┐
                │     Unit        │  ← 60%
                └─────────────────┘
```

### 3.2 Tipos de Teste

| Tipo | Descrição | Framework | Cobertura Mínima |
|------|-----------|-----------|------------------|
| Unit | Testes isolados de componentes | pytest | 80% |
| Integration | Testes de integração entre camadas | pytest-asyncio | 70% |
| E2E | Testes de ponta a ponta | pytest + httpx | N/A |
| Performance | Testes de carga e stress | Locust | N/A |
| Security | Testes de segurança | OWASP ZAP | N/A |

## 4. Casos de Teste

### 4.1 Testes Unitários - Domain Layer

#### 4.1.1 Value Objects

##### TC-VO-001: CodigoIBGE - Criação válida

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Código IBGE de Roraima válido |
| **Entrada** | `"1400050"` (Boa Vista) |
| **Resultado Esperado** | Value Object criado com sucesso |
| **Critério de Aceite** | `codigo_ibge.value == "1400050"` |

```python
def test_deve_criar_codigo_ibge_valido():
    codigo = CodigoIBGE("1400050")
    assert codigo.value == "1400050"
```

##### TC-VO-002: CodigoIBGE - Rejeição de código inválido

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Código com menos de 7 dígitos |
| **Entrada** | `"140005"` |
| **Resultado Esperado** | ValueError lançado |
| **Critério de Aceite** | Exceção com mensagem apropriada |

```python
def test_deve_rejeitar_codigo_ibge_com_digitos_insuficientes():
    with pytest.raises(ValueError, match="7 dígitos"):
        CodigoIBGE("140005")
```

##### TC-VO-003: CodigoIBGE - Rejeição de estado diferente de RR

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Código de outro estado |
| **Entrada** | `"1300000"` (Amazonas) |
| **Resultado Esperado** | ValueError lançado |
| **Critério de Aceite** | Mensagem indicando "Roraima" |

```python
def test_deve_rejeitar_codigo_ibge_fora_de_roraima():
    with pytest.raises(ValueError, match="Roraima"):
        CodigoIBGE("1300000")
```

##### TC-VO-004: TipoInterrupcao - Valores válidos

| Campo | Valor |
|-------|-------|
| **Entrada** | `1` (Programada) e `2` (Não Programada) |
| **Resultado Esperado** | Enum criado corretamente |

```python
@pytest.mark.parametrize("valor,esperado", [
    (1, TipoInterrupcao.PROGRAMADA),
    (2, TipoInterrupcao.NAO_PROGRAMADA),
])
def test_deve_criar_tipo_interrupcao_valido(valor, esperado):
    tipo = TipoInterrupcao(valor)
    assert tipo == esperado
```

##### TC-VO-005: TipoInterrupcao - Valor inválido

| Campo | Valor |
|-------|-------|
| **Entrada** | `3` |
| **Resultado Esperado** | ValueError lançado |

```python
def test_deve_rejeitar_tipo_interrupcao_invalido():
    with pytest.raises(ValueError):
        TipoInterrupcao(3)
```

#### 4.1.2 Entities

##### TC-ENT-001: Interrupcao - Criação válida

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Todos os campos válidos |
| **Resultado Esperado** | Entity criada |

```python
def test_deve_criar_interrupcao_valida():
    interrupcao = Interrupcao(
        id=UUID("..."),
        municipio=CodigoIBGE("1400050"),
        tipo=TipoInterrupcao.NAO_PROGRAMADA,
        quantidade_ucs=1500,
        quantidade_equipes=3,
        data_atualizacao=datetime.now(),
    )
    assert interrupcao.municipio.value == "1400050"
```

##### TC-ENT-002: Interrupcao - Igualdade por ID

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Duas interrupções com mesmo ID |
| **Resultado Esperado** | Igualdade retorna True |

```python
def test_interrupcoes_com_mesmo_id_sao_iguais():
    id_ = UUID("...")
    int1 = Interrupcao(id=id_, ...)
    int2 = Interrupcao(id=id_, ...)
    assert int1 == int2
```

### 4.2 Testes Unitários - Application Layer

#### 4.2.1 Use Cases

##### TC-UC-001: GetInterrupcoesAtivas - Sucesso com cache hit

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Dados em cache |
| **Resultado Esperado** | Retorna dados do cache, não consulta repositório |

```python
@pytest.mark.asyncio
async def test_deve_retornar_dados_do_cache():
    # Arrange
    cache_mock = Mock()
    cache_mock.get.return_value = cached_data
    repo_mock = Mock()
    use_case = GetInterrupcoesAtivasUseCase(repo_mock, cache_mock)

    # Act
    result = await use_case.execute()

    # Assert
    assert result.is_success
    repo_mock.buscar_ativas.assert_not_called()
```

##### TC-UC-002: GetInterrupcoesAtivas - Sucesso com cache miss

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Cache vazio |
| **Resultado Esperado** | Consulta repositório, atualiza cache |

```python
@pytest.mark.asyncio
async def test_deve_buscar_do_repositorio_e_atualizar_cache():
    # Arrange
    cache_mock = Mock()
    cache_mock.get.return_value = None
    repo_mock = Mock()
    repo_mock.buscar_ativas.return_value = [...]
    use_case = GetInterrupcoesAtivasUseCase(repo_mock, cache_mock)

    # Act
    result = await use_case.execute()

    # Assert
    assert result.is_success
    repo_mock.buscar_ativas.assert_called_once()
    cache_mock.set.assert_called_once()
```

##### TC-UC-003: GetInterrupcoesAtivas - Erro de repositório

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Repositório lança exceção |
| **Resultado Esperado** | Result.fail com mensagem de erro |

```python
@pytest.mark.asyncio
async def test_deve_retornar_falha_quando_repositorio_falha():
    # Arrange
    cache_mock = Mock()
    cache_mock.get.return_value = None
    repo_mock = Mock()
    repo_mock.buscar_ativas.side_effect = Exception("DB Error")
    use_case = GetInterrupcoesAtivasUseCase(repo_mock, cache_mock)

    # Act
    result = await use_case.execute()

    # Assert
    assert result.is_failure
    assert "DB Error" in result.error
```

### 4.3 Testes de Integração - Infrastructure Layer

#### 4.3.1 Repository

##### TC-REPO-001: OracleInterrupcaoRepository - Conexão

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Database de teste disponível |
| **Resultado Esperado** | Conexão estabelecida |

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_deve_conectar_ao_banco():
    async with get_test_session() as session:
        repo = OracleInterrupcaoRepository(session)
        # Executa query simples para verificar conexão
        result = await repo._session.execute(text("SELECT 1 FROM DUAL"))
        assert result.scalar() == 1
```

##### TC-REPO-002: OracleInterrupcaoRepository - Buscar ativas

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Dados de teste inseridos |
| **Resultado Esperado** | Lista de interrupções agregadas |

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_deve_buscar_interrupcoes_ativas():
    async with get_test_session() as session:
        repo = OracleInterrupcaoRepository(session)
        result = await repo.buscar_ativas()
        assert isinstance(result, list)
        # Verifica estrutura dos dados
        if result:
            assert hasattr(result[0], 'municipio')
            assert hasattr(result[0], 'tipo')
```

#### 4.3.2 Cache Service

##### TC-CACHE-001: RedisCacheService - Get/Set

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Redis de teste disponível |
| **Resultado Esperado** | Dados persistidos e recuperados |

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_deve_armazenar_e_recuperar_dados():
    cache = RedisCacheService(get_test_redis())

    await cache.set("test_key", {"data": "test"}, ttl=60)
    result = await cache.get("test_key")

    assert result == {"data": "test"}
```

##### TC-CACHE-002: RedisCacheService - TTL

| Campo | Valor |
|-------|-------|
| **Pré-condição** | Dados com TTL curto |
| **Resultado Esperado** | Dados expiram após TTL |

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_dados_devem_expirar_apos_ttl():
    cache = RedisCacheService(get_test_redis())

    await cache.set("test_key", {"data": "test"}, ttl=1)
    await asyncio.sleep(2)
    result = await cache.get("test_key")

    assert result is None
```

### 4.4 Testes E2E - API Endpoints

#### 4.4.1 Health Check

##### TC-E2E-001: Health Check - API saudável

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **URL** | `/health` |
| **Resultado Esperado** | 200, `{"status": "healthy"}` |

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_health_check_retorna_healthy():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### 4.4.2 Endpoint Principal

##### TC-E2E-002: Interrupções - Sucesso com autenticação

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **URL** | `/quantitativointerrupcoesativas` |
| **Headers** | `x-api-key: valid_key` |
| **Resultado Esperado** | 200, formato ANEEL |

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_endpoint_retorna_formato_aneel_com_auth():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": TEST_API_KEY}
        )

    assert response.status_code == 200
    data = response.json()
    assert "idcStatusRequisicao" in data
    assert "emailIndisponibilidade" in data
    assert "mensagem" in data
    assert "quantitativoInterrupcoesAtivas" in data
```

##### TC-E2E-003: Interrupções - Erro sem autenticação

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **URL** | `/quantitativointerrupcoesativas` |
| **Headers** | (sem x-api-key) |
| **Resultado Esperado** | 401, mensagem de erro |

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_endpoint_retorna_401_sem_api_key():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/quantitativointerrupcoesativas")

    assert response.status_code == 401
    data = response.json()
    assert data["idcStatusRequisicao"] == 2
```

##### TC-E2E-004: Interrupções - Erro com API key inválida

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **URL** | `/quantitativointerrupcoesativas` |
| **Headers** | `x-api-key: invalid_key` |
| **Resultado Esperado** | 401 |

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_endpoint_retorna_401_com_api_key_invalida():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": "chave_invalida"}
        )

    assert response.status_code == 401
```

##### TC-E2E-005: Rate Limiting

| Campo | Valor |
|-------|-------|
| **Método** | GET x 15 |
| **URL** | `/quantitativointerrupcoesativas` |
| **Resultado Esperado** | 429 após 12ª requisição |

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_rate_limit_bloqueia_apos_limite():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Faz 12 requisições válidas
        for _ in range(12):
            response = await client.get(
                "/quantitativointerrupcoesativas",
                headers={"x-api-key": TEST_API_KEY}
            )
            assert response.status_code == 200

        # 13ª requisição deve ser bloqueada
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": TEST_API_KEY}
        )
        assert response.status_code == 429
```

##### TC-E2E-006: Validação do formato de resposta

| Campo | Valor |
|-------|-------|
| **Validação** | Schema ANEEL completo |
| **Resultado Esperado** | Todos os campos obrigatórios presentes |

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_resposta_segue_schema_aneel():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": TEST_API_KEY}
        )

    data = response.json()

    # Campos obrigatórios da resposta
    assert isinstance(data["idcStatusRequisicao"], int)
    assert data["idcStatusRequisicao"] in [1, 2]
    assert isinstance(data["emailIndisponibilidade"], str)
    assert isinstance(data["mensagem"], str)
    assert isinstance(data["quantitativoInterrupcoesAtivas"], list)

    # Campos de cada item
    for item in data["quantitativoInterrupcoesAtivas"]:
        assert isinstance(item["ideMunicipio"], int)
        assert 1400000 <= item["ideMunicipio"] <= 1499999
        assert item["idcTipoInterrupcao"] in [1, 2]
        assert isinstance(item["qtdInterrupcoes"], int)
        assert isinstance(item["qtdUcsInterrompidas"], int)
        assert isinstance(item["qtdEquipesDeslocamento"], int)
        assert re.match(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", item["dthUltRecuperacao"])
```

### 4.5 Testes de Performance

#### 4.5.1 Teste de Carga

##### TC-PERF-001: Carga normal (ANEEL)

| Campo | Valor |
|-------|-------|
| **Cenário** | Polling ANEEL a cada 5 minutos |
| **Usuários** | 1 |
| **Requisições** | 12/minuto |
| **Duração** | 1 hora |
| **SLA** | p95 < 500ms |

```python
# locustfile.py
from locust import HttpUser, task, between

class ANEELUser(HttpUser):
    wait_time = between(4, 6)  # 5 min médio

    @task
    def get_interrupcoes(self):
        self.client.get(
            "/quantitativointerrupcoesativas",
            headers={"x-api-key": API_KEY}
        )
```

##### TC-PERF-002: Stress test

| Campo | Valor |
|-------|-------|
| **Cenário** | Múltiplos clientes simultâneos |
| **Usuários** | 10 |
| **Requisições** | 100 req/min total |
| **Duração** | 15 minutos |
| **SLA** | p99 < 2000ms, 0% erros |

### 4.6 Testes de Segurança

#### 4.6.1 OWASP Top 10

##### TC-SEC-001: SQL Injection

| Campo | Valor |
|-------|-------|
| **Vetor** | Parâmetros de query |
| **Payload** | `'; DROP TABLE--` |
| **Resultado Esperado** | 400 Bad Request ou input sanitizado |

##### TC-SEC-002: API Key Brute Force

| Campo | Valor |
|-------|-------|
| **Vetor** | Tentativas múltiplas de autenticação |
| **Resultado Esperado** | Rate limiting aplicado após N tentativas |

##### TC-SEC-003: Information Disclosure

| Campo | Valor |
|-------|-------|
| **Vetor** | Respostas de erro |
| **Resultado Esperado** | Sem stack traces ou informações internas |

## 5. Ambiente de Testes

### 5.1 Ambientes

| Ambiente | Propósito | Database | Cache |
|----------|-----------|----------|-------|
| Local | Desenvolvimento | SQLite/Mocks | Dict |
| CI | Integração contínua | Oracle TestContainer | Redis TestContainer |
| Homologação | Testes de aceitação | Oracle Homolog | Redis Homolog |

### 5.2 Fixtures

```python
# conftest.py

@pytest.fixture
def codigo_ibge_boa_vista():
    return CodigoIBGE("1400050")

@pytest.fixture
def interrupcao_factory():
    def _create(**kwargs):
        defaults = {
            "id": uuid4(),
            "municipio": CodigoIBGE("1400050"),
            "tipo": TipoInterrupcao.NAO_PROGRAMADA,
            "quantidade_ucs": 100,
            "quantidade_equipes": 2,
            "data_atualizacao": datetime.now(),
        }
        return Interrupcao(**{**defaults, **kwargs})
    return _create

@pytest.fixture
async def test_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
def mock_repository():
    return Mock(spec=InterrupcaoRepository)

@pytest.fixture
def mock_cache():
    return Mock(spec=CacheService)
```

### 5.3 Dados de Teste

```python
# test_data.py

TEST_INTERRUPCOES = [
    {
        "ideMunicipio": 1400050,
        "idcTipoInterrupcao": 2,
        "qtdInterrupcoes": 3,
        "qtdUcsInterrompidas": 2500,
        "qtdEquipesDeslocamento": 4,
        "dthUltRecuperacao": "10/12/2025 14:30",
    },
    {
        "ideMunicipio": 1400050,
        "idcTipoInterrupcao": 1,
        "qtdInterrupcoes": 1,
        "qtdUcsInterrompidas": 500,
        "qtdEquipesDeslocamento": 2,
        "dthUltRecuperacao": "10/12/2025 14:25",
    },
]

MUNICIPIOS_RORAIMA = [
    ("1400050", "Boa Vista"),
    ("1400100", "Alto Alegre"),
    ("1400027", "Amajari"),
    ("1400159", "Bonfim"),
    ("1400175", "Cantá"),
    # ... demais municípios
]
```

## 6. Critérios de Aceite

### 6.1 Critérios de Entrada

- [ ] Código commitado no repositório
- [ ] Build passando no CI
- [ ] Ambiente de teste disponível
- [ ] Dados de teste preparados

### 6.2 Critérios de Saída

- [ ] Cobertura de código >= 80%
- [ ] Todos os testes unitários passando
- [ ] Todos os testes de integração passando
- [ ] Testes E2E críticos passando
- [ ] Nenhuma vulnerabilidade crítica
- [ ] Performance dentro do SLA

### 6.3 Métricas de Qualidade

| Métrica | Threshold | Bloqueante |
|---------|-----------|------------|
| Cobertura de linhas | >= 80% | Sim |
| Cobertura de branches | >= 70% | Não |
| Testes unitários passando | 100% | Sim |
| Testes integração passando | 100% | Sim |
| Tempo médio de resposta | < 200ms | Não |
| p95 latência | < 500ms | Sim |

## 7. Execução dos Testes

### 7.1 Comandos

```bash
# Todos os testes
pytest backend/tests/ -v

# Apenas unitários
pytest backend/tests/ -m unit -v

# Apenas integração
pytest backend/tests/ -m integration -v

# Apenas E2E
pytest backend/tests/ -m e2e -v

# Com cobertura
pytest backend/tests/ --cov=backend --cov-report=html --cov-fail-under=80

# Testes específicos
pytest backend/tests/unit/domain/value_objects/test_codigo_ibge.py -v

# Performance (Locust)
locust -f tests/performance/locustfile.py --host=http://localhost:8001
```

### 7.2 Pipeline CI/CD

```yaml
# .github/workflows/test.yml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: pip install -r requirements-test.txt

    - name: Run unit tests
      run: pytest -m unit --cov=backend --cov-fail-under=80

    - name: Run integration tests
      run: pytest -m integration

    - name: Upload coverage
      uses: codecov/codecov-action@v4
```

## 8. Rastreabilidade

### 8.1 Matriz de Rastreabilidade

| Requisito | Caso de Teste |
|-----------|---------------|
| REQ-001: Retornar interrupções ativas | TC-UC-001, TC-UC-002, TC-E2E-002 |
| REQ-002: Autenticação via API Key | TC-E2E-002, TC-E2E-003, TC-E2E-004 |
| REQ-003: Rate Limiting 12 req/min | TC-E2E-005 |
| REQ-004: Cache 5 minutos | TC-UC-001, TC-CACHE-002 |
| REQ-005: Formato ANEEL | TC-E2E-006 |
| REQ-006: Código IBGE 7 dígitos RR | TC-VO-001, TC-VO-002, TC-VO-003 |

## 9. Referências

- [Especificação API 1 - ANEEL](../api-specs/API_01_QUANTITATIVO_INTERRUPCOES_ATIVAS.md)
- [OpenAPI Specification](../api-specs/openapi-api1-interrupcoes.yaml)
- [pytest Documentation](https://docs.pytest.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

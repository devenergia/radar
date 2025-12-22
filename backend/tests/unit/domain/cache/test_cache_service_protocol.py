"""Testes TDD para Protocol CacheService (RAD-106).

Seguindo TDD, estes testes sao escritos ANTES da implementacao.
Eles definem o contrato esperado para o servico de cache.
"""

import inspect
from typing import Protocol


class TestCacheServiceProtocol:
    """Testes para verificar que CacheService e um Protocol valido."""

    def test_deve_ser_um_protocol(self):
        """CacheService deve ser um Protocol."""
        from backend.shared.domain.cache.cache_service import CacheService

        assert issubclass(type(CacheService), type(Protocol))

    def test_protocol_deve_ter_metodo_get(self):
        """Protocol deve definir metodo get."""
        from backend.shared.domain.cache.cache_service import CacheService

        assert hasattr(CacheService, "get")
        assert callable(getattr(CacheService, "get", None))

    def test_protocol_deve_ter_metodo_set(self):
        """Protocol deve definir metodo set."""
        from backend.shared.domain.cache.cache_service import CacheService

        assert hasattr(CacheService, "set")
        assert callable(getattr(CacheService, "set", None))

    def test_protocol_deve_ter_metodo_delete(self):
        """Protocol deve definir metodo delete."""
        from backend.shared.domain.cache.cache_service import CacheService

        assert hasattr(CacheService, "delete")
        assert callable(getattr(CacheService, "delete", None))

    def test_protocol_deve_ter_metodo_exists(self):
        """Protocol deve definir metodo exists."""
        from backend.shared.domain.cache.cache_service import CacheService

        assert hasattr(CacheService, "exists")
        assert callable(getattr(CacheService, "exists", None))

    def test_protocol_deve_ter_metodo_clear(self):
        """Protocol deve definir metodo clear."""
        from backend.shared.domain.cache.cache_service import CacheService

        assert hasattr(CacheService, "clear")
        assert callable(getattr(CacheService, "clear", None))


class TestCacheKeys:
    """Testes para constantes de chaves de cache."""

    def test_deve_ter_chave_interrupcoes_ativas(self):
        """CacheKeys deve definir chave para interrupcoes ativas."""
        from backend.shared.domain.cache.cache_service import CacheKeys

        assert hasattr(CacheKeys, "INTERRUPCOES_ATIVAS")
        assert CacheKeys.INTERRUPCOES_ATIVAS == "interrupcoes:ativas"

    def test_deve_ter_chave_universo_municipios(self):
        """CacheKeys deve definir chave para universo municipios."""
        from backend.shared.domain.cache.cache_service import CacheKeys

        assert hasattr(CacheKeys, "UNIVERSO_MUNICIPIOS")
        assert CacheKeys.UNIVERSO_MUNICIPIOS == "universo:municipios"

    def test_deve_ter_chave_universo_conjuntos(self):
        """CacheKeys deve definir chave para universo conjuntos."""
        from backend.shared.domain.cache.cache_service import CacheKeys

        assert hasattr(CacheKeys, "UNIVERSO_CONJUNTOS")
        assert CacheKeys.UNIVERSO_CONJUNTOS == "universo:conjuntos"


class TestCacheTTL:
    """Testes para constantes de TTL do cache."""

    def test_ttl_interrupcoes_deve_ser_300_segundos(self):
        """TTL de interrupcoes deve ser 5 minutos (300 segundos)."""
        from backend.shared.domain.cache.cache_service import CacheTTL

        assert hasattr(CacheTTL, "INTERRUPCOES")
        assert CacheTTL.INTERRUPCOES == 300

    def test_ttl_universo_deve_ser_3600_segundos(self):
        """TTL de universo deve ser 1 hora (3600 segundos)."""
        from backend.shared.domain.cache.cache_service import CacheTTL

        assert hasattr(CacheTTL, "UNIVERSO")
        assert CacheTTL.UNIVERSO == 3600

    def test_ttl_curta_deve_ser_60_segundos(self):
        """TTL curta deve ser 1 minuto (60 segundos)."""
        from backend.shared.domain.cache.cache_service import CacheTTL

        assert hasattr(CacheTTL, "CURTA")
        assert CacheTTL.CURTA == 60


class TestCacheServiceGenericType:
    """Testes para verificar suporte a tipos genericos."""

    def test_protocol_deve_ser_generico(self):
        """CacheService deve suportar tipos genericos."""
        from backend.shared.domain.cache.cache_service import CacheService

        # Verificar que CacheService aceita parametro de tipo
        # CacheService[int], CacheService[str], etc.
        assert hasattr(CacheService, "__class_getitem__")


class TestCacheServiceMethodSignatures:
    """Testes para verificar assinaturas dos metodos."""

    def test_get_deve_retornar_valor_ou_none(self):
        """Metodo get deve ter assinatura correta."""
        from backend.shared.domain.cache.cache_service import CacheService

        sig = inspect.signature(CacheService.get)
        params = list(sig.parameters.keys())

        assert "self" in params
        assert "key" in params

    def test_set_deve_ter_parametro_ttl_com_default(self):
        """Metodo set deve ter parametro ttl_seconds com valor default."""
        from backend.shared.domain.cache.cache_service import CacheService

        sig = inspect.signature(CacheService.set)
        params = sig.parameters

        assert "ttl_seconds" in params
        assert params["ttl_seconds"].default == 300

    def test_delete_deve_aceitar_key(self):
        """Metodo delete deve aceitar key como parametro."""
        from backend.shared.domain.cache.cache_service import CacheService

        sig = inspect.signature(CacheService.delete)
        params = list(sig.parameters.keys())

        assert "key" in params

    def test_exists_deve_aceitar_key(self):
        """Metodo exists deve aceitar key como parametro."""
        from backend.shared.domain.cache.cache_service import CacheService

        sig = inspect.signature(CacheService.exists)
        params = list(sig.parameters.keys())

        assert "key" in params

    def test_clear_nao_deve_ter_parametros_alem_de_self(self):
        """Metodo clear so deve ter self como parametro."""
        from backend.shared.domain.cache.cache_service import CacheService

        sig = inspect.signature(CacheService.clear)
        params = list(sig.parameters.keys())

        # Apenas self
        assert len(params) == 1
        assert "self" in params

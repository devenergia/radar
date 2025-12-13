"""Result Pattern para tratamento de erros sem exceptions."""

from __future__ import annotations

from typing import Callable, Generic, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class Result(Generic[T]):
    """
    Result Pattern para tratamento de erros sem exceptions.

    Baseado no Either pattern de linguagens funcionais.

    Uso:
        result = Result.ok(value)  # Sucesso
        result = Result.fail("erro")  # Falha

        if result.is_success:
            value = result.value
        else:
            error = result.error
    """

    def __init__(
        self,
        is_success: bool,
        value: T | None = None,
        error: str | None = None,
    ) -> None:
        if is_success and error is not None:
            raise ValueError("Result nao pode ser sucesso com erro")
        if not is_success and error is None:
            raise ValueError("Result falho deve ter mensagem de erro")

        self._is_success = is_success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        """Retorna True se o resultado for sucesso."""
        return self._is_success

    @property
    def is_failure(self) -> bool:
        """Retorna True se o resultado for falha."""
        return not self._is_success

    @property
    def value(self) -> T:
        """
        Retorna o valor do resultado.

        Raises:
            ValueError: Se o resultado for falha.
        """
        if not self._is_success:
            raise ValueError(
                "Nao pode obter valor de um Result falho. Use error ao inves."
            )
        return self._value  # type: ignore

    @property
    def error(self) -> str:
        """
        Retorna o erro do resultado.

        Raises:
            ValueError: Se o resultado for sucesso.
        """
        if self._is_success:
            raise ValueError("Nao pode obter erro de um Result bem-sucedido.")
        return self._error  # type: ignore

    @classmethod
    def ok(cls, value: T) -> Result[T]:
        """Cria um Result de sucesso."""
        return cls(is_success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> Result[T]:
        """Cria um Result de falha."""
        return cls(is_success=False, error=error)

    @classmethod
    def combine(cls, results: list[Result[object]]) -> Result[None]:
        """
        Combina multiplos Results em um unico.

        Retorna falha se qualquer um dos results for falha.
        """
        for result in results:
            if result.is_failure:
                return Result.fail(result.error)
        return Result.ok(None)

    def map(self, fn: Callable[[T], U]) -> Result[U]:
        """
        Mapeia o valor do Result para outro tipo.

        Se o Result for falha, retorna o mesmo erro.
        """
        if self.is_failure:
            return Result.fail(self._error)  # type: ignore
        return Result.ok(fn(self._value))  # type: ignore

    def flat_map(self, fn: Callable[[T], Result[U]]) -> Result[U]:
        """
        Encadeia operacoes que retornam Result.

        Se o Result for falha, retorna o mesmo erro.
        """
        if self.is_failure:
            return Result.fail(self._error)  # type: ignore
        return fn(self._value)  # type: ignore

    def __repr__(self) -> str:
        if self._is_success:
            return f"Result.ok({self._value!r})"
        return f"Result.fail({self._error!r})"

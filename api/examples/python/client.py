"""
Cliente Python para API RADAR - Roraima Energia
Base Legal: Ofício Circular nº 14/2025-SFE/ANEEL

Este módulo fornece uma classe cliente para consumir os endpoints da API RADAR.
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime


class RadarAPIClient:
    """
    Cliente para consumo da API RADAR - Roraima Energia.

    Exemplo de uso:
        client = RadarAPIClient(
            base_url="https://api.roraimaenergia.com.br/radar",
            api_key="sua-api-key"
        )

        # Consultar interrupções ativas
        interrupcoes = client.get_interrupcoes_ativas()

        # Consultar demandas diversas
        demandas = client.get_demandas_diversas()

        # Consultar dados de uma demanda específica
        demanda = client.get_dados_demanda("123456789")
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Inicializa o cliente da API RADAR.

        Args:
            base_url: URL base da API (ex: https://api.roraimaenergia.com.br/radar)
            api_key: Chave de API fornecida pela Roraima Energia
            timeout: Timeout em segundos para requisições (padrão: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz uma requisição GET para o endpoint especificado.

        Args:
            endpoint: Nome do endpoint (sem barra inicial)
            params: Parâmetros de query string (opcional)

        Returns:
            Dict com a resposta JSON da API

        Raises:
            requests.exceptions.HTTPError: Se a requisição falhar
        """
        url = f"{self.base_url}/{endpoint}"

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()

    def get_interrupcoes_ativas(self, dth_recuperacao: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta o quantitativo de interrupções ativas.

        Args:
            dth_recuperacao: Data/hora para recuperação histórica (formato: dd/mm/yyyy hh:mm)
                            Se não informado, retorna dados do momento atual.
                            Disponível a partir de 01/04/2026.

        Returns:
            Dict com a estrutura:
            {
                "idcStatusRequisicao": 1,
                "emailIndisponibilidade": "radar@roraimaenergia.com.br",
                "mensagem": "",
                "interrupcaoFornecimento": [...]
            }
        """
        params = {}
        if dth_recuperacao:
            params["dthRecuperacao"] = dth_recuperacao

        return self._make_request("quantitativointerrupcoesativas", params if params else None)

    def get_demandas_diversas(self) -> Dict[str, Any]:
        """
        Consulta o quantitativo de demandas diversas do dia.

        Returns:
            Dict com a estrutura:
            {
                "idcStatusRequisicao": 1,
                "mensagem": "",
                "demandasDiversas": [...]
            }
        """
        return self._make_request("quantitativodemandasdiversas")

    def get_dados_demanda(self, num_protocolo: str) -> Dict[str, Any]:
        """
        Consulta os dados detalhados de uma demanda específica.

        Args:
            num_protocolo: Número do protocolo da demanda (até 30 caracteres)

        Returns:
            Dict com a estrutura:
            {
                "idcStatusRequisicao": 1,
                "mensagem": "",
                "demanda": {...}
            }
        """
        params = {"numProtocolo": num_protocolo}
        return self._make_request("dadosdemanda", params)

    def is_api_available(self) -> bool:
        """
        Verifica se a API está disponível.

        Returns:
            True se a API estiver acessível, False caso contrário
        """
        try:
            response = self.get_interrupcoes_ativas()
            return response.get("idcStatusRequisicao") == 1
        except Exception:
            return False


# ============================================
# EXEMPLO DE USO
# ============================================

if __name__ == "__main__":
    # Configuração
    BASE_URL = "https://api.roraimaenergia.com.br/radar"
    API_KEY = "sua-api-key-aqui"  # Substituir pela chave real

    # Criar cliente
    client = RadarAPIClient(base_url=BASE_URL, api_key=API_KEY)

    print("=" * 60)
    print("API RADAR - Roraima Energia")
    print("=" * 60)

    # 1. Consultar interrupções ativas
    print("\n[1] Consultando interrupções ativas...")
    try:
        interrupcoes = client.get_interrupcoes_ativas()

        if interrupcoes["idcStatusRequisicao"] == 1:
            lista = interrupcoes.get("interrupcaoFornecimento", [])
            print(f"    Status: Sucesso")
            print(f"    Total de registros: {len(lista)}")

            if lista:
                print("    Primeiros 3 registros:")
                for item in lista[:3]:
                    print(f"      - Conjunto: {item['ideConjuntoUnidadeConsumidora']}, "
                          f"Município: {item['ideMunicipio']}, "
                          f"Programadas: {item['qtdOcorrenciaProgramada']}, "
                          f"Não Programadas: {item['qtdOcorrenciaNaoProgramada']}")
        else:
            print(f"    Erro: {interrupcoes.get('mensagem')}")

    except requests.exceptions.HTTPError as e:
        print(f"    Erro HTTP: {e}")
    except Exception as e:
        print(f"    Erro: {e}")

    # 2. Consultar demandas diversas
    print("\n[2] Consultando demandas diversas...")
    try:
        demandas = client.get_demandas_diversas()

        if demandas["idcStatusRequisicao"] == 1:
            lista = demandas.get("demandasDiversas", [])
            print(f"    Status: Sucesso")
            print(f"    Total de registros: {len(lista)}")

            if lista:
                print("    Primeiros 3 registros:")
                for item in lista[:3]:
                    print(f"      - Nível: {item['idcNivelAtendimento']}, "
                          f"Canal: {item['idcCanalAtendimento']}, "
                          f"Tipologia: {item['idcTipologia']}, "
                          f"Em andamento: {item['qtdAndamentoNoMomento']}")
        else:
            print(f"    Erro: {demandas.get('mensagem')}")

    except requests.exceptions.HTTPError as e:
        print(f"    Erro HTTP: {e}")
    except Exception as e:
        print(f"    Erro: {e}")

    # 3. Consultar dados de demanda específica
    print("\n[3] Consultando dados de demanda específica...")
    try:
        protocolo = "02157896542021565898742569875"
        demanda = client.get_dados_demanda(protocolo)

        if demanda["idcStatusRequisicao"] == 1:
            dados = demanda.get("demanda", {})

            if dados:
                print(f"    Status: Sucesso")
                print(f"    Protocolo: {dados.get('numProtocolo')}")
                print(f"    UC: {dados.get('numUC')}")
                print(f"    Titular: {dados.get('nomeTitularUC')}")
                print(f"    Canal: {dados.get('idcCanalAtendimento')}")
                print(f"    Status da demanda: {dados.get('idcStatus')}")
                print(f"    Abertura: {dados.get('dthAbertura')}")
            else:
                print(f"    Protocolo {protocolo} não encontrado")
        else:
            print(f"    Erro: {demanda.get('mensagem')}")

    except requests.exceptions.HTTPError as e:
        print(f"    Erro HTTP: {e}")
    except Exception as e:
        print(f"    Erro: {e}")

    print("\n" + "=" * 60)
    print("Fim da demonstração")
    print("=" * 60)

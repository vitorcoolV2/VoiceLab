"""
Módulo utilitário para parsing e utilização do Swagger/OpenAPI spec do servidor TTS.
Permite gerar ajuda dinâmica, exemplos de uso e validação de argumentos para o CLI.
"""

import requests
from typing import Dict, Any, Optional


def fetch_openapi_spec(server_url: str = "http://localhost:8000/openapi.json") -> Optional[Dict[str, Any]]:
    """
    Faz download do ficheiro OpenAPI/Swagger do servidor TTS.
    Retorna o dicionário do spec ou None em caso de erro.
    """
    try:
        response = requests.get(server_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[swagger_utils] Erro ao obter OpenAPI spec: {e}")
        return None


def list_endpoints(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lista os endpoints disponíveis no spec OpenAPI.
    Retorna um dicionário {endpoint: métodos}.
    """
    paths = openapi_spec.get("paths", {})
    return {path: list(methods.keys()) for path, methods in paths.items()}


# Futuras funções:
# - get_endpoint_help(openapi_spec, endpoint)
# - get_examples_for_endpoint(openapi_spec, endpoint)
# - validate_args_against_spec(openapi_spec, endpoint, args) 
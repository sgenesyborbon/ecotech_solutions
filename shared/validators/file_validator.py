# ==================
# FILE VALIDATOR
# ==================

import json
from enum import StrEnum
from pathlib import Path
from typing import Any, TypeVar

from shared.exceptions.exception import (
    InfrastructureError,
    ValidationError,
)

T = TypeVar("T")  # Item
E = TypeVar("E", bound=StrEnum)  # Enum (bounded to Enum classes)
K = TypeVar("K")  # Key
V = TypeVar("V")  # Value
C = TypeVar("C")  # Class / Instance Type


class FileValidator:
    """Files and data loader validation for domain models and inputs."""

    # -------------------
    # VALIDAR ARCHIVO
    # -------------------

    @staticmethod
    def validar_existencia_archivo(
        path: Path | str,
        field_name: str = "file_path",
    ) -> Path:
        """Valida la ruta del archivo existe y que es un archivo."""

        file_path = Path(path) if isinstance(path, str) else path

        if not file_path.exists():
            raise InfrastructureError(
                f"Archivo para campo: '{field_name}' no encontrado en la ruta: '{file_path.resolve()}'"
            )

        if not file_path.is_file():
            raise InfrastructureError(
                f"""Ruta para archivo: '{field_name}' es un directorio.
                Se espera un archivo: '{file_path.resolve()}'"""
            )

        return file_path

    # --------------------------
    # VALIDA RUTA DE DIRECTORIO
    # --------------------------

    @staticmethod
    def valida_existencia_ruta(
        path: Path | str,
        field_name: str = "directory_path",
        create_if_missing: bool = True,
    ) -> Path:
        """Valida o crea una ruta de directorio"""

        dir_path = Path(path) if isinstance(path, str) else path

        if not dir_path.exists():
            if create_if_missing:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as err:
                    raise InfrastructureError(
                        f"""Error al crear directorio '{field_name}' en la ruta
                        '{dir_path.resolve()}': {err}"""
                    ) from err
            else:
                raise InfrastructureError(
                    f"""Directorio '{field_name}' no existe en:
                    '{dir_path.resolve()}'"""
                )

        if not dir_path.is_dir():
            raise InfrastructureError(
                f"""Ruta para '{field_name}' es un archivo.
                Se espera una ruta de directorio: '{dir_path.resolve()}'"""
            )

        return dir_path

    # ------------------------
    # VALIDACIÓN ARCHIVO JSON
    # ------------------------

    @staticmethod
    def validar_archivo_json(
        path: Path | str,
        field_name: str = "json_file",
        allow_empty: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Valida la existencia del archivo, lo lee y parsea contenido JSON a la memoria"""

        file_path = FileValidator.validar_existencia_archivo(path, field_name=field_name)

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as err:
            raise ValidationError(
                f"""Archivo JSON corrompido o inválido:'{field_name}'
                 ({file_path.name}), {err}""",
                field_name=field_name,
                invalid_value=str(file_path),
            ) from err
        except OSError as err:
            raise InfrastructureError(
                f"Error de lectura '{field_name}' en '{file_path.resolve()}': {err}"
            ) from err

        if not allow_empty and not data:
            raise ValidationError(
                f"Archivo JSON para campo: '{field_name}' ({file_path.name}) está vacío",
                field_name=field_name,
                invalid_value=data,
            )

        return data

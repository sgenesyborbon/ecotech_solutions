
import json
from decimal import Decimal
from pathlib import Path

from ejercicio_2_productos.paneles_solares import PanelSolar
from shared.exceptions.exception import StockInvalidoError
from shared.validators.data_validator import DataValidator


class GestorInventario:
    """Clase para gestionar el inventario de dispositivos ecológicos."""

    def __init__(self):
        
        self.lista_dispositivos = [] # lista de fichas técnicas

    def agregar_dispositivo(self, dispositivo: PanelSolar) -> None:
        """Agrega un dispositivo ecológico al inventario."""

        dispositivo_validado = DataValidator.validar_clase(
            value=dispositivo,
            expected_class=PanelSolar,
            field_name="dispositivo",
            allow_none=False
        )
        self.lista_dispositivos.append(dispositivo_validado)

    def obtener_inventario(self) -> list:
        """Devuelve la lista completa del inventario."""
        return self.lista_dispositivos


    def guardar_registros_json(
        self,
        lista_registros: list,
        ruta_archivo: Path | str) -> None:
        """Almacena en memoria los registros con stock incluido en formato JSON"""

        self.lista_registros: list = lista_registros
        registros_limpios = []

        # Validar la regla de negocio del stock antes de serializar
        for dispositivo in self.lista_registros:
            stock_actual = getattr(dispositivo, "stock", 0)
            if stock_actual <= 0:
                prod_id = getattr(dispositivo, "producto_id", "SIN-ID")
                codigo = getattr(dispositivo, "codigo_producto", "SIN-CODIGO")
        
                # Lanzamos la excepción personalizada de dominio
                raise StockInvalidoError(
                    producto_id=str(prod_id),
                    codigo_producto=str(codigo),
                    stock=dispositivo.stock
                )
            registro_dict = {
                "producto_id": str(getattr(dispositivo, "producto_id", "SIN-ID")),
                "codigo_producto": str(getattr(dispositivo, "codigo_producto", "SIN-CODIGO")),
                "nombre": getattr(dispositivo, "nombre", "Sin Nombre"),
                "categoria": str(getattr(dispositivo, "categoria", "")),
                "stock": stock_actual,
                "precio_venta": str(getattr(dispositivo, "precio_venta", "0.00")),
                "fecha_produccion": str(getattr(dispositivo, "fecha_produccion", ""))
            }
            if hasattr(dispositivo, "actualizar_registro_dispositivos"):
                try:
                    # Intentamos llamarlo con su estructura original si existe
                    registro_dict = dispositivo.actualizar_registro_dispositivos(
                        registro_dict)
                except TypeError:
                    pass  # Si no recibe argumentos, mantenemos nuestro diccionario limpio con stock

            registros_limpios.append(registro_dict)

        ruta_salida = Path(ruta_archivo)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            json.dump(
                registros_limpios, 
                archivo,
                ensure_ascii=False,
                indent=4,
                default=lambda o: float(o) if isinstance(o, Decimal) else str(o)
            )
                
            print(f"Registro guardado exitosamente!\n"
                f"Guardado en: '{ruta_salida.resolve()}'.")

    @staticmethod
    def guardar_catalogo_json(lista_disposivos: list, ruta_archivo: Path | str) -> None:
        """Almacena en memoria las fichas técnicas de los dispositivos en
        formato JSON"""

        catalogo_ecotech = [
            dispositivo.obtener_ficha_tecnica()
            for dispositivo in lista_disposivos
        ]

        ruta_salida = Path(ruta_archivo)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            json.dump(
                catalogo_ecotech, 
                archivo,
                ensure_ascii=False,
                indent=4,
                default=lambda o: float(o) if isinstance(o, Decimal) else str(o)
            )
        
        print(f"¡Catálogo exportado exitosamente!\n"
              f"Guardado en: '{ruta_salida.resolve()}'.")


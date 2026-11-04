
import re
from datetime import date
from datetime import datetime as dt
from decimal import Decimal
from uuid import UUID, uuid4

from ejercicio_2_productos.formula_precio import PrecioProducto
from shared.enums.enums import Categoria, TipoProducto
from shared.exceptions.exception import StockInvalidoError, ValidationError
from shared.validators.data_validator import DataValidator
from shared.validators.datetime_validator import DatetimeValidator


class DispositivoEcologico:
    """Define un dispositivo ecológico con atributos de nombre, descripción y stock."""

    def __init__(
        self,
        categoria: Categoria,
        tipo_producto: TipoProducto,
        codigo_producto: str,
        nombre: str,
        descripcion: str,
        fecha_produccion: date | None = None,
        fecha_garantia: date | None = None,
        degradacion_anual_max: float | None = None,
        precio_venta: PrecioProducto | Decimal | None = None,
    ) -> None:

        self.producto_id: UUID = DataValidator.validar_uuid(
            value=uuid4(), field_name="producto_id", allow_none=False
        ) # ID tipo UUID

        self.categoria = DataValidator.validar_enum(
            value=categoria, enum_cls=Categoria,
            field_name="categoria", allowed_subset=None
        )
        self.tipo_producto = DataValidator.validar_enum(
            value=tipo_producto, enum_cls=TipoProducto,
            field_name="tipo_producto", allowed_subset=None
        )
        self.codigo_producto = DataValidator.validar_str(
            value=codigo_producto, 
            field_name="codigo_producto",
            pattern=r"^(PANEL_SOLAR|BATERIA_RECARGABLE|SISTEMA_RECICLAJE|TERMOSTATO_INTELIGENTE|SENSOR_EFICIENCIA)-\d+$",
            pattern_description="""El código debe iniciar con un TipoProducto válido
            seguido de guion y número (Ej: PANEL_SOLAR-001)"""
        )
        self.nombre = DataValidator.validar_str(
            nombre, field_name="nombre", min_length=2, max_length=150
        )
        self.descripcion = DataValidator.validar_str(
            descripcion, field_name="descripcion", min_length=2, max_length=150
        )

        self.fecha_produccion = DatetimeValidator.validar_date(
            fecha_produccion, field_name="fecha_produccion", allow_none=True
        )
        self.fecha_garantia = DatetimeValidator.validar_date(
            fecha_garantia, field_name="fecha_garantia", allow_none=True
        )
        self.degradacion_anual_max = DataValidator.validar_numero(
            value=degradacion_anual_max, field_name="degradacion_anual_max",
            min_value=0.0, max_value=100.0, allow_float=True,
        )
        self.precio_venta = DataValidator.validar_clase(
            value=precio_venta, expected_class=PrecioProducto, field_name="precio_venta",
            allow_none=True,
        )

    @property
    def stock(self) -> int:
        """Getter explícito para acceder al stock de manera segura."""
        return getattr(self, '_stock', 0)

    @stock.setter
    def stock(self, nuevo_stock: int) -> None:
        """Setter con validación de negocio para impedir stocks negativos."""

        if not isinstance(nuevo_stock, int) or nuevo_stock <= 0:
            raise StockInvalidoError(
                producto_id=str(self.producto_id),
                codigo_producto=self.codigo_producto,
                stock=nuevo_stock
            )
        self._stock = nuevo_stock

    def limpiar_registro_dispositivos(self, registro_dispositivos_raw: dict) -> dict:
        """Transforma un diccionario crudo individual en un diccionario
        estandarizado"""

        self.registro_dispositivos_raw: dict = registro_dispositivos_raw

        # Limpiar categoría del dispositivo
        categoria_raw = self.registro_dispositivos_raw.get("categoria", "Otro")
        categoria_limpia = DataValidator.validar_enum(
            value=categoria_raw,
            enum_cls=Categoria,
            field_name="categoria"
        )
        # Limpiar tipo de producto
        tipo_producto_raw = self.registro_dispositivos_raw.get("tipo_producto", "Otro")
        try:
            tipo_producto_limpio = DataValidator.validar_enum(
                value=tipo_producto_raw,
                enum_cls=TipoProducto,
                field_name="tipo_producto"
            )
        except ValueError:
            tipo_producto_limpio = TipoProducto.OTRO

        # Limpiar código del producto
        producto_codigo_raw = str(self.registro_dispositivos_raw.get("codigo_producto", ""))
        coincidir_numero = re.search(r"\d+", producto_codigo_raw)
    
        if coincidir_numero:
            # Si el código original tenía números, los conservamos como entero
            numero_serie = int(coincidir_numero.group())
        else:
            # Si estaba vacío o no tenía números (ej. campo "")
            # asignamos un número por defecto (ej. 1 o un ID seguro)
            numero_serie = 1
        
        codigo_construido = f"{tipo_producto_limpio.value}-{numero_serie:03d}"
        try:
            producto_codigo_limpio = DataValidator.validar_str(
                value=codigo_construido,
                field_name="codigo_producto",
                pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ]+-\d+$",
                pattern_description="El código debe iniciar con un TipoProducto seguido de guion y número",
                allow_none=False
            )
        except ValidationError:
            producto_codigo_limpio = f"{tipo_producto_limpio.value}-000"

        # Limpiar fecha de producción (con valor por defecto seguro si falta)
        fecha_produccion_raw = self.registro_dispositivos_raw.get("fecha_produccion")
        if not fecha_produccion_raw or str(fecha_produccion_raw).strip() == "":
            fecha_produccion_limpia = dt.now()
        else:
            fecha_produccion_limpia = DatetimeValidator.validar_datetime(
                value=fecha_produccion_raw,
                field_name="fecha_produccion",
                allow_none=False
            )

        # Limpiar fecha_garantia (con valor por defecto seguro si falta)
        fecha_garantia_raw = self.registro_dispositivos_raw.get("fecha_garantia")
        if not fecha_garantia_raw or str(fecha_garantia_raw).strip() == "":
            fecha_garantia_limpia = dt.now()
        else:
            fecha_garantia_limpia = DatetimeValidator.validar_datetime(
                value=fecha_garantia_raw,
                field_name="fecha_garantia",
                allow_none=False
            )
   
        # Extraer y limpiar degradación anual máxima
        degradacion_anual_max_raw = self.registro_dispositivos_raw.get(
            "degradacion_anual_max", 0.0)
        if isinstance(degradacion_anual_max_raw, str):
            match_temp = re.search(r"[-+]?\d*\.?\d+", degradacion_anual_max_raw)
            degradacion_anual_max_extraida = float(match_temp.group()) if match_temp else 0.0
        else:
            degradacion_anual_max_extraida = float(degradacion_anual_max_raw)

        degradacion_anual_max_limpia = DataValidator.validar_numero(
            value=degradacion_anual_max_extraida,
            field_name="degradacion_anual_max",
            min_value=None,
            max_value=None,
            allow_float=True
        )

        # Extraer y limpiar stock
        stock_raw = self.registro_dispositivos_raw.get(
            "stock", 0)
        if isinstance(stock_raw, str):
            match_temp = re.search(r"[-+]?\d*\.?\d+", stock_raw)
            stock_extraido = int(match_temp.group()) if match_temp else 0
        else:
            stock_extraido = int(stock_raw)
        
        stock_limpio = DataValidator.validar_numero(
            value=stock_extraido,
            field_name="stock",
            min_value=None,
            max_value=None,
            allow_float=False
        )

        # Extraer y limpiar precio de venta
        precio_raw = self.registro_dispositivos_raw.get("precio_venta", Decimal("0.0"))
        
        # Si viene como una instancia de PrecioProducto, calculamos su precio final
        if hasattr(precio_raw, "calcular_precio_venta"):
            precio_extraido = precio_raw.calcular_precio_venta()
        elif isinstance(precio_raw, str):
            # Si se presenta como texto monetario (ej. "$286.00"), purgamos símbolos
            match_precio = re.search(r"[-+]?\d*\.?\d+", precio_raw.replace("$", "").replace(",", ""))
            precio_extraido = Decimal(match_precio.group()) if match_precio else Decimal("0.0")
        else:
            precio_extraido = Decimal(str(precio_raw))

        # Validamos usando DataValidator de decimales
        precio_venta_limpio = DataValidator.validar_decimal(
            value=precio_extraido,
            field_name="precio_venta",
            min_value=Decimal("0.00"),
            max_value=None,
            max_decimal_places=2
        )

        # Retorna estrictamente el diccionario limpio
        self.registro_dispositivos_raw = {
            "categoria": categoria_limpia,
            "tipo_producto": tipo_producto_limpio,
            "codigo_producto": producto_codigo_limpio,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "stock": stock_limpio,
            "fecha_produccion": fecha_produccion_limpia,
            "fecha_garantia": fecha_garantia_limpia,
            "degradacion_anual_max": degradacion_anual_max_limpia,
            "precio_venta": precio_venta_limpio,
        }
        return self.registro_dispositivos_raw

    def obtener_ficha_tecnica(self) -> dict:
        """Ficha técnica comercial base del dispositivo"""

        precio_final = Decimal("0.0")
        if self.precio_venta and hasattr(self.precio_venta, "calcular_precio_venta"):
            precio_final = self.precio_venta.calcular_precio_venta()

        return {
            "Producto ID": str(self.producto_id),
            "Categoría": self.categoria.value if hasattr(self.categoria, "value") else str(self.categoria),
            "Tipo de Producto": self.tipo_producto.value if hasattr(self.tipo_producto, "value") else str(self.tipo_producto),
            "Código de Producto": self.codigo_producto,
            "Nombre": self.nombre,
            "Descripción": self.descripcion,
            "Fecha de Producción": self.fecha_produccion.isoformat() if self.fecha_produccion else None,
            "Fecha de Garantía": self.fecha_garantia.isoformat() if self.fecha_garantia else None,
            "Degradación Anual Máxima": f"{self.degradacion_anual_max}%",
            "Precio de Venta": f"${precio_final:.2f}",
        }

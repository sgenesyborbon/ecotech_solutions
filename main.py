import os
import sys
from pathlib import Path

# Configuración inicial del entorno y rutas relativas
os.environ["NPY_DISABLE_CPU_FEATURES"] = "AVX,AVX2,AVX512F"
raiz_proyecto = Path(__file__).resolve().parent
sys.path.append(str(raiz_proyecto))

from datetime import date
from decimal import Decimal

from ejercicio_1_sensores.reporte_sensores import ReporteSensores

# Importación de módulos del proyecto EcoTech Solutions
from ejercicio_1_sensores.sensores import Sensor
from ejercicio_2_productos.dispositivos_ecologicos import DispositivoEcologico
from ejercicio_2_productos.formula_precio import PrecioProducto
from ejercicio_2_productos.inventario import GestorInventario
from ejercicio_2_productos.paneles_solares import PanelSolar
from ejercicio_3_auditoria_web.auditoria_emisiones import AuditoriaHuellaCarbono
from ejercicio_3_auditoria_web.calculadora_consumo import CalculadoraConsumoIndustrial
from shared.enums.enums import (
    Categoria,
    TipoCosto,
    TipoProducto,
)
from shared.exceptions.exception import StockInvalidoError, ValidationError


def ejecutar_sistema_ecotech():
    print("=" * 70)
    print("--- ECOTECH SOLUTIONS - SISTEMA INTEGRAL DE GESTIÓN Y AUDITORÍA---")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. MÓDULO DE SENSORES Y REPORTES TÉRMICOS (Ejercicio 1)
    # ---------------------------------------------------------
    print("\n[INFO] Inicializando Módulo de Sensores...")
    try:
        # Instanciación y carga de datos de sensores
        gestor_sensores = Sensor()
        # Generación del reporte de sensores y análisis estadístico
        reporte_sensorial = ReporteSensores()
        
        # Ruta de salida para el reporte en PDF de sensores
        ruta_pdf_sensores = raiz_proyecto / "reporte_sensores_planta.pdf"
        reporte_sensorial.generar_reporte_pdf(
            sensor=gestor_sensores,
            ruta_pdf=ruta_pdf_sensores,
            umbral_temperatura=100.0
        )
        print(f"[OK] Reporte PDF de sensores generado en: {ruta_pdf_sensores}")

    except ValidationError as e:
        print(f"[ERROR] En módulo de sensores: {e}")

    # ---------------------------------------------------------
    # 2. MÓDULO DE PRODUCTOS ECOLÓGICOS E INVENTARIO (Ejercicio 2)
    # ---------------------------------------------------------
    print("\n[INFO] Inicializando Módulo de Inventario y Dispositivos Ecológicos...")
    try:
        gestor_inventario = GestorInventario()

        # Ejemplo de registro y actualización de stock para un Panel Solar
        costo_dispositivo = PrecioProducto(
            categoria=Categoria.ENERGIA_SOLAR,
            tipo_producto=TipoProducto.PANEL_SOLAR,
            codigo_producto="PANEL_SOLAR-001",
            estructura_costos={
                TipoCosto.INSUMOS: Decimal("150.00"),
                TipoCosto.MANO_DE_OBRA: Decimal("50.00"),
                TipoCosto.ELECTRICIDAD: Decimal("20.00"),
            },
            margen_ganancia=Decimal("30.00")
        )
        
        dispositivo_ecologico = DispositivoEcologico(
            categoria=Categoria.ENERGIA_SOLAR,
            tipo_producto=TipoProducto.PANEL_SOLAR,
            codigo_producto="PANEL_SOLAR-001",
            nombre="Panel Solar Monocristalino PERC",
            descripcion="""Panel fotovoltaico de alta eficiencia con tecnología
            Half-Cell para proyectos industriales.""",
            fecha_produccion=date(2026, 11, 1),
            fecha_garantia=date(2051, 11, 1),
            degradacion_anual_max=0.55,
            precio_venta=costo_dispositivo,
        )
        panel_solar = PanelSolar(
            categoria=dispositivo_ecologico.categoria,
            tipo_producto=dispositivo_ecologico.tipo_producto,
            codigo_producto=dispositivo_ecologico.codigo_producto,
            nombre=dispositivo_ecologico.nombre,
            descripcion=dispositivo_ecologico.descripcion,
            stock=90,
            fecha_produccion=dispositivo_ecologico.fecha_produccion,
            fecha_garantia=dispositivo_ecologico.fecha_garantia,
            degradacion_anual_max=dispositivo_ecologico.degradacion_anual_max,
            precio_venta=dispositivo_ecologico.precio_venta,
            potencia_max_salida="450W",
            tolerancia_positiva="0/+5W",
            eficiencia_max=20.7,
            caracteristicas_generales={
                "Células": ["Monocristalinas Half-Cell 144 células"],
                "Resistencia": ["Carga de nieve 5400 Pa", "Carga de viento 2400 Pa"],
                "Caja de Conexión": ["IP68 con 3 diodos Bypass"]
            },
            dimensiones_modulo={"Módulo Completo": ("2094 mm", "1038 mm")},
            rendimiento_electrico={
                "1000 W/m2": (41.5, 450.0),
                "800 W/m2": (41.2, 360.0),
                "600 W/m2": (40.8, 270.0)},
            datos_electricos={
                "Tensión Vmp": ("V", 41.5),
                "Corriente Imp": ("A", 10.85),
                "Tensión Voc": ("V", 49.3)},
            datos_mecanicos={
                "Vidrio Frontal": "3.2 mm Templado",
                "Marco": "Aluminio Anodizado", "Peso": 23.5},
            datos_adicionales={
                "Temperatura Operativa": "-40°C a +85°C",
                "Conector": "MC4 Compatible"}
        )

        # Invocación del método de registro de stock y persistencia en JSON
        stock_inicial = 25
        panel_solar.registrar_stock(stock_inicial)
        gestor_inventario.agregar_dispositivo(panel_solar)
        
        print(f"[OK] Dispositivo '{panel_solar.nombre}' registrado con éxito. Stock actual: {stock_inicial} unidades.")

    except StockInvalidoError as sie:
        print(f"[ERROR DE STOCK] {sie}")
    except ValidationError as ve:
        print(f"[ERROR DE VALIDACIÓN] {ve}")

    # ---------------------------------------------------------
    # 3. MÓDULO DE AUDITORÍA WEB Y EMISIONES (Ejercicio 3)
    # ---------------------------------------------------------
    print("\n[INFO] Inicializando Módulo de Auditoría de Huella de Carbono...")
    try:
        calculadora = CalculadoraConsumoIndustrial()

        consumo_mes = calculadora.calcular_consumo_kwh()
        print(f"Consumo mensual de kwh: {consumo_mes}")
        consumo_total = calculadora.calcular_consumo_total()
        print(f"Consumo total de planta: {consumo_total}")
        auditoria = AuditoriaHuellaCarbono()
        
        # Procesamiento de métricas energéticas y estimación de emisiones
        emisiones_estimadas = auditoria.calcular_emisiones_carbono()
        print(f"""Auditoría sustentable procesada correctamente. Emisiones globales calculadas: {emisiones_estimadas}""")

    except ValidationError as e:
        print(f"[ERROR] En módulo de auditoría web: {e}")

    print("\n" + "=" * 70)
    print("      ¡EJECUCIÓN DEL SISTEMA FINALIZADA EXITOSAMENTE!      ")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_sistema_ecotech()
import json
import os
import sys
from pathlib import Path

os.environ["NPY_DISABLE_CPU_FEATURES"] = "AVX,AVX2,AVX512F"
raiz_proyecto = Path(__file__).resolve().parent.parent
sys.path.append(str(raiz_proyecto))

from datetime import date
from datetime import datetime as dt
from decimal import Decimal

from ejercicio_1_sensores.reporte_sensores import ReporteSensores
from ejercicio_1_sensores.sensores import Sensor
from ejercicio_2_productos.dispositivos_ecologicos import DispositivoEcologico
from ejercicio_2_productos.formula_precio import PrecioProducto
from ejercicio_2_productos.inventario import GestorInventario
from ejercicio_2_productos.paneles_solares import PanelSolar
from ejercicio_2_productos.reporte_inventario import ReporteCatalogo
from ejercicio_3_auditoria_web.auditoria_emisiones import AuditoriaHuellaCarbono
from ejercicio_3_auditoria_web.calculadora_consumo import CalculadoraConsumoIndustrial
from shared.enums.enums import (
    Categoria,
    EtapaProducto,
    TipoCosto,
    TipoMaquinaria,
    TipoProducto,
    TipoSensor,
    Ubicacion,
)
from shared.exceptions.exception import StockInvalidoError

registro_sensores = Sensor(
    categoria=Categoria.MONITOREO_INDUSTRIAL,
    tipo_producto=TipoProducto.SENSOR_EFICIENCIA,
    tipo_sensor=TipoSensor.PIROMETROS,
    codigo_producto="PIROMETROS-001",
    ubicacion=Ubicacion.PLANTA_ESTE,
    dia_registro=dt.now(),
    temperatura=24.0,
)
registros_limpios = registro_sensores.procesar_guardar_archivo(
    "ejercicio_1_sensores/registro_impuro_raw.json", "ejercicio_1_sensores/registro_limpio.json")

lista_sensores_alerta, promedio_temperatura = registro_sensores.generar_resumen_sensores()

print(f"Sensores en alerta: {lista_sensores_alerta}")
print(f"Promedio global de la planta: {promedio_temperatura:.2f} °C")

# ¡Proceso exitoso! Se guardaron 30 registros limpios en 'ejercicio_1_sensores/registro_limpio.json'.
# Sensores en alerta: ['Termopares-008', 'Termoresistencias-009', 'Termistores-012', 'Termistores-020', 'Pirómetros-021', 'Termopares-023', 'Pirómetros-025']
# Promedio global de la planta: 558.00 °C

generador_reporte = ReporteSensores()
generador_reporte.generar_reporte_pdf(
    sensor=registro_sensores,
    ruta_pdf="ejercicio_1_sensores/reporte_sensores.pdf"
)
# ¡Reporte PDF generado exitosamente!
# Guardado en: '\ecotech_solutions\ejercicio_1_sensores\reporte_sensores.pdf'.

print("--- PRUEBA 1: Registro y exportación del catálogo con stock erróneo (0) ---")

try:
    # Creamos un dispositivo erróneo con stock 0
    costo_dispositivo_erroneo = PrecioProducto(
        categoria=Categoria.ENERGIA_SOLAR,
        tipo_producto=TipoProducto.PANEL_SOLAR,
        codigo_producto="PANEL_SOLAR-002",
        estructura_costos={
            TipoCosto.INSUMOS: Decimal("150.00"),
            TipoCosto.MANO_DE_OBRA: Decimal("50.00"),
            TipoCosto.ELECTRICIDAD: Decimal("20.00"),
        },
        margen_ganancia=Decimal("30.00")
    )

    dispositivo_erroneo = DispositivoEcologico(
        categoria=Categoria.ENERGIA_SOLAR,
        tipo_producto=TipoProducto.PANEL_SOLAR,
        codigo_producto="PANEL_SOLAR-002",
        nombre="Panel Solar Monocristalino PERC",
        descripcion="""Panel fotovoltaico de alta eficiencia con tecnología " \
        "Half-Cell para proyectos industriales.""",
        fecha_produccion=date(2026, 11, 1),
        fecha_garantia=date(2051, 11, 1),
        degradacion_anual_max=0.55,
        precio_venta=costo_dispositivo_erroneo
    )
    stock_erroneo = dispositivo_erroneo.stock = 0
    panel_solar_erroneo = PanelSolar(
        categoria=dispositivo_erroneo.categoria,
        tipo_producto=dispositivo_erroneo.tipo_producto,
        codigo_producto=dispositivo_erroneo.codigo_producto,
        nombre=dispositivo_erroneo.nombre,
        descripcion=dispositivo_erroneo.descripcion,
        stock= stock_erroneo,
        fecha_produccion=dispositivo_erroneo.fecha_produccion,
        fecha_garantia=dispositivo_erroneo.fecha_garantia,
        degradacion_anual_max=dispositivo_erroneo.degradacion_anual_max,
        precio_venta=dispositivo_erroneo.precio_venta,
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
            "Marco": "Aluminio Anodizado",
            "Peso": 23.5},
        datos_adicionales={
            "Temperatura Operativa": "-40°C a +85°C",
            "Conector": "MC4 Compatible"}
    )
    stock_erroneo = panel_solar_erroneo.registrar_stock(0)
except StockInvalidoError as e:
    print(f"Error inesperado de stock: {e.message}")

# Error inesperado de stock: Producto ID'22a6961a-d7b4-4502-9560-42cd48b906f8'
# Código PANEL_SOLAR-002 tiene stock inválido: 0. Stock no puede ser negativo

print("--- PRUEBA 2: Registro y exportación del catálogo con stock válido ---")

try:
    # 1. Creamos un dispositivo válido con stock 90
    costo_dispositivo_ecologico_1 = PrecioProducto(
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
    precio_venta_1 = costo_dispositivo_ecologico_1.calcular_precio_venta()

    dispositivo_ecologico_1 = DispositivoEcologico(
        categoria=Categoria.ENERGIA_SOLAR,
        tipo_producto=TipoProducto.PANEL_SOLAR,
        codigo_producto="PANEL_SOLAR-001",
        nombre="Panel Solar Monocristalino PERC",
        descripcion="""Panel fotovoltaico de alta eficiencia con tecnología
        Half-Cell para proyectos industriales.""",
        fecha_produccion=date(2026, 11, 1),
        fecha_garantia=date(2051, 11, 1),
        degradacion_anual_max=0.55,
        precio_venta=costo_dispositivo_ecologico_1,
    )
    stock_1 = dispositivo_ecologico_1.stock = 90
    panel_solar_1 = PanelSolar(
        categoria=dispositivo_ecologico_1.categoria,
        tipo_producto=dispositivo_ecologico_1.tipo_producto,
        codigo_producto=dispositivo_ecologico_1.codigo_producto,
        nombre=dispositivo_ecologico_1.nombre,
        descripcion=dispositivo_ecologico_1.descripcion,
        stock=90,
        fecha_produccion=dispositivo_ecologico_1.fecha_produccion,
        fecha_garantia=dispositivo_ecologico_1.fecha_garantia,
        degradacion_anual_max=dispositivo_ecologico_1.degradacion_anual_max,
        precio_venta=dispositivo_ecologico_1.precio_venta,
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
    stock_1 = panel_solar_1.registrar_stock(90)
    # 2. Creamos un segundo dispositivo válido con stock 50
    costo_dispositivo_ecologico_2 = PrecioProducto(
        categoria=Categoria.ENERGIA_SOLAR,
        tipo_producto=TipoProducto.PANEL_SOLAR,
        codigo_producto="PANEL_SOLAR-003",
        estructura_costos={
            TipoCosto.INSUMOS: Decimal("180.00"),
            TipoCosto.MANO_DE_OBRA: Decimal("60.00"),
            TipoCosto.ELECTRICIDAD: Decimal("25.00"),
        },
        margen_ganancia=Decimal("30.00")
    )
    precio_venta_2 = costo_dispositivo_ecologico_2.calcular_precio_venta()

    dispositivo_ecologico_2 = DispositivoEcologico(
        categoria=Categoria.ENERGIA_SOLAR,
        tipo_producto=TipoProducto.PANEL_SOLAR,
        codigo_producto="PANEL_SOLAR-003",
        nombre="Panel Solar Bifacial N-Type TopCon 550W",
        descripcion="""Panel solar fotovoltaico bifacial de alta potencia
        con celdas de tecnología N-Type para máxima captación energética.""",
        fecha_produccion=date(2026, 8, 15),
        fecha_garantia=date(2051, 8, 15),
        degradacion_anual_max=0.40,
        precio_venta=costo_dispositivo_ecologico_2,
    )
    stock_2 = dispositivo_ecologico_2.stock = 75
    panel_solar_2 = PanelSolar(
        categoria=dispositivo_ecologico_2.categoria,
        tipo_producto=dispositivo_ecologico_2.tipo_producto,
        codigo_producto=dispositivo_ecologico_2.codigo_producto,
        nombre=dispositivo_ecologico_2.nombre,
        descripcion=dispositivo_ecologico_2.descripcion,
        stock=75,
        fecha_produccion=dispositivo_ecologico_2.fecha_produccion,
        fecha_garantia=dispositivo_ecologico_2.fecha_garantia,
        degradacion_anual_max=dispositivo_ecologico_2.degradacion_anual_max,
        precio_venta=dispositivo_ecologico_2.precio_venta,
        potencia_max_salida="550W",
        tolerancia_positiva="0/+10W",
        eficiencia_max=22.8,
        caracteristicas_generales={
            "Células": ["Monocristalinas N-Type Bifaciales 132 células"],
            "Resistencia": ["Carga de nieve 5400 Pa", "Carga de viento 2400 Pa"],
            "Tecnología": ["""Ganancia bifacial hasta 30% adicional por cara posterior"""]
        },
        dimensiones_modulo={"Módulo Completo": ("2278 mm", "1134 mm")},
        rendimiento_electrico={
            "1000 W/m2": (42.1, 550.0), 
            "800 W/m2": (41.5, 440.0), 
            "600 W/m2": (40.9, 330.0)
        },
        datos_electricos={
            "Tensión Vmp": ("V", 42.1), 
            "Corriente Imp": ("A", 13.07), 
            "Tensión Voc": ("V", 50.3)
        },
        datos_mecanicos={
            "Vidrio Frontal/Posterior": "2.0mm Templado Doblado", 
            "Marco": "Aluminio Anodizado Negro", 
            "Peso": 28.5
        },
        datos_adicionales={
            "Temperatura Operativa": "-40°C a +85°C", 
            "Conector": "MC4 EVO2 Compatible"
        }
    )
    stock_2 = panel_solar_2.registrar_stock(75)

    # Stock actualizado. Nuevo stock: 90
    # Stock actualizado. Nuevo stock: 75

    registro = GestorInventario()
    lista_paneles = [panel_solar_1, panel_solar_2]
    registro_ecotech = registro.guardar_registros_json(
        lista_registros=lista_paneles,
        ruta_archivo=Path("ejercicio_2_productos/registros_ecotech.json"))
    
    print("Registro guardado de forma exitosa")

    catalogo_ecotech = registro.guardar_catalogo_json(
        lista_paneles,
        ruta_archivo=Path("ejercicio_2_productos/catalogo_ecotech.json"),
    )
    print("Catálogo guardado de forma exitosa")

    reporte = ReporteCatalogo()
    reporte.generar_catalogo_pdf(
        ruta_json="ejercicio_2_productos/catalogo_ecotech.json",
        ruta_pdf="ejercicio_2_productos/ficha_tecnica_panel_solar.pdf"
    )
    print("¡Catálogo exportado exitosamente sin errores de stock!")

except StockInvalidoError as e:
    print(f"Error inesperado de stock: {e.message}")


# ¡Reporte PDF generado exitosamente!
# Guardado en: \ecotech_solutions\ejercicio_1_sensores\reporte_sensores.pdf'.
# ¡Catálogo exportado exitosamente!
# Guardado en: \ecotech_solutions\ejercicio_2_productos\catalogo_ecotech.json'.
# ¡Ficha Técnica PDF generada con éxito!
# Guardado en: \ecotech_solutions\ejercicio_2_productos\ficha_tecnica_panel_solar.pdf'.


maquinarias_datos = [
    {
        "tipo_maquinaria": TipoMaquinaria.INSPECCION_CLASIFICACION,
        "codigo_maquinaria": "INSPECCION_CLASIFICACION-001",
        "nombre_maquinaria": "Mesa de Inspección Óptica de Obleas",
        "potencia_watts": 3500.0,  # 3.5 kW (Sistemas ópticos y de transporte)
        "horas_dia": 16.0,
        "dias_mes": 22,
        "tarifa_kwh": 0.15,      # USD por kWh
        "factor_carga": 0.85,
    },
    {
        "tipo_maquinaria": TipoMaquinaria.CORTADORA_LASER,
        "codigo_maquinaria": "CORTADORA_LASER-001",
        "nombre_maquinaria": "Cortadora Láser de Células Half-Cell",
        "potencia_watts": 12000.0,  # 12 kW (Láser de alta precisión)
        "horas_dia": 16.0,
        "dias_mes": 22,
        "tarifa_kwh": 0.15,
        "factor_carga": 0.90,
    },
    {
        "tipo_maquinaria": TipoMaquinaria.ENCADENADO,
        "codigo_maquinaria": "ENCADENADO-001",
        "nombre_maquinaria": "Soldadora Automática de Células (Stringer)",
        "potencia_watts": 8500.0,  # 8.5 kW (Soldadura infrarroja/láser)
        "horas_dia": 16.0,
        "dias_mes": 22,
        "tarifa_kwh": 0.15,
        "factor_carga": 0.90,
    },
    {
        "tipo_maquinaria": TipoMaquinaria.LAMINADORA,
        "codigo_maquinaria": "LAMINADORA-001",
        "nombre_maquinaria": "Laminadora al Vacío de Alta Capacidad",
        # 35 kW (Altos requerimientos térmicos por resistencias)
        "potencia_watts": 35000.0,
        "horas_dia": 18.0,
        "dias_mes": 22,
        "tarifa_kwh": 0.15,
        "factor_carga": 0.95,
    },
    {
        "tipo_maquinaria": TipoMaquinaria.SIMULADOR_SOLAR,
        "codigo_maquinaria": "SIMULADOR_SOLAR-001",
        "nombre_maquinaria": "Simulador Solar Flash (Prueba STC)",
        # 15 kW (Destellos de alta intensidad lumínica)
        "potencia_watts": 15000.0,
        "horas_dia": 10.0,
        "dias_mes": 22,
        "tarifa_kwh": 0.15,
        "factor_carga": 0.80,
    },
]

registros_consumos_kwh = []

# Procesamos cada máquina utilizando la clase CalculadoraConsumoIndustrial
for datos in maquinarias_datos:
    calculadora = CalculadoraConsumoIndustrial(
        tipo_maquinaria=datos["tipo_maquinaria"],
        codigo_maquinaria=datos["codigo_maquinaria"],
        nombre_maquinaria=datos["nombre_maquinaria"],
        potencia_watts=float(datos["potencia_watts"]),
        horas_dia=float(datos["horas_dia"]),
        dias_mes=int(datos["dias_mes"]),
        tarifa_kwh=float(datos["potencia_watts"]),
        factor_carga=float(datos["factor_carga"]),
    )

    # Obtenemos el diccionario con el consumo calculado
    resultado_equipo = calculadora.calcular_consumo_kwh()
    registros_consumos_kwh.append(resultado_equipo)

    print(f"[{datos['codigo_maquinaria']}] {datos['nombre_maquinaria']} -> Consumo: {resultado_equipo['costo_mensual']} kWh/mes")

    # Ruta de salida para el archivo JSON
    ruta_json = Path(
        "ejercicio_3_auditoria_web/consumo_maquinaria_planta.json")
    ruta_json.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo_out:
            json.dump(
                registros_consumos_kwh,
                archivo_out,
                ensure_ascii=False,
                indent=4,
                default=lambda o: float(o) if isinstance(
                    o, Decimal) else str(o)
            )
        print(
            f"\n¡Éxito! Se guardaron {len(registros_consumos_kwh)} registros de maquinaria en: '{ruta_json.resolve()}'")
    except OSError as e:
        print(f"Error al exportar el archivo JSON: {e}")


# [INSPECCION_CLASIFICACION-001] Mesa de Inspección Óptica de Obleas -> Consumo: 3665200.0 kWh/mes
# [CORTADORA_LASER-001] Cortadora Láser de Células Half-Cell -> Consumo: 45619200.0 kWh/mes
# [ENCADENADO-001] Soldadora Automática de Células(Stringer) -> Consumo: 22888800.0 kWh/mes
# [LAMINADORA-001] Laminadora al Vacío de Alta Capacidad -> Consumo: 460845000.0 kWh/mes
# [SIMULDOR_SOLAR-001] Simulador Solar Flash(Prueba STC) -> Consumo: 39600000.0 kWh/mes
# ¡Éxito! Se guardaron 5 registros de maquinaria en: '\ejercicio_3_auditoria_web\consumo_maquinaria_planta.json'

consumo_total_datos = CalculadoraConsumoIndustrial.calcular_consumo_total(
    ruta_json)
consumo_total_planta = consumo_total_datos.get("consumo_global_kwh", 0.0)

auditoria = AuditoriaHuellaCarbono(
    producto=panel_solar_1,
    etapa_producto=EtapaProducto.A3,
    consumo_kwh=consumo_total_planta,
    factor_emision=0.4,
)
metricas = auditoria.obtener_metricas_consumo(
    registros_consumos_kwh, ruta_json)
emisiones = auditoria.calcular_emisiones_carbono()

print("\n--- AUDITORÍA DE HUELLA DE CARBONO ---")
print(f"Consumo Global Planta: {consumo_total_planta} kWh")
print(f"Emisiones Totales de CO2: {emisiones} kg CO2e")

# --- AUDITORÍA DE HUELLA DE CARBONO ---
# Consumo Global Planta: 23348.6 kWh
# Emisiones Totales de CO2: 9339 kg CO2e

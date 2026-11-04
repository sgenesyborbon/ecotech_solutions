
from datetime import date
from decimal import Decimal

import pytest

from ejercicio_2_productos.dispositivos_ecologicos import DispositivoEcologico
from ejercicio_2_productos.formula_precio import PrecioProducto
from ejercicio_2_productos.paneles_solares import PanelSolar
from ejercicio_3_auditoria_web.auditoria_emisiones import AuditoriaHuellaCarbono
from ejercicio_3_auditoria_web.calculadora_consumo import CalculadoraConsumoIndustrial
from shared.enums.enums import (
    Categoria,
    EtapaProducto,
    TipoCosto,
    TipoMaquinaria,
    TipoProducto,
)
from shared.exceptions.exception import ValidationError


@pytest.fixture
def panel_solar_fixture():
    """Fixture para proveer una instancia válida de PanelSolar."""

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
        descripcion="Panel fotovoltaico de alta eficiencia.",
        fecha_produccion=date(2026, 11, 1),
        fecha_garantia=date(2051, 11, 1),
        degradacion_anual_max=0.55,
        precio_venta=costo_dispositivo
    )

    return PanelSolar(
        categoria=dispositivo_ecologico.categoria,
        tipo_producto=dispositivo_ecologico.tipo_producto,
        codigo_producto=dispositivo_ecologico.codigo_producto,
        nombre=dispositivo_ecologico.nombre,
        descripcion=dispositivo_ecologico.descripcion,
        stock=100,
        fecha_produccion=dispositivo_ecologico.fecha_produccion,
        fecha_garantia=dispositivo_ecologico.fecha_garantia,
        degradacion_anual_max=dispositivo_ecologico.degradacion_anual_max,
        precio_venta=dispositivo_ecologico.precio_venta,
        potencia_max_salida="450W",
        tolerancia_positiva="0/+5W",
        eficiencia_max=20.7,
        caracteristicas_generales={"Células": ["Monocristalinas"]},
        dimensiones_modulo={"Módulo Completo": ("2094 mm", "1038 mm")},
        rendimiento_electrico={"1000 W/m2": (41.5, 450.0)},
        datos_electricos={"Tensión Vmp": ("V", 41.5)},
        datos_mecanicos={"Peso": 23.5},
        datos_adicionales={"Conector": "MC4 Compatible"}
    )


@pytest.fixture
def laminadora_fixture():
    """Fixture que provee una instancia de CalculadoraConsumoIndustrial."""

    return CalculadoraConsumoIndustrial(
        tipo_maquinaria=TipoMaquinaria.LAMINADORA,
        codigo_maquinaria="LAMINADORA-001",
        nombre_maquinaria="Laminadora al Vacío de Alta Capacidad",
        potencia_watts=35000.0,
        horas_dia=18.0,
        dias_mes=22,
        tarifa_kwh=0.15,
        factor_carga=0.95,
    )


# --- 1. PRUEBAS DE CALCULADORA DE CONSUMO ---
def test_calculadora_instancia_y_tipos(laminadora_fixture):
    """Verifica que la calculadora se instancie y devuelva los tipos de datos correctos."""

    assert isinstance(laminadora_fixture, CalculadoraConsumoIndustrial)
    
    resultado = laminadora_fixture.calcular_consumo_kwh()
    assert isinstance(resultado, dict)
    assert "kwh_mensual" in resultado
    assert "costo_mensual" in resultado
    assert isinstance(resultado["kwh_mensual"], float)
    assert isinstance(resultado["costo_mensual"], float)


def test_calculadora_exactitud_calculo(laminadora_fixture):
    """Valida la exactitud matemática del consumo industrial formulado."""

    # Fórmula: ((Watts * Horas/Día * Días/Mes) / 1000) * Factor de Carga
    # ((35000 * 18 * 22) / 1000) * 0.95 = (13860.0) * 0.95 = 13167.0 kWh
    resultado = laminadora_fixture.calcular_consumo_kwh()
    esperado_kwh = 13167.0
    assert pytest.approx(resultado["kwh_mensual"], 0.01) == esperado_kwh


# --- 2. PRUEBAS DE AUDITORÍA DE HUELLA DE CARBONO ---

def test_auditoria_instancia_y_tipos(panel_solar_fixture):
    """Verifica la instanciación correcta de PanelSolar y tipos de datos en Auditoría."""

    auditoria = AuditoriaHuellaCarbono(
        producto=panel_solar_fixture,
        etapa_producto=EtapaProducto.A3,
        consumo_kwh=1000.0,
        factor_emision=0.4,
    )
    
    assert isinstance(auditoria, AuditoriaHuellaCarbono)
    assert isinstance(auditoria.producto, PanelSolar)
    assert isinstance(auditoria.etapa_producto, EtapaProducto)
    assert isinstance(auditoria.consumo_kwh, float)
    assert isinstance(auditoria.factor_emision, float)


def test_auditoria_exactitud_emisiones(panel_solar_fixture):
    """Valida la exactitud del cálculo de emisiones de carbono."""

    auditoria = AuditoriaHuellaCarbono(
        producto=panel_solar_fixture,
        etapa_producto=EtapaProducto.A3,
        consumo_kwh=1000.0,
        factor_emision=0.4,
    )
    # 1000.0 * 0.4 = 400.0 (redondeado)
    emisiones = auditoria.calcular_emisiones_carbono()
    assert isinstance(emisiones, (int, float))
    assert emisiones == 400.0


def test_auditoria_validadores_tipo_error():
    """Comprueba que el DataValidator rechace tipos incorrectos o negativos."""

    # Consumo negativo debe lanzar ValueError en calcular_emisiones
    auditoria_negativa = AuditoriaHuellaCarbono(consumo_kwh=100.0, factor_emision=0.4)
    auditoria_negativa.consumo_kwh = -50.0
    
    with pytest.raises(ValueError, match="no puede ser negativo"):
        auditoria_negativa.calcular_emisiones_carbono()

    # Pasar un tipo inválido en el constructor debe disparar ValidationError
    with pytest.raises(ValidationError):
        AuditoriaHuellaCarbono(consumo_kwh="no_es_un_numero", factor_emision=0.4)
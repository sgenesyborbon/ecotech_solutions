from enum import StrEnum


class Categoria(StrEnum):
    """Categoría de dispositivos ecológicos utilizados en distintas industrias"""

    ENERGIA_SOLAR = "Energía Solar"
    ALMACENAMIENTO_ENERGIA = "Almacenamiento de Energía"  # Para baterías
    GESTION_RESIDUOS = "Gestión de Residuos"            # Para sistemas de reciclaje
    CLIMATIZACION = "Climatización y Confort"             # Para termostatos
    MONITOREO_INDUSTRIAL = "Monitoreo Industrial"       # Para toda la familia de sensores térmicos
    OTRO = "Otro"

class TipoSensor(StrEnum):
    """Tipos de sensores utilizados en distintas industrias"""

    TERMOPARES = "Termopares"              # Rango entre -200 °C hasta 2000 °C
    TERMORESISTENCIAS = "Termoresistencias" # Rango entre -200 °C y 850 °C
    TERMISTORES = "Termistores"           # Rango entre -50 °C y 450 °C
    PIROMETROS = "Pirómetros"             # Rango entre -50 °C y 3000 °C
    SENSOR_DESCONOCIDO = "Sensor Desconocido"
    OTRO = "Otro"


class TipoProducto(StrEnum):
    """Tipos específicos de dispositivos y equipos ecológicos del catálogo"""

    PANEL_SOLAR = "Panel Solar"
    BATERIA_RECARGABLE = "Batería Recargable"
    SISTEMA_RECICLAJE = "Sistema de Reciclaje"
    TERMOSTATO_INTELIGENTE = "Termostato Inteligente"
    SENSOR_EFICIENCIA = "Sensor de Eficiencia Energética"
    OTRO = "Otro"


class Ubicacion(StrEnum):
    """Código identificatorio para la ubicación de sensores"""

    PLANTA_ESTE = "Planta Este"
    PLANTA_OESTE = "Planta Oeste"
    PLANTA_NORTE = "Planta Norte"
    PLANTA_SUR = "Planta Sur"
    AREA_NO_ASIGNADA = "Area No Asignada"


class TipoCosto(StrEnum):
    """Categorías de costos empresariales para la fabricación"""

    ALQUILER = "alquiler"
    LUZ = "luz"
    ELECTRICIDAD = "electricidad"
    MANO_DE_OBRA = "mano_de_obra"
    PUBLICIDAD = "publicidad"
    FINANCIAMIENTO = "financiamiento"
    INSUMOS = "insumos"


class EtapaProducto(StrEnum):
    """Etapas de Producción para cálculos de huella de carbono"""

    A1 = "Suministro de Materias Primas"
    A2 = "Transporte"
    A3 = "Fabricación"


class TipoMaquinaria(StrEnum):
    """Tipos de máquinas requeridas para la producción de paneles solares
    fotovoltaicos en serie"""

    INSPECCION_CLASIFICACION = "Máquina de Inspección y Clasificación de Obleas"
    CORTADORA_LASER = "Cortadora Láser de Células"
    ENCADENADO = "Máquina de Encadenado de Células"
    ESTACION_ENCORDADO = "Estación de Encordado y Conexión de Cadenas"
    LAMINADORA = "Máquina Laminadora al Vacío"
    ESTACION_ENMARCADO_AUTOMATICO = "Estación de Enmarcado Automático"
    CURADORA_SILICONA = "Curadora de Silicona"
    SIMULADOR_SOLAR = "Simulador Solar Flash"
    PRUEBAS_ELECTROLUMINISCENCIA = "Máquina de Pruebas de Electroluminiscencia"
    ENSACADORA_ENCORDADORA = "Ensacadora y Encordadora Final de Embalaje"
    OTRA_MAQUINA = "Otra Máquina"


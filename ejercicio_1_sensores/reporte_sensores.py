from datetime import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ejercicio_1_sensores.sensores import Sensor
from shared.validators.data_validator import DataValidator


class ReporteSensores:
    """Genera reportes estadísticos de los sensores en PDF"""

    def generar_reporte_pdf(
        self,
        sensor: Sensor,
        ruta_pdf: Path | str = "reporte_sensores.pdf",
   ) -> None:
        """ Calcula estadísticas con Pandas/NumPy y genera un informe PDF
        con tablas y gráficos"""

        sensor = DataValidator.validar_clase(
            value=sensor,
            expected_class=Sensor,
            field_name="sensor",
            allow_none=False,
        )

        # Extrae la lista de sensores limpios directamente de la instancia de Sensor
        lista_datos = getattr(sensor, "lista_sensores_limpios", [])

        # Si la lista está vacía o contiene solo dicts vacíos, cancelar generación
        if not lista_datos or lista_datos == [{}]:
            print("No hay datos limpios cargados para generar el reporte.")
            return
    
        lista_sensores_alerta, promedio_temperatura = sensor.generar_resumen_sensores()

        df = pd.DataFrame(lista_datos)
        total_registros = len(df)
        total_alertas = len(lista_sensores_alerta)
        porcentaje_alertas = (total_alertas / total_registros * 100) if total_registros > 0 else 0.0

        # Cálculos Estadísticos con Pandas y NumPy
        promedio_temperatura = float(np.mean(df["temperatura"]))
        temp_max = float(np.max(df["temperatura"])) if not df.empty else 0.0
        temp_min = float(np.min(df["temperatura"])) if not df.empty else 0.0
        estado_planta = "ALERTA" if total_alertas > 0 else "NORMAL"

        # Agrupación por Ubicación usando Pandas
        promedio_por_ubicacion = df.groupby("ubicacion")["temperatura"].mean().round(2).to_dict()

        df_alertas = df[df["codigo_producto"].isin(
            sensor.lista_sensores_alerta)] if not df.empty else pd.DataFrame()

        # Configuración del Documento PDF
        ruta_salida = Path(ruta_pdf)
        doc = SimpleDocTemplate(
            str(ruta_salida),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []
        estilos = getSampleStyleSheet()

        # Paleta de Colores EcoTech
        COLOR_PRIMARIO = colors.HexColor("#319CBD")
        COLOR_SECUNDARIO = colors.HexColor("#59ACC5")
        COLOR_ALERTA = colors.HexColor("#E74C3C")
        COLOR_TEXTO = colors.HexColor("#1C1917")
        COLOR_FONDO = colors.HexColor("#F0F8F9")
        COLOR_BORDE = colors.HexColor("#C5DBE2")

        # Estilos de Texto
        estilos.add(ParagraphStyle(
            name="TituloTech",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=COLOR_PRIMARIO,
            alignment=TA_LEFT,
        ))
        estilos.add(ParagraphStyle(
            name="SubtituloTech",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=COLOR_SECUNDARIO,
            alignment=TA_LEFT,
        ))
        estilos.add(ParagraphStyle(
            name="TextoNormal",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=COLOR_TEXTO,
        ))

        # --- Encabezado ---
        story.append(Paragraph("ECOTECH SOLUTIONS - REPORTE TÉRMICO", estilos["TituloTech"]))
        story.append(Paragraph("Monitoreo y Mapeo Estadístico de Planta", estilos["SubtituloTech"]))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARIO, spaceAfter=15))

        # --- Resumen Ejecutivo (Tabla Resumen) ---
        fecha_str = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        resumen_data = [
            ["Fecha de Reporte:", fecha_str,
                "Total Registros:", str(total_registros)],
            ["Promedio Global:", f"{promedio_temperatura:.2f} °C", "Sensores en Alerta:",
                f"{total_alertas} ({porcentaje_alertas:.1f}%)"],
            ["Temp. Máxima:", f"{temp_max:.1f} °C",
                "Temp. Mínima:", f"{temp_min:.1f} °C"],
            ["Estado Planta:", estado_planta, "", ""]
        ]

        t_resumen = Table(resumen_data, colWidths=[110, 140, 120, 140])
        t_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO),
            ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_TEXTO),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_resumen)
        story.append(Spacer(1, 15))

        # --- Gráfico de Promedios por Ubicación ---
        story.append(Paragraph("Promedio de Temperatura por Ubicación (°C)", estilos["SubtituloTech"]))
        story.append(Spacer(1, 5))

        # Construcción del Gráfico de Barras nativo de ReportLab
        d = Drawing(520, 140)
        bc = VerticalBarChart()
        bc.x = 40
        bc.y = 25
        bc.height = 95
        bc.width = 440
        bc.data = [list(promedio_por_ubicacion.values())]
        bc.categoryAxis.categoryNames = list(promedio_por_ubicacion.keys())
        bc.categoryAxis.labels.fontSize = 8
        bc.categoryAxis.labels.dy = -10
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(promedio_por_ubicacion.values()) + 20 if promedio_por_ubicacion else 100
        bc.bars[0].fillColor = COLOR_PRIMARIO
        d.add(bc)
        
        story.append(d)
        story.append(Spacer(1, 15))

        # --- Tabla de Sensores en Alerta ---
        story.append(Paragraph("Dispositivos en Alerta (Fuera de Rango Umbral)", estilos["SubtituloTech"]))
        story.append(Spacer(1, 5))

        if not df_alertas.empty:
            # Cabecera de la tabla de alertas
            alertas_tabla_data = [["Código Producto", "Tipo Sensor", "Ubicación",
                                   "Fecha/Hora", "Temperatura (°C)"]]
    
            for _, fila in df_alertas.iterrows():
                alertas_tabla_data.append([
                    str(fila["codigo_producto"]),
                    str(fila["tipo_sensor"]),
                    str(fila["ubicacion"]),
                    str(fila["dia_registro"]),
                    f"{fila['temperatura']:.1f}"
                ])
            
            t_alerta = Table(alertas_tabla_data, colWidths=[130, 130, 150, 100])
            t_alerta.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_ALERTA),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ]))
            story.append(t_alerta)
        else:
            story.append(Paragraph("No se registraron sensores superando el umbral de alerta.", estilos["TextoNormal"]))

        # --- CONSTRUCCIÓN FINAL DEL PDF (Una sola llamada) ---
        doc.build(story)
        print(f"¡Reporte PDF generado exitosamente!\n"
              f"Guardado en: '{ruta_salida.resolve()}'.")
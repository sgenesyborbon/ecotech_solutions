import base64
import io
import json
from io import BytesIO
from pathlib import Path
from smtplib import SMTPException

from django.contrib import messages
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as RLImage,
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def vista_panel_sustentabilidad(request):
    """ Función llama al diccionario para ser utilizado en panel.html"""

    # Ruta donde tu script ya guardó exitosamente el archivo JSON
    ruta_json = Path("ejercicio_3_auditoria_web/metricas_sustentabilidad.json")

    # Valores por defecto por si el archivo no se encuentra
    consumo_global_kwh = 0.0
    total_emisiones = 0.0
    maquina_mayor_consumo = "N/A"
    registros_maquinaria = []

    # Leemos el archivo JSON directamente (el mismo que creó tu script)
    if ruta_json.exists():
        with open(ruta_json, "r", encoding="utf-8") as f:
            contenido = json.load(f)
            
            # Si tu JSON es la lista de registros directa o un diccionario global
            if isinstance(contenido, list):
                registros_maquinaria = contenido
            elif isinstance(contenido, dict):
                registros_maquinaria = contenido.get("registros", [])

        # Calculamos los totales directamente en la vista para asegurarnos de que la plantilla reciba los datos
        for reg in registros_maquinaria:
            kwh = float(reg.get("kwh_mensual", 0.0))
            consumo_global_kwh += kwh
            
            # Si el JSON guarda el costo o emisiones, los sumamos, o aplicamos el factor 0.4
            total_emisiones += kwh * 0.4

        # Determinamos la máquina de mayor consumo del listado
        if registros_maquinaria:
            max_reg = max(registros_maquinaria, key=lambda x: float(x.get("kwh_mensual", 0.0)))
            maquina_mayor_consumo = max_reg.get("nombre_maquinaria", "Desconocida")
            nombres_maquinarias = [reg.get("nombre_maquinaria") for reg in registros_maquinaria]
            consumos_mensuales = [float(reg.get("kwh_mensual", 0.0)) for reg in registros_maquinaria]
            costos_mensuales = [float(reg.get("costo_mensual", 0.0)) for reg in registros_maquinaria]
            costo_global_planta = sum(float(reg.get("costo_mensual", 0.0)) for reg in registros_maquinaria)
            costo_global_formateado = f"{costo_global_planta:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Preparamos el diccionario de contexto exacto que espera tu template panel.html
    context = {
        "titulo": "Panel Administrativo de Sustentabilidad",
        "consumo_global": round(consumo_global_kwh, 2),
        "total_emisiones": round(total_emisiones, 2),
        "costo_global": costo_global_formateado,
        "mayor_consumo": maquina_mayor_consumo,
        "lista_registros": registros_maquinaria,
        "nombres_json": json.dumps(nombres_maquinarias, ensure_ascii=False),
        "consumos_json": json.dumps(consumos_mensuales),
        "costos_json": json.dumps(costos_mensuales),
    }

    return render(request, "panel_sustentabilidad.html", context)


def exportar_pdf_view(request):
    ruta_json = Path(
        "ejercicio_3_auditoria_web/consumo_maquinaria_planta.json")

    registros_maquinaria = []
    consumo_global_kwh = 0.0
    total_emisiones = 0.0

    if ruta_json.exists():
        with open(ruta_json, "r", encoding="utf-8") as f:
            contenido = json.load(f)
            if isinstance(contenido, list):
                registros_maquinaria = contenido
            elif isinstance(contenido, dict):
                registros_maquinaria = contenido.get("registros", [])

        for reg in registros_maquinaria:
            kwh = float(reg.get("kwh_mensual", 0.0))
            consumo_global_kwh += kwh
            total_emisiones += kwh * 0.4

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_sustentabilidad_ecotech.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    estilos = getSampleStyleSheet()

    COLOR_PRIMARIO = colors.HexColor("#198754")
    COLOR_SECUNDARIO = colors.HexColor("#0d6efd")
    COLOR_TEXTO = colors.HexColor("#212529")
    COLOR_FONDO = colors.HexColor("#f8f9fa")
    COLOR_BORDE = colors.HexColor("#dee2e6")

    estilos.add(ParagraphStyle(name='TituloPDF', fontName='Helvetica-Bold',
                fontSize=18, leading=22, textColor=COLOR_PRIMARIO))
    estilos.add(ParagraphStyle(name='SubtituloPDF', fontName='Helvetica-Bold',
                fontSize=10, leading=14, textColor=colors.gray))
    estilos.add(ParagraphStyle(name='TextoNormal', fontName='Helvetica',
                fontSize=9, leading=12, textColor=COLOR_TEXTO))
    estilos.add(ParagraphStyle(name='TextoNegrita', fontName='Helvetica-Bold',
                fontSize=9, leading=12, textColor=COLOR_TEXTO))

    # Encabezado
    story.append(Paragraph("ECOTECH SOLUTIONS", estilos["SubtituloPDF"]))
    story.append(Paragraph(
        "Reporte Ejecutivo de Sustentabilidad y Consumo Energético", estilos["TituloPDF"]))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2,
                 color=COLOR_PRIMARIO, spaceAfter=12))

    # KPIs Generales
    costo_global_planta = sum(float(r.get('costo_mensual', 0))
                              for r in registros_maquinaria)
    costo_global_str = f"{costo_global_planta:,.2f}".replace(
        ",", "X").replace(".", ",").replace("X", ".")

    kpi_data = [
        [
            Paragraph("<b>Consumo Global</b>", estilos["TextoNegrita"]),
            Paragraph("<b>Emisiones Totales</b>", estilos["TextoNegrita"]),
            Paragraph("<b>Costo Mensual Total</b>", estilos["TextoNegrita"])
        ],
        [
            Paragraph(f"{consumo_global_kwh:,.2f} kWh",
                      estilos["TextoNormal"]),
            Paragraph(f"{total_emisiones:,.2f} kg CO₂",
                      estilos["TextoNormal"]),
            Paragraph(f"$ {costo_global_str}", estilos["TextoNormal"])
        ]
    ]
    t_kpis = Table(kpi_data, colWidths=[175, 175, 174])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 12))

    # --- CAPTURAR E INSERTAR EL GRÁFICO DESDE EL CLIENTE ---
    imagen_base64 = request.POST.get('grafico_imagen')
    if imagen_base64 and "data:image/png;base64," in imagen_base64:
        try:
            # Extraemos los datos binarios de la imagen base64
            _, imgstr = imagen_base64.split(';base64,')
            img_data = base64.b64decode(imgstr)
            img_io = BytesIO(img_data)

            # Insertamos la imagen en el PDF con un ancho adecuado (ej. 500 puntos)
            story.append(Paragraph(
                "<b>Gráfico Comparativo de Consumo y Costo por Maquinaria</b>", estilos["TextoNegrita"]))
            story.append(Spacer(1, 4))
            story.append(RLImage(img_io, width=500, height=200))
            story.append(Spacer(1, 12))
        except (ValueError, TypeError) as e:
            pass  # Si ocurre algún error al procesar la imagen, continúa sin romper el PDF

    # Detalle de Maquinaria
    story.append(
        Paragraph("Desglose Operativo por Maquinaria", estilos["TituloPDF"]))
    story.append(Spacer(1, 6))

    rows_tabla = [[
        Paragraph("<b>Maquinaria / Planta</b>", estilos["TextoNegrita"]),
        Paragraph("<b>Consumo (kWh)</b>", estilos["TextoNegrita"]),
        Paragraph("<b>Costo Mensual ($)</b>", estilos["TextoNegrita"])
    ]]

    for reg in registros_maquinaria:
        costo_maq = float(reg.get('costo_mensual', 0))
        costo_maq_str = f"{costo_maq:,.2f}".replace(
            ",", "X").replace(".", ",").replace("X", ".")
        rows_tabla.append([
            Paragraph(str(reg.get("nombre_maquinaria", "")),
                      estilos["TextoNormal"]),
            Paragraph(f"{float(reg.get('kwh_mensual', 0)):,.2f}",
                      estilos["TextoNormal"]),
            Paragraph(f"$ {costo_maq_str}", estilos["TextoNormal"])
        ])

    t_detalle = Table(rows_tabla, colWidths=[240, 130, 154])
    t_detalle.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_detalle)

    doc.build(story)
    return response

def enviar_correo_reporte_view(request):
    """
    Vista de Django que genera el PDF de sustentabilidad al vuelo,
    lo adjunta y lo envía por correo electrónico a un destinatario configurado.
    """
    ruta_json = Path("ejercicio_3_auditoria_web/consumo_maquinaria_planta.json")
    
    registros_maquinaria = []
    consumo_global_kwh = 0.0
    total_emisiones = 0.0

    if ruta_json.exists():
        with open(ruta_json, "r", encoding="utf-8") as f:
            contenido = json.load(f)
            if isinstance(contenido, list):
                registros_maquinaria = contenido
            elif isinstance(contenido, dict):
                registros_maquinaria = contenido.get("registros", [])

        for reg in registros_maquinaria:
            kwh = float(reg.get("kwh_mensual", 0.0))
            consumo_global_kwh += kwh
            total_emisiones += kwh * 0.4

    # 1. Generar el PDF en memoria usando io.BytesIO (sin guardarlo físicamente en el disco)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    estilos = getSampleStyleSheet()

    COLOR_PRIMARIO = colors.HexColor("#198754")
    COLOR_TEXTO = colors.HexColor("#212529")
    COLOR_FONDO = colors.HexColor("#f8f9fa")
    COLOR_BORDE = colors.HexColor("#dee2e6")

    estilos.add(ParagraphStyle(name='TituloPDF', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=COLOR_PRIMARIO))
    estilos.add(ParagraphStyle(name='SubtituloPDF', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.gray))
    estilos.add(ParagraphStyle(name='TextoNormal', fontName='Helvetica', fontSize=8.5, leading=11, textColor=COLOR_TEXTO))
    estilos.add(ParagraphStyle(name='TextoNegrita', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=COLOR_TEXTO))

    story.append(Paragraph("ECOTECH SOLUTIONS", estilos["SubtituloPDF"]))
    story.append(Paragraph("Monitoreo de Emisiones y Consumo Energético", estilos["TituloPDF"]))
    story.append(Spacer(1, 8))

    # Resumen de KPIs para el cuerpo del correo/PDF
    kpi_data = [
        [
            Paragraph("<b>Consumo Global</b>", estilos["TextoNegrita"]),
            Paragraph("<b>Emisiones Totales</b>", estilos["TextoNegrita"]),
            Paragraph("<b>Costo Mensual Total</b>", estilos["TextoNegrita"])
        ],
        [
            Paragraph(f"{consumo_global_kwh:,.2f} kWh", estilos["TextoNormal"]),
            Paragraph(f"{total_emisiones:,.2f} kg CO₂", estilos["TextoNormal"]),
            Paragraph(f"$ {sum(float(r.get('costo_mensual', 0)) for r in registros_maquinaria):,.2f}", estilos["TextoNormal"])
        ]
    ]
    t_kpis = Table(kpi_data, colWidths=[175, 175, 174])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_kpis)
    
    doc.build(story)
    pdf_buffer_value = buffer.getvalue()
    buffer.close()

    # 2. Configurar y enviar el correo electrónico con el PDF adjunto
    destinatario = request.POST.get('email_destino', 'admin@ecotechsolutions.com') # O un correo por defecto
    asunto = "Reporte Ejecutivo de Sustentabilidad - EcoTech Solutions"
    cuerpo_mensaje = (
        "Hola,\n\n"
        "En archivo adjunto encontrarás el reporte automatizado de sustentabilidad, consumo energético "
        "y emisiones de CO₂ generado por el sistema EcoTech Solutions.\n\n"
        "Atentamente,\n"
        "Sistema de Auditoría Energética"
    )

    try:
        email = EmailMessage(
            subject=asunto,
            body=cuerpo_mensaje,
            from_email=None,  # Utiliza DEFAULT_FROM_EMAIL configurado en settings.py
            to=[destinatario],
        )
        # Adjuntamos el PDF generado en memoria
        email.attach("reporte_sustentabilidad_ecotech.pdf", pdf_buffer_value, "application/pdf")
        email.send()
        
        messages.success(request, f"¡Reporte enviado con éxito a {destinatario}!")

    except BadHeaderError:
        messages.error(request, "Error de seguridad: Se detectaron cabeceras inválidas en el correo electrónico.")
    except SMTPException as e:
        messages.error(request, f"Error de conexión o infraestructura SMTP al enviar el correo: {e}")

    return redirect('panel_sustentabilidad')
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class ReporteCatalogo:
    """Genera el catálogo en pdf de los dispositivos guardados en memoria"""

    def dibujar_fondo(self, canvas, doc):
        """Dibuja un rectángulo que cubre toda la página con el color de base."""

        canvas.saveState()
        # 1. Define el color de fondo (puedes usar colores predefinidos o Hex)
        canvas.setFillColor(colors.HexColor("#E1F1F5")) 
        # 2. Dibuja el rectángulo desde la esquina (0,0) hasta el ancho y alto del PDF
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        canvas.restoreState()

    def generar_catalogo_pdf(
        self,
        ruta_json: str | Path,
        ruta_pdf: str | Path,
    ) -> None:
        "Catálogo con ficha técnica del producto"

        ruta_j = Path(ruta_json)
        if not ruta_j.exists():
            print(f"No se encontró el archivo de catálogo en {ruta_j}")
            return

        with open(ruta_j, 'r', encoding='utf-8') as f:
            catalogo_data = json.load(f)

            # Configuración del Catálogo PDF con márgenes estándar
            doc = SimpleDocTemplate(
                str(ruta_pdf),
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            story = []
            estilos = getSampleStyleSheet()

            # Paleta de Colores EcoTech
            COLOR_PRIMARIO = colors.HexColor("#319CBD")
            COLOR_TEXTO = colors.HexColor("#1C1917")
            COLOR_DESTACADO = colors.HexColor("#0284C7")
            COLOR_GRID = colors.HexColor("#ABC5C4")

            # Estilos de Texto corregidos (Corregido 'fontsize' por 'fontSize')
            titulo_style = ParagraphStyle(
                name="TituloEmpresa",
                parent=estilos['Heading1'],
                fontSize=20,
                leading=24,
                textColor=COLOR_DESTACADO,
                spaceAfter=6,
                alignment=1  # Centrado
            )
            subtitulo_style = ParagraphStyle(
                name="SubTitulo",
                parent=estilos['Normal'],
                fontSize=10,
                textColor=COLOR_PRIMARIO,
                spaceAfter=15,
                alignment=1
            )
            seccion_style = ParagraphStyle(
                name="SeccionHeader",
                parent=estilos['Heading2'],
                fontSize=12,
                textColor=COLOR_TEXTO,
                spaceBefore=10,
                spaceAfter=4
            )
            texto_style = ParagraphStyle(
                name="NormalPersonalizado",
                parent=estilos['Normal'],
                fontSize=11,  # Corregido: era fontsize en minúscula
                textColor=COLOR_TEXTO,
                spaceBefore=5,
                spaceAfter=5,
            )

            cell_style = ParagraphStyle(
                'CellText', parent=texto_style, fontSize=9, leading=11)
            cell_bold = ParagraphStyle(
                'CellBold', parent=cell_style, fontName='Helvetica-Bold')

            # --- 1. ENCABEZADO Y DATOS DE CONTACTO ---
            story.append(
                Paragraph("ECOTECH SOLUTIONS - CATÁLOGO COMERCIAL", titulo_style))
            story.append(Paragraph(
                """San Martín 955, Mendoza, Argentina | +54 2614526587 | info@ecotechsolutions.com | http://ecotechsolutions.com""", subtitulo_style))
            story.append(Spacer(1, 15))

            # Carpeta base donde guardas las fotos de los productos
            carpeta_imagenes = Path("ejercicio_2_productos")

            # Iterar sobre cada producto del catálogo JSON
            for item in catalogo_data:
                story.append(
                    Paragraph(f"Ficha Técnica: {item.get('Nombre', '')}", seccion_style))
                story.append(
                    Paragraph(f"Descripción: {item.get('Descripción', '')}", texto_style))
                story.append(Spacer(1, 6))

                # VINCULACIÓN DINÁMICA DE LA IMAGEN:
                # Buscamos la imagen usando el 'Código de Producto' (ej: PANEL001.jpg o PANEL001.png)
                codigo_producto = item.get('Código de Producto', 'default')

                # Intentamos buscar en jpg o png usando el código
                ruta_imagen = carpeta_imagenes / f"{codigo_producto}.jpg"
                if not ruta_imagen.exists():
                    ruta_imagen = carpeta_imagenes / f"{codigo_producto}.png"

                if ruta_imagen.exists():
                    img_producto = Image(
                        str(ruta_imagen), width=140, height=140)
                    img_producto.hAlign = 'CENTER'
                else:
                    img_producto = Paragraph(
                        "<font color='red'><b>[Imagen no<br/>disponible]</b></font>", cell_style)

                # Construir tabla de especificaciones (2 columnas reales: Clave y Valor)
                tabla_datos = [
                    [Paragraph("Código", cell_bold), Paragraph(
                        str(item.get('Código de Producto', '')), cell_style)],
                    [Paragraph("Fecha de Producción", cell_bold), Paragraph(
                        str(item.get('Fecha de Producción', '')), cell_style)],
                    [Paragraph("Fecha de Garantía", cell_bold), Paragraph(
                        str(item.get('Fecha de Garantía', '')), cell_style)],
                    [Paragraph("Degradación Anual Max.", cell_bold), Paragraph(
                        str(item.get('Degradación Anual Máxima', '')), cell_style)],
                    [Paragraph("Precio", cell_bold), Paragraph(
                        str(item.get('Precio de Venta', '')), cell_style)],
                    [Paragraph("Potencia Max. Salida", cell_bold), Paragraph(
                        str(item.get('Potencia Máxima de Salida', '')), cell_style)],
                    [Paragraph("Eficiencia Máxima", cell_bold), Paragraph(
                        str(item.get('Eficiencia Máxima', '')), cell_style)],
                    [Paragraph("Dimensiones Módulo", cell_bold), Paragraph(
                        str(item.get('Dimensiones del Módulo', '')), cell_style)],
                ]

                # Ajustamos el ancho para las 2 columnas de datos (Total: 370 puntos)
                t_especificaciones = Table(tabla_datos, colWidths=[130, 240])
                t_especificaciones.setStyle(TableStyle([
                    # Líneas visibles en toda la tabla
                    ('GRID', (0, 0), (-1, -1), 0.5, COLOR_GRID),
                    # Fondo gris claro a las etiquetas
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                ]))

                # ESTRUCTURA DE DISEÑO: [ TABLA A LA IZQUIERDA | IMAGEN A LA DERECHA ]
                # Ancho disponible en A4 restando márgenes es ~535. 370 (tabla) + 165 (imagen) = 535.
                tabla_layout = Table(
                    [[t_especificaciones, img_producto]], colWidths=[370, 165])
                tabla_layout.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Centra la imagen en su celda derecha
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))

                story.append(tabla_layout)
                # Espacio antes del siguiente producto
                story.append(Spacer(1, 15))

            # ÚNICA llamada a build al final de procesar todo el story
            doc.build(
                story,
                onFirstPage=self.dibujar_fondo,
                onLaterPages=self.dibujar_fondo
            )
            print(
                f"¡Reporte PDF generado exitosamente en: '{Path(ruta_pdf).resolve()}'!")

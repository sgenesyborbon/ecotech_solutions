from django.urls import path

from panel_sustentabilidad.views import (
    enviar_correo_reporte_view,
    exportar_pdf_view,
    vista_panel_sustentabilidad,
)

urlpatterns = [
    path('panel_sustentabilidad/', vista_panel_sustentabilidad, name='panel_sustentabilidad'),
    path('panel_sustentabilidad/exportar-pdf/', exportar_pdf_view, name='exportar_pdf'),
    path('panel/enviar-correo/', enviar_correo_reporte_view, name='enviar_correo_reporte'),
]
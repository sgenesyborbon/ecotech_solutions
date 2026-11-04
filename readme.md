# 🌿 EcoTech Solutions - Sistema Integral de Gestión y Auditoría Industrial

Sistema backend modular en Python y Django diseñado para la monitorización de sensores IoT industriales, gestión de inventario y stock de dispositivos ecológicos, y auditoría energética de emisiones de huella de carbono.

> **Proyecto Final Integrador** - Programación Full Stack (Python, Django, SQL, JSON)  
> **Integrantes:** Sofía Genesy
> **Profesor:** Diego Simonelli
> **Fecha de Entrega:** 2026

## Descripción del Proyecto

El proyecto unifica tres componentes clave para la eficiencia industrial e impacto ambiental:
1. **Módulo 1: Procesamiento de Sensores IoT Industrial y Reportes Térmicos en PDF** Ingesta, limpieza y normalización de lecturas térmicas crudas (`registro_impuro_raw.json`), análisis estadístico del comportamiento de la planta y generación automática de reportes ejecutivos en PDF.
2. **Módulo 2: Catálogo e Inventario de Dispositivos Ecológicos (Paneles Solares) con validaciones de StockInvalidoError y exportación JSON.** Modelado orientado a objetos para dispositivos fotovoltaicos (Paneles Solares), gestión de stock garantizando encapsulamiento estricto, persistencia en archivos JSON (`catalogo_ecotech.json`) y fichas técnicas comerciales.
3. **Módulo 3: Auditoría Energética de Maquinarias Industriales y Huella de Carbono en Django** Simulación y cálculo de emisiones globales de CO2 mediante cálculo de consumo industrial e integración con la plataforma web Django.


## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.11.9
- **Framework Web & ORM:** Django
- **Librerías Principales:** NumPy (análisis estadístico), ReportLab (generación de PDFs), Pytest (suite de pruebas unitarias).
- **Formato de Persistencia Local:** JSON / SQLite.


## 📁 Estructura del Repositorio

ecotech_solutions/
├── main.py                            # Script principal de ejecución e integración
├── ejercicio_1_sensores/              # Módulo de procesamiento de sensores
│   ├── sensores.py
│   └── reporte_sensores.py
├── ejercicio_2_productos/             # Módulo de inventario y dispositivos ecológicos
│   ├── dispositivos_ecologicos.py
|   |__ formula_precio.py              # Cálculo de costos y precio de venta
│   ├── paneles_solares.py
│   |── inventario.py
|   |__ reporte_inventario.py
|   |__ catalogo_ecotech.json          # Datos serializados del inventario
|   |__ ficha_tecnica_panel_solar.pdf  # Catálogo de ficha técnica en pdf sin stock
|   |__ registros_ecotech.json         # Registro de datos limpios con stock
├── ejercicio_3_auditoria_web/         # Módulo de calculadora industrial y huella CO2
│   ├── calculadora_consumo.py
│   └── auditoria_emisiones.py
|__ panel_sustentabilidad               # App de Django para interactuar con métricas
|__ script/
|   |__ script.py                       # Instanciación de clases y métodos para prueba
├── shared/ 
|   |__enums/
|   |  |__ enums.py                     # Enums para identificar descriptores                            
│   └── exceptions/
│   |  └── exception.py                 # Excepciones personalizadas y validadores
|   |__ validators/
|       |__ data_validator.py           # Validaciones para tipo de atributos
|       |__ datetime_validator.py       # Validaciones para atributos datetime
|       |__ file_validator.py           # Validaciones para tipo de atributos extraidos
├── tests/
|   |__ test_auditoria.py               # Pruebas unitarias automatizadas (pytest)
└── requirements.txt                    # Dependencias del proyecto

## Badges

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Django](https://img.shields.io/badge/Django-FullStack-green?style=flat&logo=django)
![Status](https://img.shields.io/badge/Estado-Completado-brightgreen)
![License](https://img.shields.io/badge/Licencia-MIT-yellow)

## Licencia

MIT License

Copyright (c) [2026] EcoTech Solutions - Sistema Integral de Gestión y Auditoría Industrial

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Web Móvil - Reportes SEMYL
Generador de Informes Técnicos de Mantenimiento (Planta Eléctrica y T.T.A.)
"""

import os
from flask import Flask, render_template_string, send_file, request

# ReportLab para la exportación exacta a PDF corporativo
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

app = Flask(__name__)

# Interfaz HTML móvil moderna con Bootstrap 5
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reportes SEMYL</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; }
        .card-header-semyl { background-color: #1F4E79; color: white; font-weight: bold; }
        .btn-semyl { background-color: #1F4E79; color: white; font-weight: bold; }
        .btn-semyl:hover { background-color: #16365C; color: white; }
    </style>
</head>
<body>
    <div class="container py-4">
        <div class="text-center mb-4">
            <h3 class="text-primary fw-bold">⚡ SERVICIOS ELECTROMECÁNICOS YL</h3>
        </div>

        <form action="/generar" method="POST">
            
            <!-- 1. DATOS GENERALES -->
            <div class="card shadow-sm mb-4">
                <div class="card-header card-header-semyl">📋 Datos Generales y del Equipo</div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6"><label class="form-label">Número de Reporte</label><input type="text" name="num_reporte" class="form-control" required></div>
                        <div class="col-md-6"><label class="form-label">Fecha</label><input type="text" name="fecha" class="form-control" required></div>
                        <div class="col-md-6"><label class="form-label">Cliente</label><input type="text" name="cliente" class="form-control" required></div>
                        <div class="col-md-6"><label class="form-label">Modelo P.E.</label><input type="text" name="modelo_pe" class="form-control"></div>
                        <div class="col-md-6"><label class="form-label">Ubicación</label><input type="text" name="ubicacion" class="form-control"></div>
                        <div class="col-md-6"><label class="form-label">Capacidad (kVA/kW)</label><input type="text" name="capacidad" class="form-control"></div>
                        <div class="col-md-6"><label class="form-label">Modelo Generador</label><input type="text" name="modelo_gen" class="form-control"></div>
                        <div class="col-md-6"><label class="form-label">Serie</label><input type="text" name="serie" class="form-control"></div>
                        <div class="col-12"><label class="form-label">Motor</label><input type="text" name="motor" class="form-control"></div>
                    </div>
                </div>
            </div>

            <!-- 2. PARÁMETROS DEL MOTOR -->
            <div class="card shadow-sm mb-4">
                <div class="card-header card-header-semyl">🔧 Parámetros Operativos del Motor</div>
                <div class="card-body">
                    {% set motor_items = [
                        "Nivel de refrigerante", "Nivel de Aceite", "Nivel de combustible",
                        "Temperatura de Refrigerante", "Presión de Aceite", "Voltaje de Alternador de carga",
                        "Voltaje de cargador de baterías", "Voltaje de baterías en reposo", "Caída de Voltaje en Arranque"
                    ] %}
                    {% for desc in motor_items %}
                    <div class="row g-2 mb-3 align-items-center border-bottom pb-2">
                        <div class="col-12 col-md-5 fw-semibold small text-secondary">{{ loop.index }}. {{ desc }}</div>
                        <div class="col-6 col-md-3"><input type="text" name="m_val_{{ loop.index }}" class="form-control form-control-sm" placeholder="Valor medido"></div>
                        <div class="col-6 col-md-4"><input type="text" name="m_obs_{{ loop.index }}" class="form-control form-control-sm" placeholder="Observaciones"></div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- 3. PARÁMETROS ELÉCTRICOS -->
            <div class="card shadow-sm mb-4">
                <div class="card-header card-header-semyl">⚡ Parámetros del Generador Eléctrico</div>
                <div class="card-body">
                    <h6 class="text-dark fw-bold">Voltaje de línea (Vac)</h6>
                    <div class="row g-2 mb-3">
                        <div class="col-4"><label class="small">L1-L2</label><input type="text" name="v_l1l2" class="form-control form-control-sm"></div>
                        <div class="col-4"><label class="small">L1-L3</label><input type="text" name="v_l1l3" class="form-control form-control-sm"></div>
                        <div class="col-4"><label class="small">L2-L3</label><input type="text" name="v_l2l3" class="form-control form-control-sm"></div>
                    </div>

                    <h6 class="text-dark fw-bold">Voltaje de fase (Vac)</h6>
                    <div class="row g-2 mb-3">
                        <div class="col-4"><label class="small">L1-N</label><input type="text" name="v_l1n" class="form-control form-control-sm"></div>
                        <div class="col-4"><label class="small">L2-N</label><input type="text" name="v_l2n" class="form-control form-control-sm"></div>
                        <div class="col-4"><label class="small">L3-N</label><input type="text" name="v_l3n" class="form-control form-control-sm"></div>
                    </div>

                    <h6 class="text-dark fw-bold">Corriente (A)</h6>
                    <div class="row g-2 mb-3">
                        <div class="col-4"><label class="small">L1</label><input type="text" name="c_l1" class="form-control form-control-sm"></div>
                        <div class="col-4"><label class="small">L2</label><input type="text" name="c_l2" class="form-control form-control-sm"></div>
                        <div class="col-4"><label class="small">L3</label><input type="text" name="c_l3" class="form-control form-control-sm"></div>
                    </div>

                    <h6 class="text-dark fw-bold">Frecuencia (Hz)</h6>
                    <div class="row g-2">
                        <div class="col-md-6"><input type="text" name="frecuencia" class="form-control form-control-sm" placeholder="Valor de frecuencia"></div>
                    </div>
                </div>
            </div>

            <!-- 4. OBSERVACIONES Y RECOMENDACIONES -->
            <div class="card shadow-sm mb-4">
                <div class="card-header card-header-semyl">📝 Observaciones y Recomendaciones</div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Observaciones Técnicas</label>
                        <textarea name="observaciones" class="form-control" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Recomendaciones</label>
                        <textarea name="recomendaciones" class="form-control" rows="3"></textarea>
                    </div>
                </div>
            </div>

            <!-- BOTÓN DE GENERAR -->
            <button type="submit" class="btn btn-semyl w-100 py-3 mb-5 shadow fs-5">Generar Reporte PDF</button>

        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    num_rep = request.form.get('num_reporte', '0000')
    fecha = request.form.get('fecha', '')
    cliente = request.form.get('cliente', '')
    modelo_pe = request.form.get('modelo_pe', '')
    ubicacion = request.form.get('ubicacion', '')
    capacidad = request.form.get('capacidad', '')
    modelo_gen = request.form.get('modelo_gen', '')
    serie = request.form.get('serie', '')
    motor = request.form.get('motor', '')

    obs_text = request.form.get('observaciones', '')
    rec_text = request.form.get('recomendaciones', '')

    filename = f"Reporte_Tecnico_{num_rep}.pdf"

    try:
        doc = SimpleDocTemplate(
            filename, pagesize=letter,
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )
        story = []
        styles = getSampleStyleSheet()

        style_title = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1F4E79'), alignment=TA_RIGHT)
        style_th = ParagraphStyle('THStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, alignment=TA_CENTER)
        style_th_left = ParagraphStyle('THLeftStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, alignment=TA_LEFT)
        style_td = ParagraphStyle('TDStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#333333'), alignment=TA_LEFT)
        style_td_center = ParagraphStyle('TDCenterStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#333333'), alignment=TA_CENTER)

        # 1. Cabecera (Logo + Títulos)
        logo_path = "logo_extracted.png"
        logo_flowable = Image(logo_path, width=150, height=45) if os.path.exists(logo_path) else Paragraph("<b>SEMYL</b>", styles['Normal'])

        header_text = Paragraph(
            "<b>SERVICIOS ELECTROMECÁNICOS YL</b><br/>"
            "INFORME TÉCNICO DE MANTENIMIENTO<br/>"
            "PLANTA ELÉCTRICA Y T.T.A.<br/>"
            f"<font color='#C00000'>Número de Reporte: {num_rep}</font>",
            style_title
        )

        head_table = Table([[logo_flowable, header_text]], colWidths=[200, 340])
        head_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        story.append(head_table)
        story.append(Spacer(1, 10))

        # 2. Datos del Cliente y Equipo
        meta_data = [
            [Paragraph("<b>FECHA:</b>", style_td), Paragraph(fecha, style_td), Paragraph("<b>MODELO P.E.:</b>", style_td), Paragraph(modelo_pe, style_td)],
            [Paragraph("<b>CLIENTE:</b>", style_td), Paragraph(cliente, style_td), Paragraph("<b>SERIE:</b>", style_td), Paragraph(serie, style_td)],
            [Paragraph("<b>UBICACIÓN:</b>", style_td), Paragraph(ubicacion, style_td), Paragraph("<b>CAPACIDAD (KVA/KW):</b>", style_td), Paragraph(capacidad, style_td)],
            [Paragraph("<b>MODELO GENERADOR:</b>", style_td), Paragraph(modelo_gen, style_td), Paragraph("<b>MOTOR:</b>", style_td), Paragraph(motor, style_td)],
        ]
        meta_table = Table(meta_data, colWidths=[115, 155, 115, 155])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F2F4F8')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1F4E79')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D3D3D3')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        def crear_banner_seccion(texto):
            t = Table([[Paragraph(f"<b>{texto}</b>", ParagraphStyle('B', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white))]], colWidths=[540])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1F4E79')),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            return t

        # 3. Parámetros del Motor
        story.append(crear_banner_seccion("1. PARÁMETROS OPERATIVOS Y NIVELES DEL MOTOR"))
        motor_table_data = [[Paragraph("ITEM", style_th), Paragraph("DESCRIPCIÓN DE PRUEBA / PARÁMETRO", style_th_left), Paragraph("VALOR MEDIDO", style_th), Paragraph("OBSERVACIONES", style_th_left)]]
        
        engine_items = [
            "Nivel de refrigerante", "Nivel de Aceite", "Nivel de combustible",
            "Temperatura de Refrigerante", "Presión de Aceite", "Voltaje de Alternador de carga",
            "Voltaje de cargador de baterías", "Voltaje de baterías en reposo", "Caída de Voltaje en Arranque"
        ]

        for idx, desc in enumerate(engine_items, 1):
            val_val = request.form.get(f'm_val_{idx}', '')
            obs_val = request.form.get(f'm_obs_{idx}', '')
            motor_table_data.append([
                Paragraph(str(idx), style_td_center),
                Paragraph(desc, style_td),
                Paragraph(val_val, style_td_center),
                Paragraph(obs_val, style_td)
            ])

        m_table = Table(motor_table_data, colWidths=[40, 260, 100, 140])
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E75B6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D3D3D3')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(m_table)
        story.append(Spacer(1, 10))

        # 4. Parámetros del Generador Eléctrico
        story.append(crear_banner_seccion("2. PARÁMETROS DEL GENERADOR ELÉCTRICO"))
        gen_table_data = [[Paragraph("ITEM", style_th), Paragraph("PARÁMETRO", style_th_left), Paragraph("FASE / LÍNEA", style_th), Paragraph("VALOR", style_th), Paragraph("FASE / LÍNEA", style_th), Paragraph("VALOR", style_th), Paragraph("FASE / LÍNEA", style_th), Paragraph("VALOR", style_th)]]

        rows_gen_info = [
            ("1", "Voltaje de línea (Vac)", [("L1 - L2", request.form.get('v_l1l2', '')), ("L1 - L3", request.form.get('v_l1l3', '')), ("L2 - L3", request.form.get('v_l2l3', ''))]),
            ("2", "Voltaje de fase (Vac)", [("L1 - N", request.form.get('v_l1n', '')), ("L2 - N", request.form.get('v_l2n', '')), ("L3 - N", request.form.get('v_l3n', ''))]),
            ("3", "Corriente (A)", [("L1", request.form.get('c_l1', '')), ("L2", request.form.get('c_l2', '')), ("L3", request.form.get('c_l3', ''))]),
            ("4", "Frecuencia (Hz)", [("Frecuencia", request.form.get('frecuencia', '')), ("", ""), ("", "")])
        ]

        for it, param, triplets in rows_gen_info:
            row_cells = [
                Paragraph(it, style_td_center),
                Paragraph(param, style_td),
                Paragraph(triplets[0][0], style_td_center), Paragraph(triplets[0][1], style_td_center),
                Paragraph(triplets[1][0], style_td_center), Paragraph(triplets[1][1], style_td_center),
                Paragraph(triplets[2][0], style_td_center), Paragraph(triplets[2][1], style_td_center),
            ]
            gen_table_data.append(row_cells)

        g_table = Table(gen_table_data, colWidths=[30, 150, 65, 65, 65, 65, 50, 50])
        g_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E75B6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D3D3D3')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(g_table)
        story.append(Spacer(1, 10))

        # 5. Observaciones y Recomendaciones (CORREGIDO: Sin rowHeights fijo)
        story.append(crear_banner_seccion("3. OBSERVACIONES TÉCNICAS Y RECOMENDACIONES"))
        obs_table_data = [
            [Paragraph("<b>OBSERVACIONES TÉCNICAS</b>", style_th_left), Paragraph("<b>RECOMENDACIONES</b>", style_th_left)],
            [Paragraph(obs_text or "(Sin observaciones)", style_td), Paragraph(rec_text or "(Sin recomendaciones)", style_td)]
        ]
        obs_table = Table(obs_table_data, colWidths=[270, 270])
        obs_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E75B6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D3D3D3')),
            ('VALIGN', (0,0), (-1,1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(obs_table)
        story.append(Spacer(1, 15))

        # 6. Firmas
        sig_data = [
            [
                Paragraph("_____________________________________<br/><b>Técnico Responsable YL</b><br/>Servicios Electromecánicos YL", ParagraphStyle('S1', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=TA_CENTER)),
                Paragraph("_____________________________________<br/><b>Conformidad del Cliente</b><br/>Nombre / Firma / Sello", ParagraphStyle('S2', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=TA_CENTER))
            ]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(KeepTogether(sig_table))

        doc.build(story)
        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Ocurrió un error al generar el PDF: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

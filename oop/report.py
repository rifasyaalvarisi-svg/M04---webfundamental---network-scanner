import json
from abc import ABC, abstractmethod
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class BaseReportExporter(ABC):
    def __init__(self, scanner, filename: str):
        self._data = scanner
        self._filename = filename

    @property
    def data(self):
        return self._data

    @property
    def filename(self) -> str:
        return self._filename

    @abstractmethod
    def export(self):
        pass


class PDFReportExporter(BaseReportExporter):
    def export(self):
        scanner = self.data

        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=12,
            alignment=1
        )
        normal_style = styles['Normal']

        story.append(Paragraph("Laporan Hasil Pemindaian Port (Port Scanner)", title_style))
        story.append(Spacer(1, 12))

        summary_data = [
            [Paragraph("<b>Target Host:</b>", normal_style), Paragraph(str(scanner.target_host), normal_style)],
            [Paragraph("<b>Target IP:</b>", normal_style), Paragraph(str(scanner.target_ip), normal_style)],
            [Paragraph("<b>Rentang Port:</b>", normal_style), Paragraph(f"{scanner.start_port} - {scanner.end_port}", normal_style)],
            [Paragraph("<b>Waktu Eksekusi:</b>", normal_style), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), normal_style)],
            [Paragraph("<b>Durasi Scan:</b>", normal_style), Paragraph(f"{scanner.scan_duration:.2f} detik", normal_style)],
        ]

        summary_table = Table(summary_data, colWidths=[120, 380])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('BOX', (0, 0), (-1, -1), colors.HexColor('#cbd5e0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>Daftar Port Terbuka</b>", styles['Heading2']))
        story.append(Spacer(1, 6))

        if scanner.open_ports:
            port_table_data = [["Port", "Status", "Layanan Umum (Estimasi)"]]
            for p in scanner.open_ports:
                if p in [80, 443]:
                    service = "HTTP/HTTPS"
                elif p == 22:
                    service = "SSH"
                elif p == 21:
                    service = "FTP"
                else:
                    service = "Lainnya/Custom"
                port_table_data.append([str(p), "TERBUKA", service])

            port_table = Table(port_table_data, colWidths=[100, 150, 250])
            port_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(port_table)
        else:
            story.append(Paragraph("Tidak ada port terbuka yang ditemukan pada rentang tersebut.", normal_style))

        doc.build(story)
        print(f"[+] Laporan PDF berhasil diekspor: {self.filename}")


class JSONReportExporter(BaseReportExporter):
    def export(self):
        scanner = self.data
        data = {
            "target_host": scanner.target_host,
            "target_ip": scanner.target_ip,
            "port_range": {
                "start": scanner.start_port,
                "end": scanner.end_port
            },
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scan_duration": round(scanner.scan_duration, 2),
            "total_open_ports": len(scanner.open_ports),
            "open_ports": [
                {
                    "port": p,
                    "status": "OPEN",
                    "estimated_service": (
                        "HTTP/HTTPS" if p in [80, 443]
                        else "SSH" if p == 22
                        else "FTP" if p == 21
                        else "Lainnya/Custom"
                    )
                }
                for p in scanner.open_ports
            ]
        }

        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[+] Laporan JSON berhasil diekspor: {self.filename}")
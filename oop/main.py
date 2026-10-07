import sys
from scanner import TCPPortScanner
from report import PDFReportExporter, JSONReportExporter


def safe_filename(target: str) -> str:
    return "".join(
        c if c.isalnum() or c in "-_." else "_"
        for c in target
    )


def main():
    print("=== APLIKASI PORT SCANNER & EXPORTER (OOP) ===")

    target = input("Masukkan IP atau Domain target (contoh: 127.0.0.1): ").strip()

    try:
        start_port = int(input("Masukkan port awal (contoh: 1): "))
        end_port = int(input("Masukkan port akhir (contoh: 1024): "))
    except ValueError:
        print("[!] Masukkan angka port yang valid.")
        sys.exit(1)

    scanner = TCPPortScanner(target, start_port, end_port, timeout=0.4)
    scanner.scan()

    safe_target = safe_filename(target)
    pdf_filename = f"scan_report_{safe_target}.pdf"
    json_filename = f"scan_report_{safe_target}.json"

    exporters = [
        PDFReportExporter(scanner, pdf_filename),
        JSONReportExporter(scanner, json_filename),
    ]

    for exporter in exporters:
        exporter.export()


if __name__ == "__main__":
    main()
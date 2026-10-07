import socket
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime


class BaseScanner(ABC):
    def __init__(self, target_host: str):
        self._target_host = target_host
        self._target_ip = self._resolve_host()
        self._scan_duration = 0.0

    @property
    def target_host(self) -> str:
        return self._target_host

    @property
    def target_ip(self) -> str:
        return self._target_ip

    @property
    def scan_duration(self) -> float:
        return self._scan_duration

    def _resolve_host(self) -> str:
        try:
            return socket.gethostbyname(self._target_host)
        except socket.gaierror:
            print("\n[!] Host tidak dapat diselesaikan. Periksa kembali nama/IP target.")
            sys.exit(1)

    @abstractmethod
    def scan(self):
        pass


class TCPPortScanner(BaseScanner):
    def __init__(self, target_host: str, start_port: int, end_port: int, timeout: float = 0.5):
        super().__init__(target_host)
        self._start_port = start_port
        self._end_port = end_port
        self._timeout = timeout
        self._open_ports = []

    @property
    def start_port(self) -> int:
        return self._start_port

    @property
    def end_port(self) -> int:
        return self._end_port

    @property
    def timeout(self) -> float:
        return self._timeout

    @property
    def open_ports(self) -> list:
        return self._open_ports

    def scan(self) -> list:
        self._open_ports = []
        start_time = time.time()

        print("_" * 50)
        print(f" Memindai Target IP : {self.target_ip}")
        print(f" Rentang Port       : {self.start_port} - {self.end_port}")
        print(f" Waktu Mulai        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("_" * 50)

        try:
            for port in range(self.start_port, self.end_port + 1):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target_ip, port))
                s.close()

                if result == 0:
                    print(f"[+] Port {port} : TERBUKA")
                    self._open_ports.append(port)

        except KeyboardInterrupt:
            print("\n[!] Pemindaian dibatalkan oleh pengguna (Ctrl+C).")

        finally:
            self._scan_duration = time.time() - start_time
            print("." * 50)
            print(f" Pemindaian Selesai. Total port terbuka ditemukan: {len(self._open_ports)}")
            print(f" Durasi Pemindaian: {self.scan_duration:.2f} detik")
            print("." * 50)

        return self._open_ports
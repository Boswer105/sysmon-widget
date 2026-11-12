"""
SysMon Widget - Widget de monitoring système flottant
Fichier unique tout-en-un pour démarrage rapide.
"""
import sys
import json
from pathlib import Path
import psutil
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor, QIcon, QAction


# ============================================================
# CONFIG - Sauvegarde de la position dans config.json local
# ============================================================
CONFIG_FILE = Path(__file__).parent / "config.json"

def load_position() -> tuple[int, int]:
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text())
            return data.get("x", 100), data.get("y", 100)
    except (json.JSONDecodeError, OSError):
        pass
    return 100, 100

def save_position(x: int, y: int) -> None:
    try:
        CONFIG_FILE.write_text(json.dumps({"x": x, "y": y}, indent=2))
    except OSError:
        pass


# ============================================================
# MONITOR - Collecte des métriques système
# ============================================================
class SystemMonitor:
    def __init__(self):
        psutil.cpu_percent(interval=None)  # Init pour éviter 0% au 1er appel

    def get_cpu(self) -> dict:
        freq = psutil.cpu_freq()
        return {
            "percent": psutil.cpu_percent(interval=None),
            "frequency_mhz": round(freq.current, 0) if freq else 0,
        }

    def get_ram(self) -> dict:
        mem = psutil.virtual_memory()
        gb = 1024 ** 3
        return {
            "used_gb": round(mem.used / gb, 1),
            "total_gb": round(mem.total / gb, 1),
            "percent": mem.percent,
        }

    def get_gpu(self) -> dict | None:
        """Retourne les infos du GPU NVIDIA, ou None si non détecté."""
        if not GPU_AVAILABLE:
            return None
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return None
            gpu = gpus[0]  # On prend le premier GPU
            return {
                "name": gpu.name,
                "percent": gpu.load * 100,  # GPUtil renvoie 0.0-1.0
                "temp": gpu.temperature,
                "mem_used_mb": round(gpu.memoryUsed),
                "mem_total_mb": round(gpu.memoryTotal),
            }
        except Exception:
            return None

    def get_network(self) -> dict:
        c = psutil.net_io_counters()
        return {"download_bytes": c.bytes_recv, "upload_bytes": c.bytes_sent}

    @staticmethod
    def format_rate(current: int, previous: int) -> str:
        diff = max(0, current - previous)
        if diff < 1024:
            return f"{diff} B/s"
        elif diff < 1024 ** 2:
            return f"{diff / 1024:.1f} Ko/s"
        elif diff < 1024 ** 3:
            return f"{diff / (1024 ** 2):.1f} Mo/s"
        else:
            return f"{diff / (1024 ** 3):.2f} Go/s"


# ============================================================
# WIDGET - Fenêtre flottante
# ============================================================
class SysMonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.monitor = SystemMonitor()
        self._drag_pos: QPoint | None = None
        self._prev_net = self.monitor.get_network()

        self._setup_window()
        self._setup_ui()
        self._setup_timer()

    def _setup_window(self) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Taille ajustée pour 4 lignes de métriques + titre
        self.setFixedSize(280, 240)
        x, y = load_position()
        self.move(x, y)

    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            QWidget#mainContainer {
                background-color: rgba(20, 20, 30, 180);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
            }
            QLabel {
                color: #E5E7EB;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 13px;
            }
            QLabel#title {
                font-size: 14px;
                font-weight: 600;
                color: #60A5FA;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        container = QWidget()
        container.setObjectName("mainContainer")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(14, 12, 14, 12)
        c_layout.setSpacing(6)

        title = QLabel("⚡ SysMon")
        title.setObjectName("title")
        c_layout.addWidget(title)

        self.cpu_label = QLabel()
        self.gpu_label = QLabel()
        self.ram_label = QLabel()
        self.net_label = QLabel()
        c_layout.addWidget(self.cpu_label)
        c_layout.addWidget(self.gpu_label)
        c_layout.addWidget(self.ram_label)
        c_layout.addWidget(self.net_label)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)

        layout.addWidget(container)

    def _setup_timer(self) -> None:
        self._update_metrics()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_metrics)
        self.timer.start(1000)

    def _update_metrics(self) -> None:
        cpu = self.monitor.get_cpu()
        ram = self.monitor.get_ram()
        net = self.monitor.get_network()
        gpu = self.monitor.get_gpu()

        self.cpu_label.setText(
            f"🧠 CPU  <span style='color:#34D399;font-weight:600'>"
            f"{cpu['percent']:5.1f}%</span>  ·  {cpu['frequency_mhz']:.0f} MHz"
        )

        # GPU : affichage conditionnel
        if gpu is None:
            self.gpu_label.setText("🎮 GPU  <span style='color:#9CA3AF'>Non détecté</span>")
        else:
            self.gpu_label.setText(
                f"🎮 GPU  <span style='color:#34D399;font-weight:600'>"
                f"{gpu['percent']:5.1f}%</span>  ·  "
                f"<span style='color:#FBBF24'>{gpu['temp']}°C</span>  ·  "
                f"{gpu['mem_used_mb']}/{gpu['mem_total_mb']} Mo"
            )

        self.ram_label.setText(
            f"💾 RAM  <span style='color:#34D399;font-weight:600'>"
            f"{ram['used_gb']}/{ram['total_gb']} Go</span>  ·  {ram['percent']}%"
        )

        dl = SystemMonitor.format_rate(net["download_bytes"], self._prev_net["download_bytes"])
        ul = SystemMonitor.format_rate(net["upload_bytes"], self._prev_net["upload_bytes"])
        self.net_label.setText(
            f"🌐 Net  <span style='color:#34D399;font-weight:600'>↓{dl}</span>"
            f"  ·  <span style='color:#F87171;font-weight:600'>↑{ul}</span>"
        )
        self._prev_net = net

    # Drag & Drop
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # Sauvegarde position à la fermeture
    def closeEvent(self, event):
        pos = self.pos()
        save_position(pos.x(), pos.y())
        super().closeEvent(event)


# ============================================================
# TRAY - Icône dans la zone de notification
# ============================================================
def create_tray(widget, app) -> QSystemTrayIcon:
    tray = QSystemTrayIcon(widget)
    tray.setToolTip("SysMon Widget")

    menu = QMenu()
    show_action = QAction("Afficher / Masquer", menu)
    quit_action = QAction("Quitter", menu)

    show_action.triggered.connect(lambda: widget.setVisible(not widget.isVisible()))
    quit_action.triggered.connect(app.quit)

    menu.addAction(show_action)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()
    return tray


# ============================================================
# MAIN
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = SysMonWidget()
    widget.show()

    tray = create_tray(widget, app)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
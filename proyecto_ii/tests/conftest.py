from pathlib import Path
import sys

# Localizar la carpeta src/
SRC_DIR = Path(__file__).resolve().parents[1] / "src"

# Añadir src/ a las rutas de búsqueda de Python
sys.path.insert(0, str(SRC_DIR))
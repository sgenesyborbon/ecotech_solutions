import sys
from pathlib import Path

# Agrega automáticamente la raíz del proyecto al path de pytest
raiz_proyecto = Path(__file__).resolve().parent
sys.path.insert(0, str(raiz_proyecto))

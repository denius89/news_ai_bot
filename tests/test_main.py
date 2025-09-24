"""
Интеграционные тесты для CLI (main.py).
"""

import subprocess
import sys
import pytest


@pytest.mark.integration
def test_main_etl_runs():
    """
    Проверка: main.py запускается без ошибок
    (при наличии переменных окружения).
    """
    result = subprocess.run(
        [sys.executable, "main.py", "--source", "crypto", "--limit", "1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
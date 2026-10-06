#!/usr/bin/env python3
"""
Скрипт для обновления всех конфигураций Cloudflare Tunnel.
"""

from config.core.cloudflare import get_deployment_info, validate_cloudflare_config, CLOUDFLARE_TUNNEL_URL
import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def update_vite_config():
    """Обновляет конфигурацию Vite."""
    print("🔄 Обновление конфигурации Vite...")

    # Запускаем генератор конфига
    import subprocess

    result = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "generate_vite_config.py")], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ Конфигурация Vite обновлена")
    else:
        print(f"❌ Ошибка обновления Vite: {result.stderr}")


def update_documentation():
    """Обновляет документацию с актуальными URL."""
    print("🔄 Обновление документации...")

    deployment_info = get_deployment_info()

    # Обновляем DEPLOYMENT_GUIDE.md
    deployment_guide_path = project_root / "DEPLOYMENT_GUIDE.md"
    if deployment_guide_path.exists():
        with open(deployment_guide_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Заменяем старые URL на новые
        old_url = "https://example.invalid"
        new_url = deployment_info["tunnel_url"]

        if old_url in content:
            content = content.replace(old_url, new_url)

            with open(deployment_guide_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ DEPLOYMENT_GUIDE.md обновлен")

    # Обновляем DEVELOPMENT_GUIDE.md
    dev_guide_path = project_root / "DEVELOPMENT_GUIDE.md"
    if dev_guide_path.exists():
        with open(dev_guide_path, "r", encoding="utf-8") as f:
            content = f.read()

        old_url = "https://example.invalid"
        new_url = deployment_info["tunnel_url"]

        if old_url in content:
            content = content.replace(old_url, new_url)

            with open(dev_guide_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ DEVELOPMENT_GUIDE.md обновлен")


def show_current_config():
    """Показывает текущую конфигурацию."""
    print("\n📋 Текущая конфигурация Cloudflare:")
    print("=" * 50)

    deployment_info = get_deployment_info()

    for key, value in deployment_info.items():
        print(f"{key:20}: {value}")

    print("\n🔍 Валидация конфигурации:")
    if validate_cloudflare_config():
        print("✅ Конфигурация корректна")
    else:
        print("❌ Конфигурация содержит ошибки")


def main():
    """Основная функция."""
    print("🚀 Обновление конфигураций Cloudflare Tunnel")
    print("=" * 50)

    # Показываем текущую конфигурацию
    show_current_config()

    # Обновляем конфигурации
    update_vite_config()
    update_documentation()

    print("\n🎉 Все конфигурации обновлены!")
    print(f"🌐 Новый URL: {CLOUDFLARE_TUNNEL_URL}")


if __name__ == "__main__":
    main()

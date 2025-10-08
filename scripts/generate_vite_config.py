#!/usr/bin/env python3
"""
Генератор конфигурации Vite из Python конфига Cloudflare.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.cloudflare import get_vite_allowed_hosts


def generate_vite_config():
    """Генерирует конфигурацию Vite с актуальными хостами."""

    allowed_hosts = get_vite_allowed_hosts()

    # Формируем строку с хостами
    hosts_str = ",\n          ".join([f"'{host}'" for host in allowed_hosts])

    vite_config = f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'
import {{ resolve }} from 'path'
import {{ fileURLToPath, URL }} from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(({{ command, mode }}) => {{
  const isProduction = mode === 'production' || command === 'build'
  
  return {{
    plugins: [react()],
    base: '/webapp',
    resolve: {{
      alias: {{
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      }},
    }},
    // Конфигурация только для development
    ...(command === 'serve' && {{
      server: {{
        port: 3000,
        host: true,
        allowedHosts: [
          {hosts_str}
        ],
        headers: {{
          'Cross-Origin-Embedder-Policy': 'unsafe-none',
          'Cross-Origin-Opener-Policy': 'unsafe-none',
          'Cross-Origin-Resource-Policy': 'cross-origin',
        }},
        // Proxy для API в dev режиме
        proxy: {{
          '/api': {{
            target: 'http://localhost:8001',
            changeOrigin: true,
            secure: false,
          }},
          '/webapp': {{
            target: 'http://localhost:8001',
            changeOrigin: true,
            secure: false,
          }},
        }},
      }},
    }}),
    // Конфигурация для production
    ...(isProduction && {{
      build: {{
        outDir: 'dist',
        assetsDir: 'assets',
        sourcemap: false,
        rollupOptions: {{
          input: {{
            main: resolve(__dirname, 'index.html'),
          }},
        }},
      }},
    }}),
  }}
}})
"""

    return vite_config


if __name__ == "__main__":
    config_content = generate_vite_config()

    # Записываем в файл
    vite_config_path = project_root / "webapp" / "vite.config.ts"

    with open(vite_config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    print(f"✅ Конфигурация Vite обновлена: {vite_config_path}")
    print(f"📋 Разрешенные хосты: {get_vite_allowed_hosts()}")

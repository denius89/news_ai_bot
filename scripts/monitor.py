#!/usr/bin/env python3
"""
Система мониторинга сервисов PulseAI.

Отслеживает состояние всех сервисов и предупреждает о проблемах.
"""

import time
import requests
import psutil
import os
from pathlib import Path
from typing import Dict, List

class ServiceMonitor:
    """Мониторинг сервисов."""
    
    def __init__(self):
        self.services = {
            'flask': {
                'name': 'Flask WebApp',
                'port': 8001,
                'path': '/webapp',
                'pid_file': '.flask.pid'
            },
            'bot': {
                'name': 'Telegram Bot',
                'pid_file': '.bot.pid'
            }
        }
    
    def check_flask(self) -> Dict:
        """Проверяет состояние Flask."""
        service = self.services['flask']
        result = {
            'name': service['name'],
            'status': 'unknown',
            'details': {}
        }
        
        try:
            # Проверяем HTTP доступность
            response = requests.get(f"http://localhost:{service['port']}{service['path']}", 
                                  timeout=5)
            if response.status_code == 200:
                result['status'] = 'healthy'
                result['details']['http_status'] = response.status_code
                result['details']['response_time'] = response.elapsed.total_seconds()
            else:
                result['status'] = 'unhealthy'
                result['details']['http_status'] = response.status_code
        except requests.exceptions.RequestException as e:
            result['status'] = 'unreachable'
            result['details']['error'] = str(e)
        
        # Проверяем процесс
        pid_file = Path(service['pid_file'])
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                if psutil.pid_exists(pid):
                    result['details']['pid'] = pid
                    result['details']['process_exists'] = True
                else:
                    result['status'] = 'dead'
                    result['details']['process_exists'] = False
            except (ValueError, FileNotFoundError):
                result['status'] = 'no_pid_file'
        
        return result
    
    def check_bot(self) -> Dict:
        """Проверяет состояние Telegram Bot."""
        service = self.services['bot']
        result = {
            'name': service['name'],
            'status': 'unknown',
            'details': {}
        }
        
        # Проверяем процесс
        pid_file = Path(service['pid_file'])
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                if psutil.pid_exists(pid):
                    result['status'] = 'healthy'
                    result['details']['pid'] = pid
                    result['details']['process_exists'] = True
                    
                    # Проверяем логи на ошибки
                    log_file = Path('logs/bot.log')
                    if log_file.exists():
                        last_lines = log_file.read_text().split('\n')[-10:]
                        error_lines = [line for line in last_lines if 'ERROR' in line]
                        if error_lines:
                            result['status'] = 'warning'
                            result['details']['recent_errors'] = len(error_lines)
                else:
                    result['status'] = 'dead'
                    result['details']['process_exists'] = False
            except (ValueError, FileNotFoundError):
                result['status'] = 'no_pid_file'
        else:
            result['status'] = 'not_started'
        
        return result
    
    def check_all_services(self) -> List[Dict]:
        """Проверяет все сервисы."""
        return [
            self.check_flask(),
            self.check_bot()
        ]
    
    def print_status(self):
        """Выводит статус всех сервисов."""
        print("📊 СТАТУС СЕРВИСОВ")
        print("=" * 30)
        
        services = self.check_all_services()
        
        for service in services:
            status_icon = {
                'healthy': '✅',
                'warning': '⚠️',
                'unhealthy': '❌',
                'unreachable': '🔌',
                'dead': '💀',
                'not_started': '⏹️',
                'no_pid_file': '📄',
                'unknown': '❓'
            }.get(service['status'], '❓')
            
            print(f"{status_icon} {service['name']}: {service['status']}")
            
            for key, value in service['details'].items():
                print(f"   {key}: {value}")
        
        print()
    
    def monitor_loop(self, interval: int = 30):
        """Запускает мониторинг в цикле."""
        print(f"🔄 Запуск мониторинга (интервал: {interval}с)")
        print("Нажмите Ctrl+C для остановки")
        
        try:
            while True:
                self.print_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Мониторинг остановлен")

def main():
    """Основная функция."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Мониторинг сервисов PulseAI')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Интервал проверки в секундах (по умолчанию: 30)')
    parser.add_argument('--once', action='store_true',
                       help='Выполнить проверку один раз')
    
    args = parser.parse_args()
    
    monitor = ServiceMonitor()
    
    if args.once:
        monitor.print_status()
    else:
        monitor.monitor_loop(args.interval)

if __name__ == "__main__":
    main()

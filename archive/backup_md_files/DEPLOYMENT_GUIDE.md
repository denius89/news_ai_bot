# 🚀 PulseAI Deployment Guide

## **Production Ready Architecture**

### **Архитектура:**
```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

---

## 📋 **Быстрый Старт**

### **1. Запуск локально:**
```bash
make start
```

### **2. Проверка:**
- React App: http://localhost:8001/webapp
- API: http://localhost:8001/api/health

---

## 🌐 **Production Deploy**

### **1. Обновить URL в настройках:**
```python
# config/settings.py
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.invalid")
```

### **2. Запустить Cloudflare Tunnel:**
```bash
cloudflared tunnel --url http://localhost:8001
```

### **3. Обновить URL в настройках:**
Заменить `postcards-simple-investigators-negotiation.trycloudflare.com` на реальный URL туннеля

### **4. Перезапустить сервисы:**
```bash
make restart
```

---

## 🤖 **Telegram Bot**

### **Команды:**
- `/start` - главное меню
- `/dashboard` - открыть WebApp
- `/help` - справка

### **WebApp кнопка:**
Автоматически использует `WEBAPP_URL` из настроек

---

## 🔧 **Управление**

### **Основные команды:**
```bash
make start     # Запустить все
make stop      # Остановить все
make build     # Собрать React
make logs      # Показать логи
make restart   # Перезапустить
```

### **Индивидуальные сервисы:**
```bash
make flask     # Flask + React
make bot       # Telegram Bot
```

---

## 📊 **Мониторинг**

### **Проверка статуса:**
```bash
make check-ports
```

### **Логи:**
```bash
tail -f logs/flask.log
tail -f logs/bot.log
```

---

## ✅ **Проверка работы**

### **1. React App:**
- Открыть `/webapp`
- Проверить загрузку интерфейса
- Тестировать навигацию

### **2. API:**
- `/api/health` - статус
- `/api/latest` - новости
- `/api/categories` - категории

### **3. Telegram Bot:**
- Отправить `/start`
- Нажать "🌐 WebApp"
- Проверить открытие Dashboard

---

## 🎯 **Готово!**

Система работает как единое целое:
- **Flask** обслуживает React статику и API
- **Telegram Bot** интегрирован с WebApp
- **Cloudflare Tunnel** обеспечивает доступ

**Все готово для production!** 🚀

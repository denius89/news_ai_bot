# 🛡️ Admin Backup API Documentation

**Создано:** 27 октября 2025
**Статус:** Production Ready
**Автор:** PulseAI Team

---

## 📋 Overview

**Backup API для админ панели** позволяет управлять бэкапами базы данных через веб-интерфейс.

**Возможности:**
- ✅ Создание backup из админ-панели
- ✅ Просмотр списка всех backup
- ✅ Удаление старых backup
- ✅ Конфигурация backup (для масштабирования)
- ✅ Интеграция с облачным storage (S3, Google Cloud, Azure)

---

## 🔌 API Endpoints

### **1. GET `/admin/api/backup/list`**

Получить список всех backup файлов.

**Требует:** Admin авторизация

**Response:**
```json
{
  "status": "success",
  "backups": [
    {
      "filename": "pulseai_20251027_143022.sql.gz",
      "size_mb": 2.5,
      "size_bytes": 2621440,
      "created_at": "2025-10-27T14:30:22",
      "path": "/home/user/news_ai_bot/backups/pulseai_20251027_143022.sql.gz"
    }
  ],
  "count": 5,
  "total_size_mb": 12.5
}
```

---

### **2. POST `/admin/api/backup/create`**

Создать backup базы данных.

**Требует:** Admin авторизация

**Request:**
```json
{
  "scheduled": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Backup started in background",
  "backup_in_progress": true
}
```

**Note:** Backup запускается в фоновом потоке, не блокирует API.

---

### **3. GET `/admin/api/backup/status`**

Получить статус последнего backup.

**Требует:** Admin авторизация

**Response:**
```json
{
  "status": "success",
  "has_backup": true,
  "last_backup": {
    "filename": "pulseai_20251027_143022.sql.gz",
    "size_mb": 2.5,
    "created_at": "2025-10-27T14:30:22"
  },
  "total_backups": 5,
  "backup_dir": "/home/user/news_ai_bot/backups"
}
```

---

### **4. DELETE `/admin/api/backup/delete/<filename>`**

Удалить конкретный backup файл.

**Требует:** Admin авторизация

**Пример:**
```
DELETE /admin/api/backup/delete/pulseai_20251027_143022.sql.gz
```

**Response:**
```json
{
  "status": "success",
  "message": "Backup pulseai_20251027_143022.sql.gz deleted"
}
```

**Security:** Защита от path traversal (`..`, `/`)

---

### **5. GET `/admin/api/backup/config`**

Получить конфигурацию backup (для масштабирования).

**Требует:** Admin авторизация

**Response:**
```json
{
  "status": "success",
  "config": {
    "backup_enabled": true,
    "keep_days": 30,
    "schedule": "0 3 * * *",
    "max_size_mb": 1000,
    "auto_cleanup": true
  },
  "scalability_options": {
    "cloud_storage": ["s3", "google_cloud", "azure"],
    "compression": ["gzip", "bzip2", "xz"],
    "encryption": ["aes256", "gpg"],
    "multi_region": false
  }
}
```

---

### **6. PUT `/admin/api/backup/config`**

Обновить конфигурацию backup.

**Требует:** Admin авторизация

**Request:**
```json
{
  "keep_days": 30,
  "backup_enabled": true,
  "schedule": "0 3 * * *",
  "max_size_mb": 1000
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Backup configuration updated",
  "config": {...},
  "note": "Restart required to apply changes"
}
```

---

## 🎯 Usage Examples

### **Example 1: Создать Backup**

```bash
curl -X POST https://your-domain.com/admin/api/backup/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scheduled": false}'
```

### **Example 2: Получить список Backup**

```bash
curl -X GET https://your-domain.com/admin/api/backup/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Example 3: Удалить Backup**

```bash
curl -X DELETE https://your-domain.com/admin/api/backup/delete/pulseai_20251027_143022.sql.gz \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📈 Scalability Features

### **Cloud Storage Integration**

Поддержка интеграции с облачными хранилищами:

**S3:**
```json
{
  "cloud_storage": "s3",
  "bucket": "pulseai-backups",
  "region": "us-east-1"
}
```

**Google Cloud Storage:**
```json
{
  "cloud_storage": "google_cloud",
  "bucket": "pulseai-backups",
  "project": "your-project"
}
```

**Azure Blob Storage:**
```json
{
  "cloud_storage": "azure",
  "container": "pulseai-backups",
  "account": "your-account"
}
```

### **Encryption**

Поддержка шифрования backup:

**AES256:**
```json
{
  "encryption": "aes256",
  "encryption_key": "YOUR_KEY"
}
```

**GPG:**
```json
{
  "encryption": "gpg",
  "gpg_key_id": "YOUR_GPG_KEY_ID"
}
```

### **Compression Options**

Разные алгоритмы сжатия:

- `gzip` - быстрый (по умолчанию)
- `bzip2` - лучшее сжатие
- `xz` - максимальное сжатие

---

## 🔧 Integration with Frontend

### **React Component Example**

```typescript
// BackupManagement.tsx
import { useState, useEffect } from 'react';

export const BackupManagement = () => {
  const [backups, setBackups] = useState([]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchBackups();
  }, []);

  const fetchBackups = async () => {
    const response = await fetch('/admin/api/backup/list', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setBackups(data.backups);
  };

  const createBackup = async () => {
    setCreating(true);
    await fetch('/admin/api/backup/create', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    setTimeout(fetchBackups, 5000); // Refresh after 5s
    setCreating(false);
  };

  return (
    <div>
      <button onClick={createBackup} disabled={creating}>
        {creating ? 'Creating...' : 'Create Backup'}
      </button>
      <table>
        {backups.map(backup => (
          <tr key={backup.filename}>
            <td>{backup.filename}</td>
            <td>{backup.size_mb} MB</td>
            <td>{backup.created_at}</td>
          </tr>
        ))}
      </table>
    </div>
  );
};
```

---

## 🛡️ Security

### **Admin Authorization**

Все endpoints требуют admin авторизации:

```python
@require_admin
def create_backup():
    ...
```

### **Path Traversal Protection**

Защита от path traversal атак:

```python
# Security: prevent path traversal
if ".." in filename or "/" in filename:
    return jsonify({"status": "error", "message": "Invalid filename"}), 400
```

### **Timeout Protection**

Backup скрипт ограничен по времени:

```python
timeout=300  # 5 minutes max
```

---

## 📊 Monitoring

### **Backup Status**

Отслеживайте статус backup через API:

```bash
# Check backup status
curl https://your-domain.com/admin/api/backup/status
```

### **Logs**

Логи backup доступны в `logs/backup.log`:

```bash
tail -f logs/backup.log
```

---

## 🔄 Cron Integration

### **Automated Backups**

Добавить в crontab:

```bash
# Daily backup at 3 AM
0 3 * * * cd /path/to/project && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

### **Multiple Backups per Day**

```bash
# Every 6 hours
0 */6 * * * cd /path/to/project && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

---

## 📖 References

- Backup Script: `scripts/backup_db.sh`
- Restore Script: `scripts/restore_db.sh`
- Full Guide: `docs/BACKUP_GUIDE.md`
- Admin Routes: `routes/admin_routes.py`

---

**Дата:** 27 октября 2025
**Версия:** 1.0
**Статус:** Production Ready

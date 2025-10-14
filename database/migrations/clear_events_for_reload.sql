-- Очистка таблицы events_new для перезагрузки со всеми улучшениями
-- Дата: 14 октября 2025

-- Удаляем все события
TRUNCATE TABLE events_new;

-- Сбрасываем sequence для ID (если есть)
-- ALTER SEQUENCE events_new_id_seq RESTART WITH 1;

-- Готово! Таблица очищена и готова к загрузке свежих событий


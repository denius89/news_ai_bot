-- Удаление тестовых данных "Sample News Article"
-- Дата: 13 октября 2025

-- Удаляем все новости с паттерном "Sample News Article"
DELETE FROM news 
WHERE title LIKE 'Sample News Article%';

-- Проверяем сколько записей удалено
-- (Этот комментарий останется в логах)

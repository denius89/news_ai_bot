-- Тестовые данные для news
insert into news (title, content, source, published_at)
values 
('Bitcoin растёт', 'Цена BTC превысила $65,000', 'coindesk', now()),
('Ethereum обновляет уровень', 'ETH закрепился выше $3,500', 'investing.com', now());

-- Тестовый пользователь
insert into users (telegram_id)
values ('123456789');

-- Тестовый дайджест для пользователя
insert into digests (user_id, summary)
select id, 'Утренний дайджест: Bitcoin растёт, Ethereum тоже в плюсе'
from users
where telegram_id = '123456789';

-- Тестовые уведомления для пользователя
insert into user_notifications (user_id, title, text, read)
select 
  (SELECT id FROM users WHERE telegram_id = '123456789'),
  'Новый дайджест готов!',
  'Ваш утренний дайджест с последними новостями готов к прочтению.',
  false
union all
select 
  (SELECT id FROM users WHERE telegram_id = '123456789'),
  'Важное событие',
  'Сегодня в 15:00 ожидается важное экономическое событие в США.',
  true;

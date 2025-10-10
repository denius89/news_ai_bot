import { useAuth } from '../context/AuthContext';

/**
 * Централизованная функция для API запросов с автоматической аутентификацией
 */
export const apiRequest = async (url: string, options: RequestInit = {}) => {
  // Получаем заголовки аутентификации из контекста
  // Примечание: в реальном использовании нужно будет передавать authHeaders
  // через параметры или использовать другой подход, так как hooks нельзя вызывать
  // вне React компонентов
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  if (response.status === 401) {
    // Ошибка аутентификации - нужно обновить токены
    throw new Error('Authentication required');
  }
  
  return response;
};

/**
 * Хук для API запросов с автоматической аутентификацией
 */
export const useApiRequest = () => {
  const { authHeaders, refreshAuth } = useAuth();

  const request = async (url: string, options: RequestInit = {}) => {
    let response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...options.headers
      }
    });
    
    // Если получили 401, пробуем обновить аутентификацию
    if (response.status === 401) {
      try {
        await refreshAuth();
        // Повторяем запрос с обновленными заголовками
        response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders,
            ...options.headers
          }
        });
      } catch (refreshError) {
        console.error('Failed to refresh auth:', refreshError);
        throw new Error('Authentication failed');
      }
    }
    
    return response;
  };

  return { request };
};

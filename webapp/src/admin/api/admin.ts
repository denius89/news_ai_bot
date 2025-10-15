/**
 * API client для Admin Panel
 */

import type {
  AdminStats,
  AIMetrics,
  UserMetrics,
  LogsResponse,
  LogFile,
  AdminConfig,
  AdminInfo
} from '../types/admin';

const API_BASE = '/admin/api';

/**
 * Обработка ответа от API
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

/**
 * Получить информацию о текущем админе
 */
export async function getAdminInfo(): Promise<AdminInfo> {
  const response = await fetch(`${API_BASE}/me`);
  return handleResponse<AdminInfo>(response);
}

/**
 * Получить общую статистику
 */
export async function getAdminStats(): Promise<AdminStats> {
  const response = await fetch(`${API_BASE}/stats`);
  return handleResponse<AdminStats>(response);
}

/**
 * Получить AI метрики
 */
export async function getAIMetrics(days: number = 7): Promise<AIMetrics> {
  const response = await fetch(`${API_BASE}/metrics/ai?days=${days}`);
  return handleResponse<AIMetrics>(response);
}

/**
 * Получить метрики пользователей
 */
export async function getUserMetrics(): Promise<UserMetrics> {
  const response = await fetch(`${API_BASE}/metrics/users`);
  return handleResponse<UserMetrics>(response);
}

/**
 * Получить логи
 */
export async function getLogs(file: string = 'app.log', lines: number = 100): Promise<LogsResponse> {
  const response = await fetch(`${API_BASE}/logs/tail?file=${file}&lines=${lines}`);
  return handleResponse<LogsResponse>(response);
}

/**
 * Получить список лог-файлов
 */
export async function getLogFiles(): Promise<{ files: LogFile[] }> {
  const response = await fetch(`${API_BASE}/logs/files`);
  return handleResponse<{ files: LogFile[] }>(response);
}

/**
 * Получить конфигурацию
 */
export async function getConfig(): Promise<AdminConfig> {
  const response = await fetch(`${API_BASE}/config`);
  return handleResponse<AdminConfig>(response);
}

/**
 * Обновить конфигурацию
 */
export async function updateConfig(config: Partial<AdminConfig>): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE}/config`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(config),
  });
  return handleResponse<{ status: string; message: string }>(response);
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse<{ status: string; timestamp: string }>(response);
}



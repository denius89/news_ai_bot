/**
 * Custom hooks for event actions: export to calendar and share
 */

import { useState } from 'react';

interface Event {
  id: string;
  title: string;
  description: string;
  starts_at?: string;
  date?: string;
  time?: string;
  ends_at?: string;
  location?: string;
  link?: string;
  category: string;
  source?: string;
}

/**
 * Hook for exporting events to calendar (.ics file)
 */
export const useCalendarExport = () => {
  const formatDateForICS = (dateString: string): string => {
    // Remove all dashes, colons, and keep only digits
    // Format: YYYYMMDDTHHmmssZ
    return dateString.replace(/[-:]/g, '').split('.')[0] + 'Z';
  };

  const exportEvent = (event: Event) => {
    try {
      // Combine date and time if separate
      const startDateTime = event.starts_at || `${event.date}T${event.time || '00:00'}:00.000Z`;
      const endDateTime = event.ends_at || startDateTime;

      // Generate ICS content
      const icsContent = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//PulseAI//Events//RU',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        `UID:event-${event.id}@pulseai.com`,
        `DTSTAMP:${formatDateForICS(new Date().toISOString())}`,
        `DTSTART:${formatDateForICS(startDateTime)}`,
        `DTEND:${formatDateForICS(endDateTime)}`,
        `SUMMARY:${event.title}`,
        `DESCRIPTION:${event.description.replace(/\n/g, '\\n').replace(/,/g, '\\,')}`,
        `LOCATION:${event.location || 'Online'}`,
        `URL:${event.link || window.location.href}`,
        `CATEGORIES:${event.category}`,
        `STATUS:CONFIRMED`,
        `TRANSP:OPAQUE`,
        'END:VEVENT',
        'END:VCALENDAR'
      ].join('\r\n');

      // Create blob and download
      const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Clean title for filename
      const cleanTitle = event.title.replace(/[^a-zа-яё0-9]/gi, '-').slice(0, 30);
      link.download = `pulseai-event-${event.id}-${cleanTitle}.ics`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Failed to export event to calendar:', error);
      return false;
    }
  };

  return { exportEvent };
};

/**
 * Hook for sharing events via Web Share API or clipboard
 */
export const useShareEvent = () => {
  const [notification, setNotification] = useState<string | null>(null);
  const [isSharing, setIsSharing] = useState(false);

  const shareEvent = async (event: Event): Promise<boolean> => {
    setIsSharing(true);
    
    try {
      // Format date and time
      const startDateTime = event.starts_at || `${event.date}T${event.time || '00:00'}:00`;
      const formattedDate = new Date(startDateTime).toLocaleString('ru', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      // Prepare share data
      const shareData = {
        title: `📅 ${event.title}`,
        text: `${event.description}\n\n` +
          `📍 ${event.location || 'Online'}\n` +
          `🕒 ${formattedDate}\n` +
          `📊 Источник: ${event.source || 'PulseAI'}`,
        url: event.link || window.location.href
      };

      // Try Web Share API first (mobile devices)
      if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
        await navigator.share(shareData);
        setNotification('✓ Событие успешно отправлено');
        setTimeout(() => setNotification(null), 3000);
        return true;
      } else {
        // Fallback: copy to clipboard
        const textToCopy = `${shareData.title}\n\n${shareData.text}\n\n${shareData.url}`;
        await navigator.clipboard.writeText(textToCopy);
        setNotification('✓ Ссылка скопирована в буфер обмена');
        setTimeout(() => setNotification(null), 3000);
        return true;
      }
    } catch (error) {
      console.error('Failed to share event:', error);
      setNotification('✗ Не удалось поделиться событием');
      setTimeout(() => setNotification(null), 3000);
      return false;
    } finally {
      setIsSharing(false);
    }
  };

  const clearNotification = () => setNotification(null);

  return { shareEvent, notification, isSharing, clearNotification };
};

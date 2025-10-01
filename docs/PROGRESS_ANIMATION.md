# Progress Animation for AI Digest Generation

## Overview

The progress animation system provides visual feedback during AI digest generation in the Telegram bot. It creates an engaging user experience by showing animated progress steps and a visual progress bar.

## Features

### 🎬 Animated Progress Steps
- **🧠 Анализируем новости...** - Analyzing news content
- **📊 Считаем важность и достоверность...** - Calculating importance and credibility
- **✨ Формируем резюме...** - Forming summary
- **🔗 Проверяем источники...** - Checking sources
- **📝 Завершаем дайджест...** - Finalizing digest

### 📊 Visual Progress Bar
- Real-time progress indicator: `▰▰▰▰▱▱▱▱▱▱ 40%`
- 10-segment visual bar with filled (▰) and empty (▱) segments
- Percentage display for precise progress tracking

### ⚡ Immediate Feedback
- Instant response to user actions
- No waiting time for initial feedback
- Smooth transitions between progress steps

## Architecture

### Core Components

#### `ProgressAnimation` Class
```python
class ProgressAnimation:
    def __init__(self, callback_query: types.CallbackQuery)
    async def show_generation_progress(self, steps, progress_bar=True, interval=1.5)
    def stop(self)
    def _build_progress_text(self, step, current, total, show_bar)
    def _generate_progress_bar(self, current, total)
```

#### Convenience Functions
```python
async def show_generation_progress(callback_query, steps=None, progress_bar=True, interval=1.5)
async def show_quick_progress(callback_query, message, duration=2.0)
def build_digest_actions_keyboard(username, category=None)
```

## Usage

### Basic Implementation

```python
from utils.progress_animation import show_generation_progress

@router.callback_query(F.data.startswith("digest_ai_style:"))
async def cb_digest_ai_style(query: types.CallbackQuery):
    # Show immediate feedback
    await show_quick_progress(query, "⏳ Генерация дайджеста для тебя...")
    
    # Start animated progress
    animation = await show_generation_progress(query)
    
    # Generate digest in background
    service = DigestAIService()
    text = await asyncio.to_thread(service.generate_digest, ...)
    
    # Stop animation and show result
    animation.stop()
    await query.message.edit_text(text, reply_markup=actions_kb)
```

### Custom Progress Steps

```python
custom_steps = [
    "🔍 Поиск релевантных новостей...",
    "🧮 Анализ трендов...",
    "🤖 Генерация AI-резюме...",
    "✅ Финализация..."
]

animation = await show_generation_progress(query, steps=custom_steps)
```

### Progress Bar Control

```python
# With progress bar (default)
animation = await show_generation_progress(query, progress_bar=True)

# Without progress bar
animation = await show_generation_progress(query, progress_bar=False)

# Custom interval (default: 1.5 seconds)
animation = await show_generation_progress(query, interval=2.0)
```

## Action Buttons

### Digest Actions Keyboard

After digest generation, users see action buttons:

- **📋 Подписаться на тему** - Subscribe to category (if category selected)
- **🔔 Включить авто-дайджест** - Enable auto-digest notifications
- **⬅️ Назад** - Return to main menu

### Handler Implementation

```python
@router.callback_query(F.data.startswith("subscribe_category:"))
async def cb_subscribe_category(query: types.CallbackQuery):
    category = query.data.split(":", 1)[1]
    await query.answer(f"✅ Подписка на {category} активирована!", show_alert=True)

@router.callback_query(F.data == "enable_auto_digest")
async def cb_enable_auto_digest(query: types.CallbackQuery):
    await query.answer("✅ Авто-дайджест включен!", show_alert=True)
```

## Error Handling

### Telegram API Errors
- **Message not modified**: Gracefully handled, animation continues
- **Message too old**: Falls back to sending new message
- **Network errors**: Logged and handled without crashing

### Animation Control
- **Early termination**: `animation.stop()` can interrupt progress
- **Exception safety**: All errors are caught and logged
- **Resource cleanup**: Animation state is properly managed

## Testing

### Unit Tests
- Progress bar generation accuracy
- Animation state management
- Error handling scenarios
- Keyboard building functionality

### Integration Tests
- Full animation cycle
- Telegram API interaction mocking
- Concurrent animation handling

### Demo Script
```bash
python demo_progress_animation.py
```

## Configuration

### Default Settings
- **Interval**: 1.5 seconds between steps
- **Progress bar**: 10 segments
- **Steps**: 5 predefined steps
- **Characters**: ▰ (filled), ▱ (empty)

### Customization
All parameters can be customized per use case:
- Step messages
- Animation speed
- Progress bar appearance
- Error handling behavior

## Performance Considerations

### Async Implementation
- Non-blocking animation updates
- Background task management
- Efficient message editing

### Resource Management
- Proper cleanup of animation tasks
- Memory-efficient progress tracking
- Minimal API calls to Telegram

### User Experience
- Immediate visual feedback
- Smooth transitions
- Clear progress indication
- Engaging visual elements

## Future Enhancements

### Planned Features
- **Custom emoji sets** for different digest types
- **Sound notifications** for completion
- **Progress persistence** across bot restarts
- **A/B testing** for different animation styles

### Integration Opportunities
- **Web dashboard** progress visualization
- **Mobile app** synchronized progress
- **Analytics** tracking user engagement
- **Accessibility** improvements for screen readers

## Troubleshooting

### Common Issues

#### Animation Not Starting
- Check callback query validity
- Verify message editing permissions
- Ensure proper async context

#### Progress Bar Not Updating
- Verify `progress_bar=True` parameter
- Check step count and interval settings
- Monitor Telegram API rate limits

#### Message Edit Failures
- Handle "message not modified" errors
- Implement fallback to new messages
- Check message age and permissions

### Debug Mode
Enable detailed logging for animation debugging:
```python
import logging
logging.getLogger("utils.progress_animation").setLevel(logging.DEBUG)
```

## Related Documentation

- [Telegram Bot Handlers](TELEGRAM_HANDLERS.md)
- [AI Digest Service](AI_DIGEST_SERVICE.md)
- [User Interface Design](UI_DESIGN.md)
- [Error Handling Guide](ERROR_HANDLING.md)

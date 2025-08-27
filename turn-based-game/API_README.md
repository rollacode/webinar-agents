# 🎮 Turn-Based Game API Documentation

Документация по игровым API endpoints для пошаговой игры с агентами, кнопками и мостами.

## 📋 Содержание

- [Движение персонажа](#движение-персонажа)
- [Переключение агентов](#переключение-агентов) 
- [Использование кнопок](#использование-кнопок)
- [Использование компьютера](#использование-компьютера)
- [Сброс позиции](#сброс-позиции)
- [Server-Sent Events](#server-sent-events)
- [Игровая логика](#игровая-логика)

---

## 🚶 Движение персонажа

### POST `/api/character/multi-move`

Перемещает активного агента в указанном направлении на заданное количество шагов.

#### Параметры запроса
```json
{
  "direction": "right|left|up|down",
  "steps": 1-10,
  "agentIndex": 0  // Опционально, по умолчанию 0
}
```

#### Пример запроса
```bash
curl -X POST http://localhost:3000/api/character/multi-move \
  -H "Content-Type: application/json" \
  -d '{
    "direction": "right",
    "steps": 3,
    "agentIndex": 0
  }'
```

#### Пример успешного ответа
```json
{
  "success": true,
  "steps": [
    {
      "result": true,
      "available_actions": ["use_pc", "use_button"],
      "position": { "x": 3, "y": 2 },
      "level_completed": false
    }
  ],
  "final_position": { "x": 3, "y": 2 },
  "level_completed": false
}
```

#### Пример ошибки
```json
{
  "success": false,
  "error": "Invalid request. Need direction and steps (1-10)"
}
```

### GET `/api/character/multi-move`

Получает текущее состояние всех агентов.

#### Пример ответа
```json
{
  "success": true,
  "data": {
    "agents": [
      { "x": 2, "y": 7 },
      { "x": 16, "y": 3 }
    ],
    "activeAgent": 0,
    "agentCount": 2,
    "position": { "x": 2, "y": 7 },
    "available_actions": ["use_button"]
  }
}
```

---

## 🔄 Переключение агентов

### POST `/api/character/switch-agent`

Переключается между агентами (только для уровней с несколькими агентами).

#### Параметры запроса
```json
{
  "agentIndex": 0  // Индекс агента (0, 1, ...)
}
```

#### Пример запроса
```bash
curl -X POST http://localhost:3000/api/character/switch-agent \
  -H "Content-Type: application/json" \
  -d '{ "agentIndex": 1 }'
```

#### Пример ответа
```json
{
  "success": true,
  "data": {
    "message": "Switched to agent 1",
    "activeAgent": 1,
    "position": { "x": 16, "y": 3 },
    "agentCount": 2,
    "allAgents": [
      { "x": 2, "y": 7 },
      { "x": 16, "y": 3 }
    ]
  }
}
```

---

## 🔘 Использование кнопок

### POST `/api/character/use-button`

Активирует кнопку (B), если агент стоит рядом с ней. Опускает все мосты (Z → T).

#### Параметры запроса
Нет параметров - использует позицию активного агента.

#### Пример запроса
```bash
curl -X POST http://localhost:3000/api/character/use-button \
  -H "Content-Type: application/json"
```

#### Пример успешного ответа
```json
{
  "success": true,
  "data": {
    "message": "Button pressed! Bridges activated!",
    "bridgesActivated": true,
    "position": { "x": 6, "y": 3 }
  }
}
```

#### Пример ошибки
```json
{
  "success": false,
  "error": "No button nearby"
}
```

---

## 💻 Использование компьютера

### POST `/api/character/use-pc`

Использует компьютер (C) для завершения уровня.

#### Параметры запроса
Нет параметров - использует позицию активного агента.

#### Пример запроса
```bash
curl -X POST http://localhost:3000/api/character/use-pc \
  -H "Content-Type: application/json"
```

#### Пример успешного ответа
```json
{
  "success": true,
  "data": {
    "message": "Computer accessed successfully!",
    "level_completed": true,
    "position": { "x": 1, "y": 3 },
    "victory": true
  }
}
```

#### Пример ошибки
```json
{
  "success": false,
  "error": "No computer nearby"
}
```

### GET `/api/character/use-pc`

Получает информацию об endpoint'е.

---

## 🔄 Сброс позиции

### POST `/api/character/reset`

Сбрасывает всех агентов на стартовые позиции уровня.

#### Параметры запроса
Нет параметров.

#### Пример запроса
```bash
curl -X POST http://localhost:3000/api/character/reset \
  -H "Content-Type: application/json"
```

#### Пример ответа
```json
{
  "success": true,
  "data": {
    "message": "Character reset to starting position",
    "position": { "x": 2, "y": 7 },
    "currentLevel": "Level 3"
  }
}
```

---

## 📡 Server-Sent Events

### GET `/api/character/events`

Подключение к Server-Sent Events для получения обновлений в реальном времени.

#### Пример подключения
```javascript
const eventSource = new EventSource('/api/character/events');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Position update:', data);
};
```

#### Пример события
```json
{
  "type": "position_update",
  "agents": [
    { "x": 2, "y": 7 },
    { "x": 16, "y": 3 }
  ],
  "activeAgent": 0,
  "agentCount": 2,
  "position": { "x": 2, "y": 7 },
  "bridgesActivated": false
}
```

---

## 🎯 Игровая логика

### Тайлы карты
- **`#`** - Ground (стена) - непроходимо
- **`|`** - Ladder (лестница) - проходимо
- **`C`** - Computer (компьютер) - цель уровня
- **`B`** - Button (кнопка) - активирует мосты
- **`Z`** - Bridge Up (поднятый мост) - непроходимо
- **`T`** - Bridge Down (опущенный мост) - проходимо
- **`░`** - Empty (пустота) - проходимо

### Правила движения
1. Агент может двигаться на тайлы: `|`, `C`, `T`, `░`
2. Агент **не может** двигаться на тайлы: `#`, `Z` (если мосты не активированы)
3. После нажатия кнопки `B` все мосты `Z` становятся проходимыми `T`

### Правила действий
- **Кнопка (B)**: можно использовать, стоя рядом (соседняя клетка)
- **Компьютер (C)**: можно использовать, стоя на нем или рядом
- **Переключение агентов**: доступно только на уровнях с `starting_position_2`

### Коды состояния
- **200** - Успешная операция
- **400** - Неверные параметры запроса
- **500** - Внутренняя ошибка сервера

---

## 🛠️ Примеры использования

### Полный игровой цикл
```bash
# 1. Получить текущее состояние
curl http://localhost:3000/api/character/multi-move

# 2. Переместиться к кнопке
curl -X POST http://localhost:3000/api/character/multi-move \
  -H "Content-Type: application/json" \
  -d '{"direction": "right", "steps": 4}'

# 3. Нажать кнопку (активировать мосты)
curl -X POST http://localhost:3000/api/character/use-button

# 4. Переключиться на второго агента
curl -X POST http://localhost:3000/api/character/switch-agent \
  -H "Content-Type: application/json" \
  -d '{"agentIndex": 1}'

# 5. Дойти до компьютера и завершить уровень
curl -X POST http://localhost:3000/api/character/use-pc
```

### Обработка ошибок
```javascript
async function moveCharacter(direction, steps) {
  try {
    const response = await fetch('/api/character/multi-move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ direction, steps })
    });
    
    const result = await response.json();
    
    if (!result.success) {
      console.error('Movement failed:', result.error);
      return;
    }
    
    console.log('Movement successful:', result.final_position);
  } catch (error) {
    console.error('Network error:', error);
  }
}
```

---

## 🚀 Быстрый старт

1. **Запустите сервер**: `npm run dev`
2. **Откройте игру**: `http://localhost:3000`
3. **Тестируйте API**: используйте примеры выше или Postman

---

*Игра поддерживает до 2 агентов одновременно и включает механику кнопок/мостов для кооперативного решения головоломок.* 
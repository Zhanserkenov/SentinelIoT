# Инструкция по тестированию API в Postman

## Базовый URL
```
http://127.0.0.1:8000
```

## 1. Регистрация пользователя

**POST** `/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "testpassword123"
}
```

**Ожидаемый ответ:**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

---

## 2. Вход и получение токена

**POST** `/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "testpassword123"
}
```

**Ожидаемый ответ:**
```json
{
  "message": "User logged in",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**⚠️ ВАЖНО:** Скопируйте `access_token` из ответа - он понадобится для следующих запросов!

---

## 3. Анализ потоков (POST)

**POST** `/flows/analyze-window`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <ваш_access_token>
```

**Body (JSON):** Массив объектов flow features
```json
[
  {
    "src_mac": "00:11:22:33:44:55",
    "ack_flag_number": 10.5,
    "HTTPS": 1.0,
    "Rate": 100.0,
    "Header_Length": 20.0,
    "Variance": 5.2,
    "Max": 150.0,
    "Tot_sum": 1000.0,
    "Time_To_Live": 64.0,
    "Std": 2.5,
    "psh_flag_number": 5.0,
    "Min": 50.0,
    "DNS": 0.0
  },
  {
    "src_mac": "00:11:22:33:44:55",
    "ack_flag_number": 12.0,
    "HTTPS": 1.0,
    "Rate": 120.0,
    "Header_Length": 22.0,
    "Variance": 6.0,
    "Max": 160.0,
    "Tot_sum": 1200.0,
    "Time_To_Live": 64.0,
    "Std": 3.0,
    "psh_flag_number": 6.0,
    "Min": 60.0,
    "DNS": 0.0
  },
  {
    "src_mac": "AA:BB:CC:DD:EE:FF",
    "ack_flag_number": 8.0,
    "HTTPS": 0.0,
    "Rate": 80.0,
    "Header_Length": 18.0,
    "Variance": 4.0,
    "Max": 120.0,
    "Tot_sum": 800.0,
    "Time_To_Live": 64.0,
    "Std": 2.0,
    "psh_flag_number": 3.0,
    "Min": 40.0,
    "DNS": 1.0
  }
]
```

**Ожидаемый ответ:**
```json
{
  "sources": {
    "00:11:22:33:44:55": {
      "src_mac": "00:11:22:33:44:55",
      "flow_count": 2,
      "max_probability": 0.75,
      "alert_flows": 1,
      "status": "anomaly"
    },
    "AA:BB:CC:DD:EE:FF": {
      "src_mac": "AA:BB:CC:DD:EE:FF",
      "flow_count": 1,
      "max_probability": 0.35,
      "alert_flows": 0,
      "status": "normal"
    }
  },
  "summary": {
    "total_flows": 3,
    "total_sources": 2,
    "anomalous_sources": 1,
    "suspicious_sources": 0
  }
}
```

---

## 4. Получение результатов (GET)

**GET** `/flows/results`

**Headers:**
```
Authorization: Bearer <ваш_access_token>
```

**Ожидаемый ответ:**
```json
{
  "sources": {
    "00:11:22:33:44:55": {
      "src_mac": "00:11:22:33:44:55",
      "flow_count": 2,
      "max_probability": 0.75,
      "alert_flows": 1,
      "status": "anomaly"
    },
    "AA:BB:CC:DD:EE:FF": {
      "src_mac": "AA:BB:CC:DD:EE:FF",
      "flow_count": 1,
      "max_probability": 0.35,
      "alert_flows": 0,
      "status": "normal"
    }
  },
  "summary": {
    "total_flows": 3,
    "total_sources": 2,
    "anomalous_sources": 1,
    "suspicious_sources": 0
  }
}
```

**Если результатов нет:**
```json
{
  "sources": {},
  "summary": {
    "total_flows": 0,
    "total_sources": 0,
    "anomalous_sources": 0,
    "suspicious_sources": 0
  }
}
```

---

## Быстрая настройка в Postman

### Создание переменной для токена:

1. В Postman создайте новую коллекцию или откройте существующую
2. Перейдите в **Variables** (Переменные)
3. Создайте переменную:
   - **Variable:** `token`
   - **Initial Value:** (оставьте пустым)
   - **Current Value:** (оставьте пустым)

4. После успешного логина, в тестах (Tests) для `/auth/login` добавьте:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.collectionVariables.set("token", jsonData.access_token);
    console.log("Token saved:", jsonData.access_token);
}
```

5. В запросах `/flows/analyze-window` и `/flows/results` используйте в Authorization:
```
Bearer {{token}}
```

---

## Возможные ошибки

### 401 Unauthorized
- Проверьте, что токен правильный и не истек
- Убедитесь, что используете формат: `Bearer <token>`

### 422 Validation Error
- Убедитесь, что отправляете массив объектов (начинается с `[`)
- Проверьте, что все обязательные поля заполнены (`src_mac` и все числовые поля)
- Проверьте типы данных (числа должны быть числами, не строками)
- Убедитесь, что `src_mac` - это строка

### 500 Internal Server Error
- Проверьте, что модель загружена правильно
- Проверьте логи сервера



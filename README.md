### О проекте
«Фудграм» — это веб-сервис, в котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

Основные функции сервиса:
-   *Создание и редактирование рецептов*
-   *Подписки*: возможность подписываться на других пользователей.
-   *Избранное*: возможность добавлять рецепты в "Избранное", чтобы не потерять.
-   *Список покупок*: возможность создавать список продуктов (доступен для скачивания), которые нужно купить для приготовления выбранных блюд.
-   *Теги*: каждый рецепт обозначен тегами.

### Технологии:
- Python
- Django
- Django REST
- Docker

### Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/lukawoy/foodgram.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Заменить словарь DATABASES в файле settings.py на:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Заменить список ALLOWED_HOSTS в файле settings.py на:

```
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

# **Примеры запросов к API**

*Создание рецепта*(POST /api/recipes/)
- Authorization: Token <ваш_токен_доступа> 
- Content-Type: application/json
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
- Accept: application/json

Status 201:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
Status 400:
```
{
  "field_name": [
    "Обязательное поле."
  ]
}
```
Status 401:
```
Пользователь не авторизован
```
Status 404:
```
{
  "detail": "Страница не найдена."
}
```


*Получение тега*(GET /api/tags/{id}/)
- Accept: application/json
Status 200:
```
{
  "id": 0,
  "name": "Завтрак",
  "slug": "breakfast"
}
```
Status 404:
```
{
  "detail": "Страница не найдена."
}
```
## Над проектом работал студент Яндекс Практикум, когорта №83 - Лукин Дмитрий.

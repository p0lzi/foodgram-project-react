![foodgram workflow](https://github.com/p0lzi/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# Проект «FoodGram»

# URL дипломного проекта foodgram stend-p0lzi2.ddns.net


### Краткое описание проекта

Учебный проект социальной сети. Пользователи могут публиковать рецепты,
просматривать чужие рецепты, подписываться на авторов и добавлять их рецепты 
в избранное или в список покупок.

### **Стек**

![python version](https://img.shields.io/badge/Python-3.7-green)
![django version](https://img.shields.io/badge/Django-2.2-green)
![djangorestframework version](https://img.shields.io/badge/DRF-3.12-green)


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/p0lzi/foodgram-project-react.git
```

Перейти в папку infra
```
cd /infra
```

Запустить docker-compose

```
docker-compose up
```

Выполнить миграции

```
docker-compose exec web python manage.py migrate       
```

Создать суперпользователя

```
docker-compose exec web python manage.py createsuperuser   
```    

Собрать статику

``` 
docker-compose exec web python manage.py collectstatic --no-input 
```   


Загрузить данные в БД

``` 
docker-compose exec web python manage.py import
```  

### Документация к API доступна по адресу

**api/docs/**


### Примеры использования

Пример POST-запроса. Регистрация нового пользователя

```
POST /api/v1/users/

Request samples

{
    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "password": "string"
}
```

Пример POST-запроса. Получение токена.

```
POST /api/auth/token/

Request samples

{
  "email": "string",
  "password": "string"
}
```

Пример POST-запроса. Добавление нового рецепта

```
POST /api/recipes/

Request samples

{
    "ingredients": [
        {
            "id": number,
            "amount": number
        }
       ],
    "tags": [
        number,
    ],
    "image": "string(type<base64>)",
    "name": "string",
    "text": "string",
    "cooking_time": number
}
```

Пример GET-запроса. Получить информацию о рецепте.
```
GET /api/v1/recipes/{recipe_id}/
```


Пример GET-запроса. Получить список всех тегов.
```
GET /api/tags/
```

Пример GET-запроса. Получить список всех ингредиентов.
```
GET /api/ingredients/
```


### Импорт тестовых данных

Для проверки работы проекта можно наполнить проект тестовыми данными, для этого
можно ввести команду

```
python manage.py import
```

Данная команда импортирует данные по:

- ингредиенты;
- теги;

___

## Команда

- [Павел Зияев](https://github.com/p0lzi)
- [Яндекс Практикум](https://github.com/yandex-praktikum/)

___ 


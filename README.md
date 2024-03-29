# Collection_of_recipes

### Описание

Проект Collection_of_recipes это площадка для размещения рецептов блюд,
в которой есть удобный функционал подписки на автора,
добавления блюд в избранное и список покупок,
а так же есть возможность скачать весь необходимый список продуктов, всего в один клик.

Полная документация к API находится по эндпоинту /api/docs/

Адрес IP для проверки проекта - 158.160.42.239

## Stack

Python 3.8, Django 3.2, Docker-Compose

### Установка, Как запустить проект:

Клонируйте репозиторий:

```
git clone git@github.com:Alex386386/foodgram-project-react.git
```

Перейдите в склонированый репозиторий и внутри него перейдите в папку infra/

```
cd infra/
```

в этой папке выполните следующие команды:

```
sudo docker compose up -d
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic --no-input
sudo docker compose exec backend python manage.py load_all_data
sudo docker compose exec backend python manage.py createsuperuser
```

Теперь вам стал доступен сервис foodgram по адресу:

```
http://<IP_вашего_сервера>/
```

### Примеры работы с API для всех пользователей

Подробная документация доступна по эндпоинту 

```
http://<IP_вашего_сервера>/api/docs/
```

Для неавторизованных пользователей работа с API доступна в режиме чтения, что-либо изменить или создать не получится.

Список примеров запросов, доступных для неавторизованных пользователей:

```
Права доступа: Доступно без токена.
GET /api/users/{user_id}/ - Получение информации о юзере
GET /api/tags/ - Получение списка тэгов
GET /api/tags/{tag_id} - Получение тэга
GET /api/ingredients/ - Получение списка всех ингредиентов
GET /api/ingredients/{ingredient_id} - Получение ингредиента
GET /api/recipes/ - Получение списка всех рецептов
GET /api/recipes/{recipe_id}/ - Получение информации о рецепте
```

Примеры запросов для авторизованного пользователя, можно посмотреть в документации.

Автор:

- [Александр Мамонов](https://github.com/Alex386386) 

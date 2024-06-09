### Инструкция по запуску проекта:
1. `git clone https://github.com/vers4ch/TestTaskItsolutions.git`
2. `cd TestTaskItsolutions`
3. `sudo docker-compose build`
4. `docker-compose up -d`

### Инструкция по использованию API:
__!! Порт: 8000__

#### 1. Регистрация пользователя:

Метод: __POST__\
URL: __'/register'__\
Тело запроса (JSON):\
`` {
    "username": "your_username",
    "password": "your_password"
} ``

Ответ (JSON):\
`` { 
    "id": 1,
    "username": "your_username"
} ``



#### 2. Получение токена доступа:

Метод: __POST__\
URL: __'/token'__\
Тело запроса (форма):\
``username=your_username&password=your_password``

Ответ (JSON):\
``{
    "access_token": "your_access_token",
    "token_type": "bearer"
}``



#### 3. Получение объявления по ID:

Метод: __GET__\
URL: __'/ads/{ad_id}'__\
Заголовок авторизации:\
``` Authorization: Bearer <your_access_token>```

Ответ (JSON):\
``{
	"id": 0,
    "title": "Ad Title",
    "ad_id": 1,
    "author": "Ad Author",
    "views": 1111,
    "position": 1
}``


#### 4. Получение информации о пользователе
Метод: __GET__\
URL: __'/users/me'__\
Заголовок авторизации:\
``` Authorization: Bearer <your_access_token>```

Ответ (JSON):\
``{
	"username": "username"
}``

### __Ограничения:__
__Токен доступа действует в течение 30 минут.
Если токен доступа истек, необходимо выполнить процедуру авторизации заново.__

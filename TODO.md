## Модели приложения

| Сущность        | Модель          |
| --------------- | --------------- |
| Пользователь    | UserModel       |
| Материал здания | MaterialModel   |
| Тип помещения   | TargetModel     |
| Кафедра         | DepartmentModel |
| Здание          | BuildingModel   |
| Помещение       | HallModel       |
| Ответственный   | ChiefModel      |
| Имущество       | UnitModel       |

## API приложения (исправить)

| HTTP    | Ресурс                  | Класс и метод               | Роль в доступе | Описание                           |
| ------- | ----------------------- | --------------------------- | -------------- | ---------------------------------- |
| GET     | Коллекция зданий        | BuildingListResource.get    | user           | Получает все здания
| POST    | Коллекция зданий        | BuildingListResource.post   | user           | Создает новое здание
| GET     | Здание                  | BuildingResource.get        | user           | Получает одно здание
| PATCH   | Здание                  | BuildingResource.patch      | user           | Обновляет одно здание
| DELETE  | Здание                  | BuildingResource.delete     | user           | Удаляет одно здание
| GET     | Коллекция кафедр        | DepartmentListResource.get  | user           | Получает все кафедры
| POST    | Коллекция кафедр        | DepartmentListResource.post | user           | Создает новую кафедру
| GET     | Кафедра                 | DepartmentResource.get      | user           | Получает одно кафедру
| PATCH   | Кафедра                 | DepartmentResource.patch    | user           | Обновляет одно кафедру
| DELETE  | Кафедра                 | DepartmentResource.delete   | user           | Удаляет одно кафедру
| GET     | Коллекция помещений     | HallListResource.get        | user           | Получает все помещения
| POST    | Коллекция помещений     | HallListResource.post       | user           | Создает новое помещение
| GET     | Помещение               | HallResource.get            | user           | Получает одно помещение
| PATCH   | Помещение               | HallResource.patch          | user           | Обновляет одно помещение
| DELETE  | Помещение               | HallResource.delete         | user           | Удаляет одно помещение
| GET     | Коллекция имущества     | UnitListResource.get        | user           | Получает все имущество
| POST    | Коллекция имущества     | UnitListResource.post       | user           | Создает новое имущество
| GET     | Имущество               | UnitResource.get            | user           | Получает одно имущество
| PATCH   | Имущество               | UnitResource.patch          | user           | Обновляет одно имущество
| DELETE  | Имущество               | UnitResource.delete         | user           | Удаляет одно имущество
| GET     | Коллекция ответственных | ChiefListResource.get       | user           | Получает всех ответственных
| POST    | Коллекция ответственных | ChiefListResource.post      | user           | Создает нового ответственного
| GET     | Ответственный           | ChiefResource.get           | user           | Получает одного ответственного
| PATCH   | Ответственный           | ChiefResource.patch         | user           | Обновляет одного ответственного
| DELETE  | Ответственный           | ChiefResource.delete        | user           | Удаляет одного ответственного
| GET     | Коллекция материалов    | MaterialListResource.get    | user           | Получает все материалы
| POST    | Коллекция материалов    | MaterialListResource.post   | user           | Создает новый материал
| DELETE  | Материал здания         | MaterialResource.delete     | user           | Удаляет материал
| GET     | Коллекция типов помещ.  | TargetListResource.get      | user           | Получает все типы помещений
| POST    | Коллекция типов помещ.  | TargetListResource.post     | user           | Создает новый тип помещения
| DELETE  | Типы помещений          | TargetResource.delete       | user           | Удаляет тип помещения
| GET     | Коллекция пользователей | UserListResource.get        | admin          | Получает всех сохраненных пользователей
| POST    | Коллекция пользователей | UserListResource.post       | admin          | Создает нового пользователя
| GET     | Пользователь            | UserResource.get            | admin          | Получает существующего пользователя
| PATCH   | Пользователь            | UserResource.patch          | admin          | Обновляет одного пользователя
| DELETE  | Пользователь            | UserResource.delete         | admin          | Удаляет одного пользователя


### Задачи практики

[x] Объединить Flask-RESTful и самописную ОРМ
[x] Заменить самописную ОРМ на SQLAlchemy (пришлось объединить этот пункт и нижележащий из-за проблем интеграции)
[x] Объединить все компоненты с marshmallow
[ ] Упростить (автоматическая интеграция Flask-marshmallow и marshmallow-sqlalchemy)
[ ] Сделать веб-морду. Можно ли сделать как отдельный сервис ?
    То есть RESTful-сервис отвечает за обработку ресурсов и выдачу json.
    Web-сервис отвечает за отрисовку (шаблоны). За данными переадресуется к RESTful.
    Можно подключить как API или как микросервис.


### Ошибки кода, проблемы реализации и TODO

- [x] Нужно ограничение уникальности без учета регистра символов. Однако collation='NOCASE' не работает с UTF-8.
      Решение видится таким - создать гибридный метод, который проверяет требуемое имя в нижнем регистре
      с заданным словом в нижнем регистре. Собрать записи (filter), которые соотвествуют заданному слову.
      Решение: все оказалось проще с применением `sqlalchemy.sql.func.lower()`
- [x] При возврате ошибок вместо кода ошибки приходит ее описание.
      Все правильно: code - это текстовое описание, а status_code - это код ошибки.
      Код ошибки приходит в заголовке и не включен в json.
- [x] Заменить самописный HTTP status на HTTPStatus из библиотеки http
- [x] SQLAlchemySchema - не работает сериализация auto_field для NUMERIC -> Decimal
      (работает только как явное указание поля как fields.Float)
- [x] Не работает представление relationship с auto_load (выводит просто id)
      (также замена на конкретное поле - fields.Nested или fields.Pluck)
- [x] !!! Не добавляет любые поля, если они уникальные (без регистра) - замена метода `all()` -> `first()`
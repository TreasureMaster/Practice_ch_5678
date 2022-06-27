-- Заполнить таблицы данными

-- Материал здания
INSERT INTO public.materials ("Material")
VALUES
('Кирпич'),
('Дерево'),
('Железобетон'),
('Пеноблок');

-- Здания
INSERT INTO public.buildings
("BuildingName", "Land", "Address", "Year", "Wear", "Flow", "Picture", "Comment", "MaterialID")
VALUES
('Административное', 4000, 'ул.Никифорова, 2А', 1982, 50, 5, null, null, 1),
('Корпус 1', 3000, 'ул.Луговая, 59', 1985, 20, 3, null, null, 3),
('Корпус 2', 3200, 'ул.Пограничная, 6', 1986, 30, 3, null, null, 3);

-- Назначение помещения
INSERT INTO public.targets ("Target")
VALUES
('аудитория'),
('лаборатория'),
('вычислительный центр'),
('деканат');

-- Кафедра
INSERT INTO public.departments
("DepartmentName", "Boss", "Phone", "OfficeDean")
VALUES
('Философия', 'Ячин Сергей Евгеньевич', 842322652424, 'Гуманитарные науки'),
('Социальные науки', 'Кузина Ирина Геннадьевна', 842322652424, 'Гуманитарные науки'),
('Психология', 'Батурина Оксана Сергеевна', 842322652424, 'Гуманитарные науки'),
('История и археология', 'Пахомов Олег Станиславович', 842322652424, 'Гуманитарные науки');

-- Помещения
INSERT INTO public.halls
("HallNumber", "HallSquare", "Windows", "Heaters", "TargetID", "DepartmentID", "KadastrID")
VALUES
(101, 48, 5, 5, 1, 1, 2),
(202, 44, 4, 4, 1, 2, 2),
(122, 32, 3, 3, 2, 3, 3),
(308, 46, 4, 4, 4, 4, 3);

-- Здания
INSERT INTO public.chiefs
("Chief", "AddressChief", "Experience")
VALUES
('Иванов', 'ул.Никифорова, 56', 2),
('Петров', 'ул.Луговая, 22', 3),
('Кошкин', 'ул.Пограничная, 9', 3);

-- Имущество
INSERT INTO public.units
("UnitName", "DateStart", "Cost", "CostYear", "CostAfter", "Period", "HallID", "ChiefID")
VALUES
('Шкаф', '2005-04-27', 5600, 2020, 4700, 30, 1, 1),
('Обогреватель', '2016-06-19', 3200, 2021, 2800, 20, 2, 2),
('Компьютер', '2019-12-31', 46000, 2022, 39500, 10, 4, 3);

-- Пользователи
INSERT INTO public.users ("Login", "Password", "is_admin")
VALUES
('admin1', '9d516530dba7ae296eac0599b016c6038f230397', true),
('user1', '9d516530dba7ae296eac0599b016c6038f230397', false);

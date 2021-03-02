# Simple Filestorage HTTP API - хранилище файлов с доступом по HTTP на Python

![Build and publish](https://github.com/artif467/simple_filestorage_httpd_api/workflows/Build%20and%20publish/badge.svg)

Соответствующий образ доступен на [Docker Hub](https://hub.docker.com/repository/docker/art610/simple_filestorage_http_server_api/general)

![Analysing the code and run tests](https://github.com/artif467/simple_filestorage_httpapi/workflows/Analysing%20the%20code%20and%20run%20tests/badge.svg?branch=master)

Реализация демона (daemon), который предоставляет HTTP API для загрузки (upload), скачивания (download) и удаления (delete) файлов.

Рекомендуется:
- Linux Ubuntu 18.04;
- Python 3.8.x.

---

Следующее положение можно понять, взглянув на представленный исходный код, однако на всякий случай обозначу отдельно:

**Код не предназначен для production (это просто учебный пример)**

___

Для запуска можно склонировать данный репозиторий и перейти в каталог проекта:
```
git clone https://github.com/artif467/simple_filestorage_httpd_api.git
cd simple_filestorage_httpd_api
```

Либо загрузить архив, распаковать его и также перейти в каталог проекта:
```
wget --no-check-certificate --content-disposition https://github.com/artif467/simple_filestorage_httpd_api/archive/master.zip -O simple_filestorage_httpd_api.zip
unzip simple_filestorage_httpd_api.zip
cd simple_filestorage_httpd_api
```

Далее можно запустить основной python-скрипт:
```
# запус с параметрами по умолчанию 
python3.8 main.py

# запуск с пользовательскими параметрами
python3.8 main.py start --host <hostname> --port <port> --log <log_level> --listen <listen_clients_numb> --buffer <server_buffer_size>

# параметры
# <hostname> - имя хоста или IPv4 адрес, по умолчанию 0.0.0.0
# <port> - порт для http-сервера, по умолчанию 9000
# <log_level> - уровень для логов, по умолчанию DEBUG
# <listen_clients_numb> - количество соединений от клиентов, по умолчанию 5
# <server_buffer_size> - размер серверного буфера, по умолчанию 4096
```

Либо запустить bash-скрипт для формирования конфига для systemd:
```
sudo chmod +x setup_systemd.sh

# запус с параметрами по умолчанию 
./setup_systemd.sh

# запуск с пользовательскими параметрами
./setup_systemd.sh --host <hostname> --port <port> --log <log_level> --listen <listen_clients_numb> --buffer <server_buffer_size>

# параметры
# <hostname> - имя хоста или IPv4 адрес, по умолчанию 0.0.0.0
# <port> - порт для http-сервера, по умолчанию 9000
# <log_level> - уровень для логов, по умолчанию DEBUG
# <listen_clients_numb> - количество соединений от клиентов, по умолчанию 5
# <server_buffer_size> - размер серверного буфера, по умолчанию 4096
```

Для управления python-демоном можно использовать следующие команды:
```
python3.8 main.py start # запустить
python3.8 main.py get_pid   # получить идентификатор процесса
python3.8 main.py stop  # остановить
python3.8 main.py restart   # перезапустить
```

Для управления сервисом systemd можно использовать следующие команды:
```
systemctl status <service_name>
systemctl stop <service_name>
systemctl start <service_name>
systemctl restart <service_name>
```


**Upload: Загрузка файла на сервер**
Соответствует POST запросу к серверу. Фоновая служба (демон) получает файл от клиента и возвращает ответ (http response) с хэшом данного файла. Файл сохраняется на сервере, причем в качестве имени файла используется его хэш, в качестве подкаталога первые два символа хэша, а в качестве каталога для хранения всех файлов - каталог store/. В итоге файл с хэшом abcdef12345... будет сохранен в каталог:
`<PROJECT_DIR>/store/ab/abcdef12345...`
Алгоритм хэширования на выбор. В первой реализации будет использован алгоритм MD5 из библиотеки hashlib, ввиду простоты реализации. В последующих версиях возможно изменение, о чем будет указано в Changelog.
В случае успеха, клиенту также поступит ответ 200 - OK. При проблемах, связанных с соединением со стороны сервера, будет передан ответ 500 - Internal server error.

**Download: Скачивание файла**
Запрос на скачивание файла поступает в виде GET-запроса, в параметрах которого присутствует хэш-файла (параметр `file_hash=<required_file_hash>`), который требуется получить. Демон ищет данный файл в локальном хранилище и отдает, что соответствует ответу со статусом 200 - OK. Если демон не находит файл, то ответ будет со статусом 404 - Not Found.

**Delete: Удаление файла**
Запрос на удаление DELETE-запрос также содержит среди параметров хэш файла (параметр `file_hash=<required_file_hash>`), который демон будет искать в локальном хранилище на сервере, в случае обнаружения, данный файл будет удален и клиент получит ответ со статусом 200 - OK, в противном случае будет возвращен ответ со статусом 404 - Not Found. 

Если клиент пробует отправить запрос с методом, отличным от представленных выше, то он получит ответ со статусом 405 - Method Not Allowed.

Изначально был подготовлен чистый проект для разработки на Python 3.8 с использованием pytest, pylint, flake8, loguru и автопроверками при помощи GitHub Actions, однако планируется добавить typing для аннотаций типов.

**Используя любую часть представленного программного кода, вы автоматически принимаете и соглашаетесь со следующим положением:**
> Автор не несет никакой ответственности как за работоспособность самого скрипта и любой его отдельно взятой части, так и за работоспособность аппратного и программного обеспечения, на котором данный скрипт (любая его часть) был запущен. Автор не оказывает техническую поддержку. Ответы на любые вопросы исключительно по желанию самого автора.


Больше информации в скором времени будет представлено в разделе [WIKI](https://github.com/artif467/simple_filestorage_httpapi/wiki)

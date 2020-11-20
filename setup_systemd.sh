#!/bin/bash

PROJECT_DIR=$PWD

echo -e "\033[36mСформируем и добавим конфигурацию новой фоновой службы systemd. \033[0m"
echo -e "Вы можете указать параметры, чтобы задать адрес, порт и т.п. "
echo -e "Более полная информация содержится в README.md "

echo -e "\033[36mЗапуск следует производить с правами суперпользователя. \033[0m"
echo -e "\033[36mСервис будет связан с текущей директорией. \033[0m"
echo -ne "Продолжить установку? (y/n) " && read -r agr
if [[ $agr == 'y' ]]; then
    echo -e "\033[36mНачинаем установку \033[0m\n"
else
    echo -e "\033[36mВами был прерван процесс установки \033[0m\n"
    exit
fi

echo -e "Название SYSTEMD сервиса по умолчанию: \033[36mhttpd_uploads.service \033[0m"
echo -ne "\033[35mИзменить название SYSTEMD сервиса по умолчанию? (y/n) \033[0m" && read -r agr
if [[ $agr == 'y' ]]; then
    echo -e "\033[35mУкажите название сервиса: \033[0m" && read -r SYSTEMD_SERVICE_NAME
else
    SYSTEMD_SERVICE_NAME=httpd_uploads.service
fi

echo -ne "\033[35mСформировать файл конфигурации в текущей директории? (y/n) \033[0m" && read -r agr
if [[ $agr == 'y' ]]; then
    echo -e "Файл конфигурации сервиса будет создан в текущей директории:\033[36m"$PROJECT_DIR "\033[0m"
    echo -e "Вам потребуется самостоятельно добавить файл в директорию systemd \033[36m /lib/systemd/system/\033[0m\n"
    SYSTEMD_FILE_DIR=$PROJECT_DIR
    echo -e "Далее необходимо будет выполнить следующие команды:"
    echo -e "sudo systemctl daemon-reload"
    echo -e "sudo systemctl enable "$SYSTEMD_SERVICE_NAME
    echo -e "sudo systemctl start "$SYSTEMD_SERVICE_NAME "\n"
else
    echo -e "Файл конфигурации будет автоматически сформирован в директории:\033[36m /lib/systemd/system/"$SYSTEMD_SERVICE_NAME "\033[0m\n"
    SYSTEMD_FILE_DIR="/lib/systemd/system"
fi

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --service_name)
    SYSTEMD_SERVICE_NAME="$2"
    shift # past argument
    shift # past value
    ;;
    --host)
    HOST="$2"
    shift # past argument
    shift # past value
    ;;
    --port)
    PORT="$2"
    shift # past argument
    shift # past value
    ;;
    --log)
    LOG_LEVEL="$2"
    shift # past argument
    shift # past value
    ;;
    --listen)
    LISTEN="$2"
    shift # past argument
    shift # past value
    ;;
    --buffer)
    BUFFER="$2"
    shift # past argument
    shift # past value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

cat >$SYSTEMD_FILE_DIR/$SYSTEMD_SERVICE_NAME << EOF
[Unit]
Description=Simple File Upload HTTP Server
After=network.target
Conflicts=getty@tty1.service

[Service]
Type=simple
PIDFile=$PROJECT_DIR/daemon_pid.pid
ExecStart=/usr/bin/python3.8 $PROJECT_DIR/main.py start --host $HOST --port $PORT --log $LOG_LEVEL --listen $LISTEN --buffer $BUFFER
ExecStop=/usr/bin/python3.8 $PROJECT_DIR/main.py stop
ExecReload=/usr/bin/python3.8 $PROJECT_DIR/main.py restart
WorkingDirectory=$PROJECT_DIR/
StandardInput=tty-force
RemainAfterExit=yes
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SYSTEMD_SERVICE_NAME
sudo systemctl start $SYSTEMD_SERVICE_NAME

echo -e "\033[36mПараметры: \033[0m"
echo "SYSTEMD SERVICE NAME    = ${SYSTEMD_SERVICE_NAME}"
echo "SERVER HOST             = ${HOST}"
echo "SERVER PORT             = ${PORT}"
echo "LOG LEVEL               = ${LOG_LEVEL}"
echo "LISTEN CLIENTS MAX NUMB = ${LISTEN}"
echo "SERVER MAX BUFFER SIZE  = ${BUFFER}"
echo "DEFAULT                 = ${DEFAULT}"

echo -e 'Файл конфигурации службы был сформирован в директории:\033[36m '$SYSTEMD_FILE_DIR/$SYSTEMD_SERVICE_NAME '\033[0m\n'
echo -e 'Для управления сервисом можно использовать следующие команды:'
echo -e '\033[35msystemctl status '$SYSTEMD_SERVICE_NAME '\033[0m- вывести в консоль информацию о сервисе'
echo -e '\033[35msystemctl stop '$SYSTEMD_SERVICE_NAME '\033[0m- остановить сервис'
echo -e '\033[35msystemctl start '$SYSTEMD_SERVICE_NAME '\033[0m- запустить сервис'
echo -e '\033[35msystemctl restart '$SYSTEMD_SERVICE_NAME '\033[0m- перезапустить сервис\n'



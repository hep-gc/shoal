#!/bin/bash

#stop a running agent to apply changes to the config
service shoal-agent stop 2>/dev/null

#########################
# global variables used #
#########################
USE_NOT_DEFAULT=true

SHOAL_PYTHON=($(pip show shoal-agent 2>/dev/null|grep '^Version:'))
SHOAL_PYTHON_THREE=($(pip3 show shoal-agent 2>/dev/null|grep '^Version:'))
SHOAL_PYTHON_VERSION=''
SHOAL_PYTHON_THREE_VERSION=''
SOURCE_PATH=''
SOURCE_CONFIG_FILE=''
CONFIG_DIRECTORY=/etc/shoal/
CONFIG_FILE=/etc/shoal/shoal_agent.conf
CONFIG_FILE_OLD=/etc/shoal/shoal_agent_old.conf
LOG_FILE=/var/log/shoal_agent.log

DEFAULT_INTERVAL=''
DEFAULT_AMQP_SERVER_URL=''
DEFAULT_AMQP_PORT=''
DEFAULT_AMQP_VIRTUAL_HOST=''
DEFAULT_AMQP_EXCHANGE=''
DEFAULT_LOG_FILE=''
DEFAULT_LOGGING_LEVEL=''
DEFAULT_ADMIN_EMAIL=root@localhost

OLD_INTERVAL=''
OLD_AMQP_SERVER_URL=''
OLD_AMQP_PORT=''
OLD_AMQP_VIRTUAL_HOST=''
OLD_AMQP_EXCHANGE=''
OLD_LOG_FILE=''
OLD_LOGGING_LEVEL=''
OLD_ADMIN_EMAIL=''
DEFAULT=false;;
    esac
done

if $USE_NOT_DEFAULT; then
    # read default values of config options
    LINES=$(grep -v "^#\|\[" $SOURCE_CONFIG_FILE|sed -r "s/=/ /g")
    while read line
    do
        line_array=($line)
        case "${line_array[0]}" in
            "interval") DEFAULT_INTERVAL=${line_array[1]}
            ;;
            "amqp_server_url") DEFAULT_AMQP_SERVER_URL=${line_array[1]}
            ;;
            "amqp_port") DEFAULT_AMQP_PORT=${line_array[1]}
            ;;
            "amqp_virtual_host") DEFAULT_AMQP_VIRTUAL_HOST=${line_array[1]}
            ;;
            "amqp_exchange") DEFAULT_AMQP_EXCHANGE=${line_array[1]}
            ;;
            "log_file") DEFAULT_LOG_FILE=${line_array[1]}
            ;;
            "logging_level") DEFAULT_LOGGING_LEVEL=${line_array[1]}
            ;;
        esac
    done <<< "$LINES"

    if [ -e "$CONFIG_FILE_OLD" ]; then
        # read values of config options from existing config file if has one
        OLD_LINES=$(grep -v "^#\|\[" $CONFIG_FILE_OLD|sed -r "s/=/ /g")
        while read line
        do
            line_array=($line)
            case "${line_array[0]}" in
                "interval") OLD_INTERVAL=${line_array[1]}
                ;;
                "amqp_server_url") OLD_AMQP_SERVER_URL=${line_array[1]}
                ;;
                "amqp_port") OLD_AMQP_PORT=${line_array[1]}
                ;;
                "amqp_virtual_host") OLD_AMQP_VIRTUAL_HOST=${line_array[1]}
                ;;
                "amqp_exchange") OLD_AMQP_EXCHANGE=${line_array[1]}
                ;;
                "log_file") OLD_LOG_FILE=${line_array[1]}
                ;;
                "logging_level") OLD_LOGGING_LEVEL=${line_array[1]}
                ;;
                "admin_email") OLD_ADMIN_EMAIL=${line_array[1]}
                ;;
            esac
        done <<< "$OLD_LINES"

        echo "$CONFIG_FILE_OLD content is used in the following steps. We will walk you through the configuration options and allow you to set the values as you wish."

    else
        echo "We will walk you through the configuration options to set values."
    fi

    setEachNewValue $CONFIG_FILE interval "interval is at which the shoal-agent will contact the shoal server" $DEFAULT_INTERVAL $OLD_INTERVAL
    setEachNewValue $CONFIG_FILE admin_email "admin email is used for contact in case of issues with the shoal-agent or squid" $DEFAULT_ADMIN_EMAIL $OLD_ADMIN_EMAIL
    setEachNewValue $CONFIG_FILE amqp_server_url "this is the RabbitMQ server ip" $DEFAULT_AMQP_SERVER_URL $OLD_AMQP_SERVER_URL
    setEachNewValue $CONFIG_FILE amqp_port "this is the port number for amqp connection" $DEFAULT_AMQP_PORT $OLD_AMQP_PORT
    setEachNewValue $CONFIG_FILE amqp_virtual_host "this is used for RabbitMQ virtual host" $DEFAULT_AMQP_VIRTUAL_HOST $OLD_AMQP_VIRTUAL_HOST
    setEachNewValue $CONFIG_FILE amqp_exchange "this is the RabbitMQ exchange name" $DEFAULT_AMQP_EXCHANGE $OLD_AMQP_EXCHANGE
    setEachNewValue $CONFIG_FILE log_file "this is to set the path of the log file" $DEFAULT_LOG_FILE $OLD_LOG_FILE
    setEachNewValue $CONFIG_FILE logging_level "this decides how much information to write to the log file, select one from 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'" $DEFAULT_LOGGING_LEVEL $OLD_LOGGING_LEVEL

# create log file and change ownership
touch $LOG_FILE
chown shoal:shoal $LOG_FILE

if [ ! -z "$(command -v systemctl)" ]; then
    systemctl daemon-reload
    echo "Reloaded units for shoal-agent.service" 
fi

service shoal-agent restart
echo "Started the shoal-agent using the configuration file at $CONFIG_FILE. If you used a configuration file stored at other locations previously, please be aware that shoal-agent now only uses the configuration file at $CONFIG_FILE."



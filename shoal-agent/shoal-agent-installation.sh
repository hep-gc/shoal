#!/bin/bash

service shoal-agent stop 2>/dev/null

groupadd -f shoal
useradd shoal -g shoal 2>/dev/null

shoal_python=($(pip show shoal-agent 2>/dev/null|grep Version))
shoal_python_three=($(pip3 show shoal-agent 2>/dev/null|grep Version))

if [ ! -z "$shoal_python" ] && [ ! -z "${shoal_python[1]}" ]; then
    shoal_python_version=${shoal_python[1]}
fi 
if [ ! -z "$shoal_python_three" ] && [ ! -z "${shoal_python_three[1]}" ]; then
    shoal_python_three_version=${shoal_python_three[1]}
fi 

compareVersion() {
    local path
    local first_version=$1
    local second_version=$2
    local lower=$(printf '%s\n' "$first_version" "$second_version"|sort -V|head -n1)
    if [ "$lower" == "$first_version" ]; then
        path=/usr/local/share/shoal-agent
    else
        path=/usr/share/shoal-agent
    fi
    echo "$path"
}

if [ ! -z "$shoal_python_version" ] && [ ! -z "$shoal_python_three_version" ]; then
    SOURCE_PATH=$(compareVersion $shoal_python_version $shoal_python_three_version)
elif [ ! -z "$shoal_python_version" ]; then
    SOURCE_PATH=/usr/share/shoal-agent
elif [ ! -z "$shoal_python_three_version" ]; then
    SOURCE_PATH=/usr/local/share/shoal-agent
else
    echo Could not find the shoal-agent package, please check your pip install
    exit 0
fi

cp "$SOURCE_PATH/shoal-agent.init" /etc/init.d/
cp "$SOURCE_PATH/shoal-agent.logrotate" /etc/logrotate.d/
cp "$SOURCE_PATH/shoal-agent.service" /usr/lib/systemd/system/ 2>/dev/null

CONFIG_FILE=/etc/shoal/shoal_agent.conf
CONFIG_FILE_OLD=/etc/shoal/shoal_agent_old.conf
SOURCE_FILE="$SOURCE_PATH/shoal_agent.conf"
CONFIG_DIRECTORY=/etc/shoal/

CFG_CONTENT=$(grep -v "^#\|\[" $SOURCE_FILE)
eval "$CFG_CONTENT"

DEFAULT_INTERVAL=$interval
DEFAULT_AMQP_SERVER_URL=$amqp_server_url
DEFAULT_AMQP_PORT=$amqp_port
DEFAULT_AMQP_VIRTUAL_HOST=$amqp_virtual_host
DEFAULT_AMQP_EXCHANGE=$amqp_exchange
DEFAULT_LOG_FILE=$log_file
DEFAULT_LOGGING_LEVEL=$logging_level

setEachNewValue() {
    local label=$1
    local info=$2
    local default=$3
    local old=$4
    local enter_value

    if [ ! -z "$old" ]; then
        echo $"Please enter a value for setting the $label, $info. Your currently $label value is '$old', and the default value is '$default'. If you want to use the default, press 'Enter':"
    else
        echo $"Please enter a value for setting the $label, $info. The default value is '$default'. If you want to use the default, press 'Enter':"
    fi
    read enter_value
    if [ ! -z "$enter_value" ]; then
        if [ "$label" == "log_file" ]; then
            touch $enter_value
            chown shoal:shoal $enter_value
        fi
        if [ "$label" == "admin_email" ]; then
            origin=$"#$label=$default"
        else
            origin=$"$label=$default"
        fi
        replace=$"$label=$enter_value"
        sed -i "s|$origin|$replace|g" $CONFIG_FILE
    else
        if [ "$label" == "log_file" ]; then
            touch $default
            chown shoal:shoal $default 
        fi  
    fi

}

OLD_INTERVAL=''
OLD_AMQP_SERVER_URL=''
OLD_AMQP_PORT=''
OLD_AMQP_VIRTUAL_HOST=''
OLD_AMQP_EXCHANGE=''
OLD_LOG_FILE=''
OLD_LOGGING_LEVEL=''

if [ -f "$CONFIG_FILE" ]; then
    echo Found an existing config file at $CONFIG_FILE, backed it up at $CONFIG_FILE_OLD. We will walk you through the configuration options and allow you to set the values
 
    OLD_CFG_CONTENT=$(grep -v "^#\|\[" $CONFIG_FILE|sed -r 's/\s+=\s/=/g')
    eval "$OLD_CFG_CONTENT"

    OLD_INTERVAL=$interval
    OLD_AMQP_SERVER_URL=$amqp_server_url
    OLD_AMQP_PORT=$amqp_port
    OLD_AMQP_VIRTUAL_HOST=$amqp_virtual_host
    OLD_AMQP_EXCHANGE=$amqp_exchange
    OLD_LOG_FILE=$log_file
    OLD_LOGGING_LEVEL=$logging_level

    mv $CONFIG_FILE $CONFIG_FILE_OLD
else
    echo No configuration file has been found at $CONFIG_FILE, we will walk you through the configuration options and allow you to set the values
 
    if [ ! -d "$CONFIG_DIRECTORY" ]; then
        mkdir $CONFIG_DIRECTORY
    fi
fi

cp $SOURCE_FILE $CONFIG_DIRECTORY
setEachNewValue interval "interval is at which the shoal-agent will contact the shoal server" $DEFAULT_INTERVAL $OLD_INTERVAL
setEachNewValue admin_email "admin email is used for contact in case of issues with the shoal-agent or squid" root@localhost
setEachNewValue amqp_server_url "this is the RabbitMQ server ip" $DEFAULT_AMQP_SERVER_URL $OLD_AMQP_SERVER_URL
setEachNewValue amqp_port "this is the port number for amqp connection" $DEFAULT_AMQP_PORT $OLD_AMQP_PORT
setEachNewValue amqp_virtual_host "this is used for RabbitMQ virtual host" $DEFAULT_AMQP_VIRTUAL_HOST $OLD_AMQP_VIRTUAL_HOST
setEachNewValue amqp_exchange "this is the RabbitMQ exchange name" $DEFAULT_AMQP_EXCHANGE $OLD_AMQP_EXCHANGE
setEachNewValue log_file "this is to set the path of the log file" $DEFAULT_LOG_FILE $OLD_LOG_FILE
setEachNewValue logging_level "this decides how much information to write to the log file, select one from 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'" $DEFAULT_LOGGING_LEVEL $OLD_LOGGING_LEVEL

if [ ! -z "$(command -v systemctl)" ]; then
    systemctl daemon-reload
    echo Reloaded units for shoal-agent.service 
fi

service shoal-agent restart
echo Started the shoal-agent, check your configuration file at $CONFIG_FILE. If you are using a configuration file stored at other locations previously, please be aware that shoal-agent now only uses the configuration file at $CONFIG_FILE




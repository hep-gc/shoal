#!/bin/bash

#stop a running agent to apply changes to the config
service shoal-agent stop 2>/dev/null

#########################
# global variables used #
#########################
SHOAL_PYTHON=($(pip show shoal-agent 2>/dev/null|grep Version))
SHOAL_PYTHON_THREE=($(pip3 show shoal-agent 2>/dev/null|grep Version))
SHOAL_PYTHON_VERSION=''
SHOAL_PYTHON_THREE_VERSION=''
SOURCE_PATH=''
SOURCE_CONFIG_FILE=''
CONFIG_DIRECTORY=/etc/shoal/
CONFIG_FILE=/etc/shoal/shoal_agent.conf
CONFIG_FILE_OLD=/etc/shoal/shoal_agent_old.conf

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

##################################################

compareShoalVersion() {
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

setEachNewValue() {
    local config_file=$1
    local label=$2
    local info=$3
    local default=$4
    local old=$5
    local enter_value

    if [ ! -z "$old" ]; then
        echo $"Please enter a value for setting the $label, $info. Your currently $label value is '$old', and the default value is '$default'. If you want to use the default, press 'Enter':"
    else
        echo $"Please enter a value for setting the $label, $info. The default value is '$default'. If you want to use the default, press 'Enter':"
    fi
    read enter_value
    if [ ! -z "$enter_value" ]; then
        if [ "$label" == "log_file" ]; then
            # create log value and change ownership
            touch $enter_value
            chown shoal:shoal $enter_value
        fi
        if [ "$label" == "admin_email" ]; then
            origin=$"#$label=$default"
        else
            origin=$"$label=$default"
        fi
        replace=$"$label=$enter_value"
        sed -i "s|$origin|$replace|g" $config_file
    else
        if [ "$label" == "log_file" ]; then
            # create log value and change ownership
            touch $default
            chown shoal:shoal $default 
        fi  
    fi

}


###############################
#  MAIN                       #
###############################

# test if python2 or python3 was used for the install
if [ ! -z "$SHOAL_PYTHON" ] && [ ! -z "${SHOAL_PYTHON[1]}" ]; then
    SHOAL_PYTHON_VERSION=${SHOAL_PYTHON[1]}
fi 
if [ ! -z "$SHOAL_PYTHON_THREE" ] && [ ! -z "${SHOAL_PYTHON_THREE[1]}" ]; then
    SHOAL_PYTHON_THREE_VERSION=${SHOAL_PYTHON_THREE[1]}
fi 

if [ ! -z "$SHOAL_PYTHON_VERSION" ] && [ ! -z "$SHOAL_PYTHON_THREE_VERSION" ]; then
    SOURCE_PATH=$(compareShoalVersion $SHOAL_PYTHON_VERSION $SHOAL_PYTHON_THREE_VERSION)
elif [ ! -z "$SHOAL_PYTHON_VERSION" ]; then
    SOURCE_PATH=/usr/share/shoal-agent
elif [ ! -z "$SHOAL_PYTHON_THREE_VERSION" ]; then
    SOURCE_PATH=/usr/local/share/shoal-agent
else
    echo "Could not find the shoal-agent package. Please check your pip install."
    exit 0
fi

# add user/group shoal
groupadd -f shoal
useradd shoal -g shoal 2>/dev/null

# copy files to proper locations
cp "$SOURCE_PATH/shoal-agent.init" /etc/init.d/
cp "$SOURCE_PATH/shoal-agent.logrotate" /etc/logrotate.d/
cp "$SOURCE_PATH/shoal-agent.service" /usr/lib/systemd/system/ 2>/dev/null

SOURCE_CONFIG_FILE="$SOURCE_PATH/shoal_agent.conf"

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

if [ -f "$CONFIG_FILE" ]; then

    OLD_LINES=$(grep -v "^#\|\[" $CONFIG_FILE|sed -r "s/=/ /g")
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
        esac
    done <<< "$OLD_LINES"

    # rename the existing cofig file
    mv $CONFIG_FILE $CONFIG_FILE_OLD
    echo "Found an existing config file at $CONFIG_FILE. It is renamed to $CONFIG_FILE_OLD and its content is used in the following steps. We will walk you through the configuration options and allow you to set the values as you wish."

else
    echo "No previous configuration file has been found at $CONFIG_FILE.  We will walk you through the configuration options to set new values."
 
    if [ ! -d "$CONFIG_DIRECTORY" ]; then
        mkdir $CONFIG_DIRECTORY
    fi
fi

# copy the new config file to the preper location, and rewrite values based on user input
cp $SOURCE_CONFIG_FILE $CONFIG_DIRECTORY
setEachNewValue $CONFIG_FILE interval "interval is at which the shoal-agent will contact the shoal server" $DEFAULT_INTERVAL $OLD_INTERVAL
setEachNewValue $CONFIG_FILE admin_email "admin email is used for contact in case of issues with the shoal-agent or squid" $DEFAULT_ADMIN_EMAIL $OLD_ADMIN_EMAIL
setEachNewValue $CONFIG_FILE amqp_server_url "this is the RabbitMQ server ip" $DEFAULT_AMQP_SERVER_URL $OLD_AMQP_SERVER_URL
setEachNewValue $CONFIG_FILE amqp_port "this is the port number for amqp connection" $DEFAULT_AMQP_PORT $OLD_AMQP_PORT
setEachNewValue $CONFIG_FILE amqp_virtual_host "this is used for RabbitMQ virtual host" $DEFAULT_AMQP_VIRTUAL_HOST $OLD_AMQP_VIRTUAL_HOST
setEachNewValue $CONFIG_FILE amqp_exchange "this is the RabbitMQ exchange name" $DEFAULT_AMQP_EXCHANGE $OLD_AMQP_EXCHANGE
setEachNewValue $CONFIG_FILE log_file "this is to set the path of the log file" $DEFAULT_LOG_FILE $OLD_LOG_FILE
setEachNewValue $CONFIG_FILE logging_level "this decides how much information to write to the log file, select one from 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'" $DEFAULT_LOGGING_LEVEL $OLD_LOGGING_LEVEL

if [ ! -z "$(command -v systemctl)" ]; then
    systemctl daemon-reload
    echo "Reloaded units for shoal-agent.service" 
fi

service shoal-agent restart
echo "Started the shoal-agent using the configuration file at $CONFIG_FILE. If you used a configuration file stored at other locations previously, please be aware that shoal-agent now only uses the configuration file at $CONFIG_FILE."



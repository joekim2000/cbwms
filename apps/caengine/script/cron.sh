#!/bin/sh
#
# cron.sh - Mar 11, 2017
#

CONFIG_FILE="/opt/JionLab/caengine/etc/caengine_cron.conf"
LOG_FILE="/var/log/JionLab/caengine/caengine_cron.log"

HOUR=$1
MINUTE=$2

while read a_line
do
	a_line=`echo $a_line | grep -v "^[ 	]*#"`

	if [ "X$a_line" != "X" ]
	then
		hour=`echo $a_line | awk '{ print $1 }'`
		minute=`echo $a_line | awk '{ print $2 }'`
		script=`echo $a_line | awk '{ print $3 }'`

		if [ $hour -eq $HOUR -a $minute -eq $MINUTE ]
		then
			T=`date '+%m/%d/%Y %T'`
			echo "$T $$ $script Starting" >> $LOG_FILE

			{
			$script
			} > /dev/null 2>&1
		fi
	fi
done < $CONFIG_FILE

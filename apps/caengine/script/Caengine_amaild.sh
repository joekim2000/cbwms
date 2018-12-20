#!/bin/sh
#
# Caengine_amaild.sh - Mar 28, 2017
#

RC="Caengine_amaild"
PID_DIR="/var/run/JionLab/caengine"
DAEMON_DIR="/opt/JionLab/caengine/bin"
DAEMON="caengine_amaild"
DAEMON_CMD="/opt/JionLab/caengine/bin/amaild.py"
DAEMON_WAIT_SLEEP=5
PID_FILE="amaild"
DAEMON_CMD_OPTIONS=
CONFIG_FILE=
LOG_DIR="/var/log/JionLab/caengine"
RC_LOG_FILE="/var/log/JionLab/caengine/Caengine_amaild.log"
MONITOR_SLEEP=60

my_sleep() {
	i=0
	c=$1

	while [ $i -lt $c ]
	do
		if [ -f $PID_DIR/$RC.mon ]
		then
			sleep 1
		else
			break
		fi

		i=`expr $i + 1`
	done
}

start_daemon() {
	RETVAL=0

	T=`date '+%m/%d/%Y %T'`
	echo "$T $$ $DAEMON Starting" >> $RC_LOG_FILE

	rm -f $PID_DIR/$PID_FILE.pid

	$DAEMON_CMD $DAEMON_CMD_OPTIONS start

	RETVAL=`expr $RETVAL + $?`

	sleep $DAEMON_WAIT_SLEEP

	return $RETVAL
}

stop_daemon() {
	RETVAL=0

	T=`date '+%m/%d/%Y %T'`
	echo "$T $$ $DAEMON Stopping" >> $RC_LOG_FILE

	$DAEMON_CMD $DAEMON_CMD_OPTIONS stop

	RETVAL=`expr $RETVAL + $?`

	for i in `ps -ef | grep "$DAEMON_CMD start" | awk '{ print $2 }'`
	do
		pid=$i

		ps -p $pid > /dev/null 2>&1

		if [ $? -eq 0 ]
		then
			kill -9 $pid
		fi
	done

	rm -f $PID_DIR/$PID_FILE.pid

	return $RETVAL
}

handlerK() {
	T=`date '+%m/%d/%Y %T'`
	echo "$T $$ $RC Killed" >> $RC_LOG_FILE

	exit 1
}

trap '' 1 2 3 10 12 13 14 23
trap 'handlerK' 9 15

T=`date '+%Y%m%d%H%M%S'`
mv -f $RC_LOG_FILE $RC_LOG_FILE.$T > /dev/null 2>&1

T=`date '+%m/%d/%Y %T'`
echo "$T $$ $RC Starting" >> $RC_LOG_FILE

echo $$ > $PID_DIR/$RC.pid

while [ -f $PID_DIR/$RC.mon ]
do
	while [ -f $PID_DIR/$RC.mon ]
	do
		if [ -f $PID_DIR/$RC.pid ]
		then
			pid=`cat $PID_DIR/$RC.pid`

			if [ "X$pid" != "X$$" ]
			then
				break
			fi
		else
			break
		fi

		if [ -f $PID_DIR/$PID_FILE.pid ]
		then
			pid=`cat $PID_DIR/$PID_FILE.pid`

			ps -p $pid > /dev/null 2>&1

			if [ $? -ne 0 ]
			then
				break
			fi
		else
			break
		fi

		my_sleep $MONITOR_SLEEP
	done

	if [ -f $PID_DIR/$RC.mon ]
	then
		if [ -f $PID_DIR/$RC.pid ]
		then
			pid=`cat $PID_DIR/$RC.pid`

			if [ "X$pid" != "X$$" ]
			then
				break
			fi
		else
			break
		fi

		stop_daemon
	fi

	if [ -f $PID_DIR/$RC.mon ]
	then
		if [ -f $PID_DIR/$RC.pid ]
		then
			pid=`cat $PID_DIR/$RC.pid`

			if [ "X$pid" != "X$$" ]
			then
				break
			fi
		else
			break
		fi

		start_daemon
	fi
done

if [ -f $PID_DIR/$RC.pid ]
then
	pid=`cat $PID_DIR/$RC.pid`

	if [ "X$pid" = "X$$" ]
	then
		rm -f $PID_DIR/$RC.pid
	fi
fi

T=`date '+%m/%d/%Y %T'`
echo "$T $$ $RC Shutdowned" >> $RC_LOG_FILE

exit 0

#!/bin/sh
#
# caengine_rmaild.rc.sh - Mar 10, 2017
#

AUTO_START="yes"
RC="Caengine_rmaild"
PID_DIR="/var/run/JionLab/caengine"
DAEMON_DIR="/opt/JionLab/caengine/bin"
DAEMON="caengine_rmaild"
DAEMON_CMD="/opt/JionLab/caengine/bin/rmaild.py"
DAEMON_WAIT_SLEEP=5
PID_FILE="rmaild"
DAEMON_CMD_OPTIONS=
CONFIG_FILE=
LOG_DIR="/var/log/JionLab/caengine"
MONITOR_WAIT_SLEEP=5
FBM_USER="corebrdg"

PATH=$PATH:/sbin:/bin:/usr/sbin:/usr/bin
export PATH

if [ `uname -s` = "SunOS" ]
then
	user=`/usr/ucb/whoami | awk '{ print $1 }'`
else
	user=`whoami | awk '{ print $1 }'`
fi

case "$user" in
root | $FBM_USER)
	;;
*)
	echo "$RC: $user can't run this script"

	exit 1
	;;
esac

if [ "X$AUTO_START" != "Xyes" ]
then
	case "$1" in
	START | STOP | RESTART)
		;;
	*)
		echo "$RC: AUTO_START is disabled, please use {START|STOP|RESTART}"

		exit 1
		;;
	esac
fi

start_daemon() {
	echo "Starting $RC"

	RETVAL=0

	rm -f $PID_DIR/$PID_FILE.pid

	if [ $user = $FBM_USER ]
	then
		$DAEMON_CMD $DAEMON_CMD_OPTIONS start
	else
		su $FBM_USER -c "$DAEMON_CMD $DAEMON_CMD_OPTIONS start"
	fi

	RETVAL=`expr $RETVAL + $?`

	sleep $DAEMON_WAIT_SLEEP

	return $RETVAL
}

stop_daemon() {
	echo "Stopping $RC"

	RETVAL=0

	if [ $user = $FBM_USER ]
	then
		$DAEMON_CMD $DAEMON_CMD_OPTIONS stop
	else
		su $FBM_USER -c "$DAEMON_CMD $DAEMON_CMD_OPTIONS stop"
	fi

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

restart_daemon() {
	echo "Restarting $RC"

	RETVAL=0

	if [ $user = $FBM_USER ]
	then
		$DAEMON_CMD $DAEMON_CMD_OPTIONS restart
	else
		su $FBM_USER -c "$DAEMON_CMD $DAEMON_CMD_OPTIONS restart"
	fi

	RETVAL=`expr $RETVAL + $?`

	return $RETVAL
}

start_monitor() {
	echo "Starting Monitor $RC"

	if [ $user = $FBM_USER ]
	then
		echo $$ > $PID_DIR/$RC.mon

		$DAEMON_DIR/$RC > /dev/null 2>&1 &
	else
		su $FBM_USER -c "echo $$ > $PID_DIR/$RC.mon"

		su $FBM_USER -c "$DAEMON_DIR/$RC > /dev/null 2>&1 &"
	fi
}

stop_monitor() {
	echo "Stopping Monitor $RC"

	rm -f $PID_DIR/$RC.mon

	sleep $MONITOR_WAIT_SLEEP

	if [ -f $PID_DIR/$RC.pid ]
	then
		pid=`cat $PID_DIR/$RC.pid`

		ps -p $pid > /dev/null 2>&1

		if [ $? -eq 0 ]
		then
			kill $pid
		fi

		rm -f $PID_DIR/$RC.pid
	fi
}

case "$1" in
start_msg)
	echo "Starting $RC"
	;;
stop_msg)
	echo "Stopping $RC"
	;;
start | START)
	start_daemon
	start_monitor
	;;
stop | STOP)
	stop_monitor
	stop_daemon
	;;
restart | RESTART)
	##stop_daemon
	##start_daemon
	stop_monitor
	restart_daemon
	start_monitor
	;;
*)
	echo "Usage: $0 {start|stop|restart}"

	exit 1
	;;
esac

exit $?

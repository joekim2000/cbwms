#!/bin/sh
#
# caengine_cron.rc.sh - Jul 12, 2016
#

AUTO_START="yes"
LOG_SWITCH="no"
RC="Caengine_cron"
PID_DIR="/var/run/JionLab/caengine"
DAEMON_DIR="/opt/JionLab/caengine/bin"
MS_STAT="/opt/JionLab/fcp2/bin/ms_stat"
LOG_FILE="/var/log/JionLab/caengine/caengine_cron.log"
MONITOR_WAIT_SLEEP=5
FBM_USER="corebrdg"

PATH=$PATH:/sbin:/bin:/usr/sbin:/usr/bin
export PATH

if [ `uname -s` = "SunOS" ]
then
	user=`who am i | awk '{ print $1 }'`
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

start_script() {
	echo "Starting $RC"

	RETVAL=0

	if [ -f $LOG_FILE ]
	then
		if [ $LOG_SWITCH = "yes" ]
		then
			cur_date=`date '+%Y%m%d'`
			log_date=`$MS_STAT -c $LOG_FILE | cut -c 1-8`

			if [ $cur_date != $log_date ]
			then
				cp -p $LOG_FILE $LOG_FILE.$log_date

				T=`date '+%m/%d/%Y %T'`

				if [ $user = $FBM_USER ]
				then
					echo "$T $$ Switched Log File" > $LOG_FILE
				else
					su $FBM_USER -c "echo \"$T $$ Switched Log File\" > $LOG_FILE"
				fi
			fi
		else
			cp -p $LOG_FILE $LOG_FILE.old

			if [ $user = $FBM_USER ]
			then
				> $LOG_FILE
			else
				su $FBM_USER -c "> $LOG_FILE"
			fi
		fi
	fi

	T=`date '+%m/%d/%Y %T'`

	if [ $user = $FBM_USER ]
	then
		echo "$T $$ $RC Starting" >> $LOG_FILE
	else
		su $FBM_USER -c "echo \"$T $$ $RC Starting\" >> $LOG_FILE"
	fi

	if [ $user = $FBM_USER ]
	then
		echo $$ > $PID_DIR/$RC.mon

		$DAEMON_DIR/$RC > /dev/null 2>&1 &
	else
		su $FBM_USER -c "echo $$ > $PID_DIR/$RC.mon"

		su $FBM_USER -c "$DAEMON_DIR/$RC > /dev/null 2>&1 &"
	fi

	RETVAL=`expr $RETVAL + $?`

	return $RETVAL
}

stop_script() {
	echo "Stopping $RC"

	RETVAL=0

	T=`date '+%m/%d/%Y %T'`

	if [ $user = $FBM_USER ]
	then
		echo "$T $$ $RC Stopping" >> $LOG_FILE
	else
		su $FBM_USER -c "echo \"$T $$ $RC Stopping\" >> $LOG_FILE"
	fi

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

	return $RETVAL
}

case "$1" in
start_msg)
	echo "Starting $RC"
	;;
stop_msg)
	echo "Stopping $RC"
	;;
start | START)
	start_script
	;;
stop | STOP)
	stop_script
	;;
restart | RESTART)
	stop_script
	start_script
	;;
*)
	echo "Usage: $0 {start|stop|restart}"

	exit 1
	;;
esac

exit $?

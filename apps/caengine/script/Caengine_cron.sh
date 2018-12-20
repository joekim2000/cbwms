#!/bin/sh
#
# Caengine_cron.sh - Mar 11, 2017
#

LOG_SWITCH="no"
RC="Caengine_cron"
PID_DIR="/var/run/JionLab/caengine"
SCRIPT_DIR="/opt/JionLab/caengine/script"
SCRIPT="cron.sh"
MS_STAT="/opt/JionLab/fcp2/bin/ms_stat -e"
LOG_FILE="/var/log/JionLab/caengine/caengine_cron.log"
RC_LOG_FILE="/var/log/JionLab/caengine/Caengine_cron.log"
SCRIPT_SLEEP=45

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

log_switch() {
	cp -p $LOG_FILE $LOG_FILE.$now_date

	T=`date '+%m/%d/%Y %T'`
	echo "$T $$ Switched Log File" > $LOG_FILE

	now_date=$cur_date
}

handlerK() {
	T=`date '+%m/%d/%Y %T'`
	echo "$T $$ $RC Killed" >> $RC_LOG_FILE

	exit 1
}

trap '' 1 2 3 10 12 13 14 17 23
trap 'handlerK' 9 15

if [ $LOG_SWITCH = "yes" ]
then
	now_date=`date '+%Y%m%d'`
fi

T=`date '+%Y%m%d%H%M%S'`
mv -f $RC_LOG_FILE $RC_LOG_FILE.$T > /dev/null 2>&1

T=`date '+%m/%d/%Y %T'`
echo "$T $$ $RC Starting" >> $RC_LOG_FILE

echo $$ > $PID_DIR/$RC.pid

while [ -f $PID_DIR/$RC.mon ]
do
	t0=`$MS_STAT`

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

	hour=`date '+%H'`
	minute=`date '+%M'`

	{
	$SCRIPT_DIR/$SCRIPT $hour $minute
	} > /dev/null 2>&1 &

	if [ $LOG_SWITCH = "yes" ]
	then
		cur_date=`date '+%Y%m%d'`

		if [ $cur_date != $now_date ]
		then
			log_switch
		fi
	fi

	t1=`$MS_STAT`
	t2=`expr $t1 - $t0`
	t3=`expr $SCRIPT_SLEEP - $t2`

	if [ $t3 -gt 0 ]
	then
		my_sleep $t3
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

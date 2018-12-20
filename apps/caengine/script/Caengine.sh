#!/bin/sh
#
# Caengine.sh - Jan 17, 2017
#

PID_DIR="/var/run/JionLab"
DAEMON="caengine"
USER_GROUP="root:root"

UNAME=`uname -s`
CMD=`basename $0`

case $UNAME in
Linux)
	RC="/etc/rc.d/init.d"
	RC2="/etc/rc.d/rc3.d"
	;;
SunOS)
	RC="/etc/init.d"
	RC2="/etc/rc2.d"
	;;
AIX)
	RC="/etc/rc.d/init.d"
	RC2="/etc/rc.d/rc2.d"
	;;
HP-UX)
	RC="/sbin/init.d"
	RC2="/sbin/rc2.d"
	;;
esac

start_service() {
	if [ $UNAME = "Linux" ]
	then
		rel=`uname -r | cut -d '.' -f 1`

		if [ $rel -ge 3 ]
		then
			if [ ! -d $PID_DIR/$DAEMON ]
			then
				mkdir -p $PID_DIR/$DAEMON

				chown $USER_GROUP $PID_DIR/$DAEMON
			fi
		fi
	fi

	for i in `ls $RC2/S*$DAEMON* 2>/dev/null`
	do
		daemon=`echo $i | sed "s|$RC2/S[0-9]*||"`

		$RC/$daemon start
	done
}

stop_service() {
	for i in `ls $RC2/K*$DAEMON* 2>/dev/null`
	do
		daemon=`echo $i | sed "s|$RC2/K[0-9]*||"`

		$RC/$daemon stop
	done
}

case "$1" in
start)
	start_service
	;;
stop)
	stop_service
	;;
restart)
	stop_service
	start_service
	;;
*)
	echo "Usage: $CMD {start|stop|restart}"

	exit 1
	;;
esac

exit $?

rotateroot=`pwd`
cd $rotateroot
timestamp=$(date +'%s')
logid=$timestamp
cd ./logrotate2
/usr/bin/python2 bin/logrotate3.py -t $timestamp --logid $logid

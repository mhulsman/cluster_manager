#/bin/bash
set -e

ENVPATH=$1
ADDRESS=$2
PORT=$3
PARAMNR=$4
ENVNAME=`basename $ENVPATH`

export LFC_HOME=/grid/lsgrid/alexeyg/
export LFC_HOST=lfc.grid.sara.nl

#Wait a random time to not overload the server after submission of a number of jobs.
echo "Waiting..."
WAIT=$[ ($RANDOM % 180) ]
sleep $WAIT
echo "Waiting period over for $PARAMNR, starting bootstrap."

#load environment
chmod 744 ./gcp
./gcp $ENVPATH .
tar -xzf $ENVNAME
CURDIR=`pwd`

cd sys_enhance
cat _paths | sed s#ONAME#$CURDIR#g > paths
echo "Where is bash?"
which bash
echo "File created?"
ls -lh ./paths
. ./paths
echo "Environment loaded for $PARAMNR, starting work."

#run job
cd work
./ipengine_chief -a $ADDRESS -p $PORT -l -t GRID

#cleaning
echo "Work for $PARAMNR finished, cleaning up..."
cd /
rm -rf $CURDIR/sys_enhance
echo "Done"


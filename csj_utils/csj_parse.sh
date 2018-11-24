if [ "$#" != 2 ]; then
   echo 'you need two args, dir and fp'
   exit
fi

Dir=$1
OutputFP=$2

if [ ! -d "$Dir" ]; then 
    echo "$Dir does not exist, aborting"
    exit
else
    if [ `ls $Dir/*.xml` == "" ];then
	echo 'xml files dont exist in the dir specified, aborting'
	exit
    fi
fi

if [ -f "$OutputFP" ]; then
   echo "$OutputFP exists, and it will be overwritten unless you stop it. Is this okay? [y/n]"
   Answer=read
   if [ $Answer != 'y' ]; then
      exit
   fi
fi




echo '' > $OutputFP

for File in $Dir/*.xml
do
    python3 csj_parse.py $File >> $OutputFP
done

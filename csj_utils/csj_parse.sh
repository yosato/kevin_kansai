if [ "$#" < 2 ]; then
   echo 'you need two args, input dir and out fp'
   exit
fi

Dir=$1
OutputFP=$2
Prefix=$3

if [ ! -d "$Dir" ]; then 
    echo "$Dir does not exist, aborting"
    exit
else
    Files=`ls $Dir/*.xml`
    if [ -z "$Files" ];then
	echo 'xml files dont exist in the dir specified, aborting'
	exit
    fi
fi

if [ -f "$OutputFP" ]; then
   echo "$OutputFP exists, and it will be overwritten unless you stop it. Is this okay? [y/n]"
   read Answer
   if [ $Answer != 'y' ]; then
      exit
   fi
fi

OutFP=$OutputFP${Prefix}

echo '' > $OutFP

for File in $Dir/${Prefix}*.xml
do
    echo -en "processing $File ..."
    python3 csj_parse.py $File >> ${OutFP}
    echo -en ' done\n'
    
done

echo "All done, results in $OutFP"

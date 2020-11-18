FN=$1

cat $FN|awk -F"," '{print $1,$5}'|sed 's/ *$//'|sed -r 's:([\t ]+):/:g'|tr '\n' ' '|sed 's/ *EOS */\n/g' 
#cat $Out| sed -r 'G;:a;s/^(\S+)(\s*)(.*\n)/\3\2\1/;ta;s/\n//' > $Out.reverse


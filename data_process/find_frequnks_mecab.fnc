find_frequnks_mecab(){
    # finding frequnks from mecab
    sed -n '/UNK$/p' | sed '/記号,/d;/数,/d'| awk '{print $1}'| sed '/^[a-zA-Z]*$/d'| sort | uniq -c| sort -nr
}

mecab_unk(){
    if [ $1 = '' ]; then
	echo 'a filepath required'
	exit
    fi
    mecab -d $HOME/yosato/mecabKansaiModels/kansai_2/standard_kansai_kansai/model --unk-format %m'\t'%H'\tUNK\n' $1
}

lengthorder_top_frequnks(){

    cat $1 |\
    head -n 800| sed 's/^ *//' |awk '{print $2}'| romanise.sh > roman
    paste $1 roman | sed 's/^ *//' > both

    cat both | awk '{printf length($3)"\t"$2"\taaa\t"$3"\t"$4"\n"}'| sort -n| awk '{printf $2"\t"$3"\t"$4"\n"}'
}

mecab_plus_frequnks(){
    mecab_unk $1 > $1.mecab
    cat $1.mecab | find_frequnks_mecab > $1.mecab.frequnks
    lengthorder_top_frequnks $1.mecab.frequnks
}

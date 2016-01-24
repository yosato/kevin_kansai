# a number of things to do...
cat $1 | \
sed -e 's/\r//g' \
    -e 'y/　ｉｓ？！０１２３４５６７８９”/ is?!0123456789"/' \
    -e '/順番交替記号/d' \
    -e '/話し手記号/d' \
    -e 's/[\t ]\+[si][0-9]*,/\t/' |\
sed 's/^[。!?]\t..*$/&\nEOS/' #|\
#sed '/EOS/{N;s/EOS\nEOS/EOS/}' 

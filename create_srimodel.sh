for type in normal #vcomplex
do

    for direction in normal reverse
    do

	~/srilm/lm/bin/macosx/ngram-count -text processed/KSJKYTTKC.${type}.${direction}.simplemecab -lm models/model_ksj_${type}_${direction}.srilm
    done
done

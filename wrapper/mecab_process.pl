#!/bin/perl

##
## this programme assumes (for now) the following structure of dirs
## <model_old>/seed
##            /model
## <movel_new>/seed
##            /model
##            /corpus
## the seed directory should contain the original dictionaries as well as config files at the outset
## the model directory should get populated with new (parametrerised) dics as well as the model file that is their base
## the corpus directory should contain the training corpus (in one file). The script will generate the result file here. 
## finally, the test sentences and their solutions (two files) should be placed in the base dir.

use strict;
#use warnings;

my $Usage='mecab_process.pl [root-dir] [old-model] [new-model] <retrain-or-not (bool)>';


# checking the args
if (@ARGV<3){
    print "ERROR: You need at least three arguments\n" . $Usage . "\n";
    exit;
}

use Config;

# more paths may need to be modified/added for your environment
# the var for home dir different between win/lin
if ( "$Config{osname}" == 'windows') {
    my $HomeDir="$ENV{HOMEDIR}/$ENV{HOMEPATH}";
} else {
    my $HomeDir=$ENV{HOME};
}
my $Repo="$HomeDir/kevin_kansai";
my $EvalProg="${Repo}/eval_progs/eval_mecab.py";
#my $MecabDir="/usr/local/libexec/mecab";
#$ENV{PATH} = "$MecabDir:$ENV{PATH}";

my $TgtDir=$ARGV[0];
my $OldVers=$ARGV[1];
my $NewVers=$ARGV[2];
my $TrainP=$ARGV[3];

my $Dir="$Repo/$TgtDir";

my $TestSentsWest="${Dir}/test_sentences_kansai.txt";
my $TestSentsStd="${Dir}/test_sentences_standard.txt";
my $SolutionsWest="${Dir}/solutions_kansai.mecab";
my $SolutionsStd="${Dir}/solutions_standard.mecab";

sub version2subdir{
    my ($Vers,$SubDir)=@_;
    return "$Dir/$Vers/$SubDir";
}

my $OldModelDir=version2subdir("${OldVers}","model");
my $OldModelFile="$OldModelDir/model_${OldVers}.mod";

my $NewSeedDir=version2subdir("${NewVers}","seed");
my $NewModelDir=version2subdir("${NewVers}","model");
my $NewCorpusDir=version2subdir("${NewVers}","corpus");
my $TrainCorpus="${NewCorpusDir}/corpus_train_${NewVers}.mecab";

my $NewModelFile="${NewModelDir}/model_${NewVers}";



# just for checking existence of required files and dirs
my @PriorFiles=($OldModelFile,$NewSeedDir,$TrainCorpus,$TestSentsWest,$TestSentsStd,$SolutionsWest,$SolutionsStd);

foreach my $File (@PriorFiles) {
    if (! -e $File){
	print "$File does not exist\n";
	exit;
    }
}

# some functions

sub ifnosucess_fail{
    my ($RetVal,$Operation)=@_;
    if ($RetVal!=0){
	die "${Operation} failed";
    }
}

sub run_mecab_evaluate{
    my ($ModelVers)=@_;
    
    my $ModelDir=version2subdir("$ModelVers","model");
    my $CorpusDir=version2subdir("$ModelVers","corpus");

    my $ResultFileStd="${Dir}/${ModelVers}/resultsOnStandardTest.mecab";
    my $ResultFileWest="${Dir}/${ModelVers}/resultsOnKansaiTest.mecab";
    my $ScoreFile="${Dir}/${ModelVers}/scores.txt";

    my $SysReturnEval1=system("mecab -d $ModelDir $TestSentsWest > $ResultFileWest");
    ifnosucess_fail($SysReturnEval1,"Kansai model mecab");

    my $SysReturnEval2=system("mecab -d $ModelDir $TestSentsStd > $ResultFileStd");
    ifnosucess_fail($SysReturnEval2,"Standard model mecab");

#open(my($FSr), '>', $ScoreFile) or die "Could not open file '$ScoreFile' $!";

    print "Scores for $ModelVers\n\n";
    print "On kansai data\n";

    system("python3 $EvalProg $ResultFileWest $SolutionsWest | tee $ScoreFile");
    
    print "\nOn standard data\n";

    system("python3 $EvalProg $ResultFileStd $SolutionsStd | tee -a $ScoreFile");

#close $FSr;

}

run_mecab_evaluate($OldVers);

my $CmdDicInd="mecab-dict-index -d $NewSeedDir -o $NewSeedDir 1>&2";
my $SysReturnDicInd=system($CmdDicInd);

ifnosucess_fail($SysReturnDicInd,"Orig dic indexing");

if ($TrainP eq "true" || $TrainP eq ""){
    my $SysReturnTrain=system("mecab-cost-train -M $OldModelFile -d $NewSeedDir $TrainCorpus $NewModelFile 1>&2");
    ifnosucess_fail($SysReturnTrain,"Retraining ");
}else{
    print "\nThis run skips retraining (dic only)\n\n";
}

if ($TrainP eq "false"){
    $NewModelFile=$OldModelFile;
}

my $SysReturnDicGen=system("mecab-dict-gen -m $NewModelFile -d $NewSeedDir -o $NewModelDir 1>&2");

ifnosucess_fail($SysReturnDicGen,"New dictionary creation");

my $SysReturnDicReind=system("mecab-dict-index -d $NewModelDir -o $NewModelDir 1>&2");

ifnosucess_fail($SysReturnDicReind,"New dic indexing");

run_mecab_evaluate($NewVers)




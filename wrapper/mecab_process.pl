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

my $HomeDir;
use Config;

# more paths may need to be modified/added for your environment
# the var for home dir different between win/lin
if ( $Config{osname} eq "windows") {
    $HomeDir="$ENV{HOMEDIR}/$ENV{HOMEPATH}";
} else {
    $HomeDir=$ENV{HOME};
}
my $DataDir="$HomeDir/Dropbox/Mecab";
my $Repo="$HomeDir/kevin_kansai";
my $EvalProg="${Repo}/eval_progs/eval_mecab.py";
#my $MecabDir="/usr/local/libexec/mecab";
#$ENV{PATH} = "$MecabDir:$ENV{PATH}";

my $TgtSubDir=$ARGV[0];
my $OldVers=$ARGV[1];
my $NewVers=$ARGV[2];
my $TrainP=$ARGV[3];

my $TgtDir="$DataDir/$TgtSubDir";

my $TestSentsWest="${TgtDir}/test_sentences_kansai.txt";
my $TestSentsStd="${TgtDir}/test_sentences_standard.txt";
my $SolutionsWest="${TgtDir}/solutions_kansai.mecab";
my $SolutionsStd="${TgtDir}/solutions_standard.mecab";

sub version2subdir{
    my ($Vers,$SubDir)=@_;
    return "$TgtDir/$Vers/$SubDir";
}

my $OldModelDir=version2subdir("${OldVers}","model");
my $OldModelFile="$OldModelDir/model_${OldVers}.mod";

my $NewSeedDir=version2subdir("${NewVers}","seed");
my $NewModelDir=version2subdir("${NewVers}","model");
my $NewCorpusDir=version2subdir("${NewVers}","corpus");

my $TrainCorpus="${NewCorpusDir}/corpus_train_${NewVers}.mecab";

my $NewModelFile="${NewModelDir}/model_${NewVers}";

my $NewCombinedVers="${OldVers}_" . $NewVers;
my $NewCombinedDir="${TgtDir}/${NewCombinedVers}";

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
	die "${Operation} failed\n";
    } else {
	print "${Operation} succeeded\n";
    }
}

sub run_mecab_evaluate{
    my ($ModelVers)=@_;
    
    my $ModelDir=version2subdir("$ModelVers","model");
    my $CorpusDir=version2subdir("$ModelVers","corpus");

    my $ResultFileStd="${TgtDir}/${ModelVers}/resultsOnStandardTest.mecab";
    my $ResultFileWest="${TgtDir}/${ModelVers}/resultsOnKansaiTest.mecab";
    my $ScoreFile="${TgtDir}/${ModelVers}/scores.txt";

    my $MecabCmdWest="mecab -d $ModelDir $TestSentsWest > $ResultFileWest";
    my $SysReturnMecab1=system($MecabCmdWest);
    ifnosucess_fail($SysReturnMecab1,"Kansai model mecab (before)");

    my $MecabCmdStd="mecab -d $ModelDir $TestSentsStd > $ResultFileStd";    
    my $SysReturnMecab2=system($MecabCmdStd);
    ifnosucess_fail($SysReturnMecab2,"Standard model mecab (before)");

    my $SysReturnEval1=system("python3 $EvalProg $ResultFileWest $SolutionsWest > $ScoreFile");
    ifnosucess_fail($SysReturnEval1,"Kansai model evaluation (before)");

    my $SysReturnEval2=system("python3 $EvalProg $ResultFileStd $SolutionsStd >> $ScoreFile");
    ifnosucess_fail($SysReturnEval1,"Standard model evaluation (before)");

    print "Results in ${ScoreFile}, the content of which as below (Kansai and standard):\n";
    
    open(my $ScoreFSr, '<', $ScoreFile);
    while (my $Line = <$ScoreFSr> ){
	print $Line;
    }
    

}

sub finalclean_preparenext{
    my ($NewCombinedDir)=@_;
    mkdir($NewCombinedDir);
}

sub main{

    finalclean_preparenext($NewCombinedDir);
    # pre-training results
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

    run_mecab_evaluate($NewVers);

}

main;


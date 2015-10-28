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
if (@ARGV<2){
    print "ERROR: You need at least two arguments\n" . $Usage . "\n";
    exit;
}

my $HomeDir;
use Config;
use File::Spec;


# more paths may need to be modified/added for your environment
# the var for home dir different between win/lin
if ( $Config{osname} eq "windows") {
    $HomeDir="$ENV{HOMEDIR}/$ENV{HOMEPATH}";
} else {
    $HomeDir='/Users/yosato';
    $HomeDir=$ENV{HOME};
}

my $DataDir="$HomeDir/Dropbox/Mecab";
my $Repo="$HomeDir/kevin_kansai";
my $EvalProg="${Repo}/eval_progs/eval_mecab.py";
#my $MecabDir="/usr/local/libexec/mecab";
#$ENV{PATH} = "$MecabDir:$ENV{PATH}";

#my $path = 'D:\Folder\AnotherFolder\file.txt';  # note the single quotes
#my @elements = File::Spec->splitdir($path);
#my $TgtDir=$ARGV[0];
my ($OldRtDirN,$OldVers)=split('/',$ARGV[0]);
my ($AddRtDirN,$AddVers)=split('/',$ARGV[1]);
my $CombRtDirN=$ARGV[2];
my $EvalOnlyP=$ARGV[3];
my $TestFileDir=$ARGV[4];
my $TrainP=$ARGV[5];


my $OldRtDir="${DataDir}/${OldRtDirN}";
my $AddRtDir="${DataDir}/${AddRtDirN}";
my $CombRtDir="${DataDir}/${CombRtDirN}";

my $TestSentsWest="${AddRtDir}/test_sentences_kansai.txt";
my $TestSentsStd="${OldRtDir}/test_sentences_standard.txt";
my $SolutionsWest="${AddRtDir}/solutions_kansai.mecab";
my $SolutionsStd="${OldRtDir}/solutions_standard.mecab";

my $OldModelDir="${OldRtDir}/${OldVers}/model";
my $OldModelFile="${OldModelDir}/model_${OldVers}.mod";

my $AddSeedDir="${AddRtDir}/${AddVers}/seed";
my $AddCorpusDir="${AddRtDir}/${AddVers}/corpus";

my $TrainCorpus="${AddCorpusDir}/corpus_train_${AddVers}.mecab";

my $CombVers=$OldVers . '_' . $AddVers;
my $CombVersDir="${AddRtDir}/${CombVers}";
my $CombModelDir="${CombVersDir}/model";

my $NewModelFile="${CombModelDir}/model_${AddVers}";



# just for checking existence of required files and dirs
my @PriorFiles=($OldModelFile,$AddSeedDir,$TrainCorpus,$TestSentsWest,$TestSentsStd,$SolutionsWest,$SolutionsStd);

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
    my ($ModelDir)=@_;
    my ($ModelRtDir,$ModelVers)=split('/',$ModelDir);
    
    my $ModelDir="${DataDir}/${ModelDir}/model";
    my $CorpusDir="${DataDir}/${ModelDir}/corpus";

    my $ResultFileStd="${DataDir}/${ModelRtDir}/resultsOnStandardTest.mecab";
    my $ResultFileWest="${DataDir}/${ModelRtDir}/resultsOnKansaiTest.mecab";
    my $ScoreFile="${DataDir}/${ModelRtDir}/scores.txt";

    my $MecabCmdWest="mecab -d $ModelDir $TestSentsWest;
# > $ResultFileWest";
    my $SysReturnMecab1=system($MecabCmdWest);
    ifnosucess_fail($SysReturnMecab1,"Kansai model mecab");

    my $MecabCmdStd="mecab -d $ModelDir $TestSentsStd > $ResultFileStd";    
    my $SysReturnMecab2=system($MecabCmdStd);
    ifnosucess_fail($SysReturnMecab2,"Standard model mecab");

    my $SysReturnEval1=system("python3 $EvalProg $ResultFileWest $SolutionsWest > $ScoreFile");
    ifnosucess_fail($SysReturnEval1,"Kansai model evaluation");

    my $SysReturnEval2=system("python3 $EvalProg $ResultFileStd $SolutionsStd >> $ScoreFile");
    ifnosucess_fail($SysReturnEval1,"Standard model evaluation");

    print "Results in ${ScoreFile}, the content of which as below (Kansai and standard):\n";
    
    open(my $ScoreFSr, '<', $ScoreFile);
    while (my $Line = <$ScoreFSr> ){
	print $Line;
    }
    

}

sub final_clean{
    my (@OldDicConfFPs,$CombVersDir)=@_;

    # collecting the fps copied from old dics in the seed
    my @Files2Del;
    foreach my $DicFP (@OldDicConfFPs){
	my $Basename=basename($DicFP);
	push(@Files2Del,"${AddSeedDir}/${Basename}");
    }

    
    foreach my $File (@Files2Del){
	unlink $File;
    }
}

sub prepare_files{
    use File::Basename;
    use File::Copy;

    my ($AddSeedDir,$OldDicConfFPs)=@_;

    
    for my $file (@{$OldDicConfFPs}) {
        copy("$file","$AddSeedDir") or die "Copy $file failed";
    }

#    my @CRTgts=glob("$AddSeedDir/*.csv");
    push(@{$OldDicConfFPs},$TrainCorpus);
    remove_crs_files(@{$OldDicConfFPs});
    
}

sub mkdir_ifnotexists{
    my ($DirN)=@_;
    if (! -d $DirN){
	mkdir $DirN;
	return 1;
    }else{
	return 1;
    }
}


sub remove_crs_files{
    my @FPs=@_;
    foreach my $FP (@FPs){
	remove_crs_file($FP);
    }
}

sub remove_crs_file{
    use File::Copy;
    
    my ($FP)=@_;
    open(FHr,'<',$FP);
    my $FPTmp="${FP}.tmp";
    open(FHw,'>',$FPTmp);
    while (<FHr>) {
	s/\r//g;
	print FHw $_;
    }
    close(FHr);
    close(FHw);
    move($FPTmp,$FP);

}

sub retrain_model{
    my $MecabLogFP="${AddRtDir}/mecab-train-${CombVers}.log";

    print "\nGenerating the original dic index\n";
    my $CmdDicInd="mecab-dict-index -d $AddSeedDir -o $AddSeedDir > $MecabLogFP 2>&1";
    my $SysReturnDicInd=system($CmdDicInd);
    
    ifnosucess_fail($SysReturnDicInd,"Orig dic indexing");

    print "\nNow the re-training has started (this may take time) ...\n";
    
    mkdir_ifnotexists($CombVersDir);
    unless (mkdir_ifnotexists($CombModelDir)){
	die ("mkdir failed for $CombModelDir\n");
    }

    if ($TrainP eq 'true' || $TrainP eq ""){
	my $SysReturnTrain=system("mecab-cost-train -M $OldModelFile -d $AddSeedDir $TrainCorpus $NewModelFile >> $MecabLogFP 2>&1");
	ifnosucess_fail($SysReturnTrain,"Retraining ");
    }else{
	print "\nThis run skips retraining (dic only)\n";
    }

    if ($TrainP eq "false"){
	$NewModelFile=$OldModelFile;
    }

    
    print "\nRe-building index (this may also take time) ...\n";
    my $SysReturnDicGen=system("mecab-dict-gen -m $NewModelFile -d $AddSeedDir -o $CombModelDir >> $MecabLogFP 2>&1");

    ifnosucess_fail($SysReturnDicGen,"New dictionary creation");


    my @CRTgts=glob("${CombModelDir}/*.{csv,def}");
    remove_crs_files(@CRTgts);

    
    my $SysReturnDicReind=system("mecab-dict-index -d $CombModelDir -o $CombModelDir >> $MecabLogFP 2>&1");

    ifnosucess_fail($SysReturnDicReind,"New dic indexing");

    print 'Congrats, new combined model re-built (retraining finished)';
    sleep(2);

}

sub main{
 
    print "First we evaluate the original model\n\n";
    run_mecab_evaluate("${OldRtDirN}/${OldVers}");

    my @OldDicConfFPs=glob("${OldModelDir}/*");
    
    print "\nCopying/creating config and dic files for a new model build\n";
    prepare_files($AddSeedDir,\@OldDicConfFPs);

    if (not $EvalOnlyP){
	retrain_model;
    }
    
    print "\nNow we evaluate the new model (fingers crossed)\n";
    run_mecab_evaluate("$AddRtDirN/$CombVers");

    print "\nCleaning files to finish up\n";
    final_clean(@OldDicConfFPs,$CombVersDir);

    print "Everything is done!!\n\n"

}

main;


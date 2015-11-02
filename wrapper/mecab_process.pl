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

my $Usage='mecab_process.pl [original_dir] [original_model] [additional_dir] [additional_model] [testfile_dir] <retrain-or-not (bool)>';


# checking the args
if (@ARGV<5){
    print "ERROR: You need at least five arguments\n" . $Usage . "\n";
    exit;
}

my $HomeDir;
use Config;

# more paths may need to be modified/added for your environment
# the var for home dir different between win/lin
if ( $Config{osname} eq "windows") {
    $HomeDir="$ENV{HOMEDIR}/$ENV{HOMEPATH}";
} else {
    $HomeDir='/Users/yosato';
    $HomeDir=$ENV{HOME};
}

#my $DataDir="$HomeDir/Dropbox/Mecab";
my $Repo="$HomeDir/kevin_kansai";
my $EvalProg="${Repo}/eval_progs/eval_mecab.py";
#my $MecabDir="/usr/local/libexec/mecab";
#$ENV{PATH} = "$MecabDir:$ENV{PATH}";

my $OldDir=$ARGV[0];
#my $OldDir="$DataDir/$OldSubDir";
my $OldVers=$ARGV[1];

my $AddDir=$ARGV[2];
#my $AddDir="$DataDir/$AddSubDir";
my $AddVers=$ARGV[3];
my $TestFileDir=$ARGV[4];
#my $TestFileDir="$DataDir/$TestFileSubDir";
my $TrainP=$ARGV[5];

my $TestSentsWest="${TestFileDir}/test_sentences_kansai.txt";
my $TestSentsStd="${TestFileDir}/test_sentences_standard.txt";
my $SolutionsWest="${TestFileDir}/solutions_kansai.mecab";
my $SolutionsStd="${TestFileDir}/solutions_standard.mecab";

my $OldModelDir="${OldDir}/${OldVers}/model";
my $OldModelFile="${OldModelDir}/model_${OldVers}.mod";

my $AddSeedDir="${AddDir}/${AddVers}/seed";
my $AddCorpusDir="${AddDir}/${AddVers}/corpus";

my $TrainCorpus="${AddCorpusDir}/corpus_train_${AddVers}.mecab";

my $CombVers=$OldVers . '_' . $AddVers;
my $CombVersDir="${AddDir}/${CombVers}";
my $CombModelDir="${CombVersDir}/model";

my $CombModelFile="${CombModelDir}/model_${AddVers}";



# just for checking existence of required files and dirs
my @PriorFiles=($OldModelFile,$AddSeedDir,$TestSentsWest,$TestSentsStd,$SolutionsWest,$SolutionsStd);

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

sub merge_corpora{
    my @Corpora=@_;

    open(FHw, '>>',$TrainCorpus);
    foreach my $Corpus (@Corpora){
	open(FHr,'<', $Corpus);
	while (<FHr>){
	    print FHw $_;
	}
	close(FHr);
	    }
    close(FHw);

    return 1;

}

sub run_mecab_evaluate{
    my ($TestFileDir,$ModelRtDir)=@_;
    
    my $ModelDir="${ModelRtDir}/model";
    
    my $TestSentsStd="${TestFileDir}/test_sentences_standard.txt";
    my $TestSentsWest="${TestFileDir}/test_sentences_kansai.txt";
    my $SolutionsStd="${TestFileDir}/solutions_standard.mecab";
    my $SolutionsWest="${TestFileDir}/solutions_kansai.mecab";

    
    my $ResultFileStd="${ModelRtDir}/resultsOnStandardTest.mecab";
    my $ResultFileWest="${ModelRtDir}/resultsOnKansaiTest.mecab";
    my $ScoreFile="${ModelRtDir}/scores.txt";

    my $MecabCmdWest="mecab -d $ModelDir $TestSentsWest > $ResultFileWest";
    my $SysReturnMecab1=system($MecabCmdWest);
    ifnosucess_fail($SysReturnMecab1,"Kansai model mecab");

    my $MecabCmdStd="mecab -d $ModelDir $TestSentsStd > $ResultFileStd";    
    my $SysReturnMecab2=system($MecabCmdStd);
    ifnosucess_fail($SysReturnMecab2,"Standard model mecab");


    
    my $SysReturnEval1=system("python3 $EvalProg $ResultFileWest $SolutionsWest > $ScoreFile");
    ifnosucess_fail($SysReturnEval1,"Kansai model evaluation");

    my $SysReturnEval2=system("python3 $EvalProg $ResultFileStd $SolutionsStd >> $ScoreFile");
    ifnosucess_fail($SysReturnEval1,"Standard model evaluation");

    #=== this is an ad hoc addition by ys to avoid k's prob of CRs, but we should investigate where they come from
    
    remove_crs_files(($ResultFileStd,$ResultFileWest));
    #==================================
    
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

    my (@OldDicConfFPs)=@_;


    for my $file (@OldDicConfFPs) {
        copy("$file","$AddSeedDir") or die "Copy $file failed";
    }

#    my @DefFNs=('char.def','feature.def','unk.def','rewrite.def','dicrc');
#    for my $file (@DefFNs) {
#        copy("${OldModelDir}/${file}","$AddSeedDir") or die "Copy $file failed";
#    }
    
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

sub main{
 
    print "First we evaluate the original model\n\n";
    run_mecab_evaluate($TestFileDir,"${OldDir}/${OldVers}");

    my @OldDicConfFPs=glob("${OldModelDir}/*");
    
    print "\nCopying/creating config and dic files for a new model build\n";

    if (! -e $TrainCorpus){
	my @Corpora=glob("${AddCorpusDir}/*.mecab");
	if (@Corpora){
	    merge_corpora(@Corpora) or die;
	}
    }


    prepare_files(@OldDicConfFPs);

    my @CRTgts=glob("$AddSeedDir/*.csv");
    push(@CRTgts,$TrainCorpus);

    remove_crs_files(@CRTgts);

    my $MecabLogFP="${AddDir}/mecab-train-${CombVers}.log";

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
	my $SysReturnTrain=system("mecab-cost-train -M $OldModelFile -d $AddSeedDir $TrainCorpus $CombModelFile >> $MecabLogFP 2>&1");
	ifnosucess_fail($SysReturnTrain,"Retraining ");
    }else{
	print "\nThis run skips retraining (dic only)\n";
    }

    if ($TrainP eq "false"){
	$CombModelFile=$OldModelFile;
    }
    
    print "\nRe-building index (this may also take time) ...\n";
    my $SysReturnDicGen=system("mecab-dict-gen -m $CombModelFile -d $AddSeedDir -o $CombModelDir >> $MecabLogFP 2>&1");

    ifnosucess_fail($SysReturnDicGen,"New dictionary creation");


     
    my $SysReturnDicReind=system("mecab-dict-index -d $CombModelDir -o $CombModelDir >> $MecabLogFP 2>&1");

    ifnosucess_fail($SysReturnDicReind,"New dic indexing");

    print 'Congrats, new combined model re-built (retraining finished)';
    sleep(2);

    print "\nNow we evaluate the new model (fingers crossed)\n";
    run_mecab_evaluate($TestFileDir,"${AddDir}/${CombVers}");

    print "\nCleaning files to finish up\n";
    final_clean(@OldDicConfFPs,$CombVersDir);

    print "Everything is done!!\n\n"

}

main;


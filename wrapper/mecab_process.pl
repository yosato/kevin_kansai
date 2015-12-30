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

my $Usage='mecab_process.pl [original_dir] [original_model] [additional_dir] [additional_model] [testfile_dir] <retrain-or-not, 1 or 0> <eval-only, 1 or 0>';


my $Debug=1;


# checking the args
if (@ARGV<5){
    print "ERROR: You need at least five arguments\n" . $Usage . "\n";
    exit;
}

my $HomeDir;
my $Repo;
use Config;

# some globals

# the var for home dir different between win/lin
if ( $Config{osname} eq "windows") {
    $HomeDir="$ENV{HOMEDIR}/$ENV{HOMEPATH}";
    $Repo="$HomeDir/kevin_kansai";
} else {
    $HomeDir='/Users/yosato';
    $HomeDir=$ENV{HOME};
    $Repo="$HomeDir/myProjects/kevin_kansai";
}

my $EvalProg="${Repo}/myPythonLibs/mecabtools/eval_mecab.py";

my $OldDir=$ARGV[0];
my $OldVers=$ARGV[1];

# 'add' is for additional, what you're trying to add
my $AddDir=$ARGV[2];
my $AddVers=$ARGV[3];
my $TestFileDir=$ARGV[4];
my $TrainP=$ARGV[5];
my $EvalOnlyP=$ARGV[6];

my $TestSentsWest="${TestFileDir}/test_sentences_kansai.txt";
my $TestSentsStd="${TestFileDir}/test_sentences_standard.txt";
my $SolutionsWest="${TestFileDir}/solutions_kansai.mecab";
my $SolutionsStd="${TestFileDir}/solutions_standard.mecab";

my $OldModelDir="${OldDir}/${OldVers}/model";
my $OldModelFile="${OldModelDir}/model_${OldVers}.mod";

my $AddSeedDir="${AddDir}/${AddVers}/seed";
my $AddCorpusDir="${AddDir}/${AddVers}/corpus";

my $TrainCorpusFN="corpus_train_${AddVers}.mecab";
my $TrainCorpus="${AddCorpusDir}/${TrainCorpusFN}";

my $CombVers=$OldVers . '_' . $AddVers;
my $CombVersDir="${AddDir}/${CombVers}";
my $CombModelDir="${CombVersDir}/model";

my $CombModelFile="${CombModelDir}/model_${AddVers}";

my $MecabLogFP="${AddDir}/mecab-train-${CombVers}.log";


# just for checking existence of required files and dirs
my @PriorFiles=($OldModelFile,$AddSeedDir,$TestSentsWest,$TestSentsStd,$SolutionsWest,$SolutionsStd);

foreach my $File (@PriorFiles) {
    if (! -e $File){
	print "\n$File does not exist\n";
	exit;
    }
}

# some major functions

sub prepare_files{
    use File::Basename;
    use File::Copy;

    my ($AddDics,$TrainCorpora,$OldDicConfFPs)=@_;

    print "copying original files...\n";
    # first copy the original dics to the seed dir
    for my $file (@$OldDicConfFPs) {
        copy("$file","$AddSeedDir") or die "Copy $file failed";
    }

    print "resetting parameters in dics...\n";
    # replace paras of dic lines to zero
    for my $file (@$AddDics){
	my $Tmp=$file . '.aaa';
	open(FHw, '>', );
	open(FHr,'<', $file);
	while (my $Line=<FHr>){
	    # !!! well this doesnt seem to do subs
	    $Line =~ s/,[0-9]+,[0-9]+,-?[0-9]+,/,0,0,0,/;
	    print FHw $Line;
	}
	close(FHw);
	close(FHr);
	copy($Tmp, $file);
	unlink $Tmp
    }

    print "merging corpus...\n";
    my @Corpora;
    for my $Corpus (@$TrainCorpora){
	if (basename($Corpus) ne $TrainCorpusFN){
	    push (@Corpora,$Corpus); 
	}
    }

    if (@Corpora){
	merge_corpora(\@Corpora,$TrainCorpus) or die;
    }

    my @AllRelFiles;
    push(@AllRelFiles,$TrainCorpus);
    push(@AllRelFiles,@$AddDics);

    remove_crs_files(@AllRelFiles);
}


sub ifnosuccess_fail{
    my ($RetVal,$Operation,$LogFP)=@_;
    if ($RetVal!=0){
	my $FailMess="\n${Operation} failed\n";
	open(FHw, '>>', $LogFP); 
	print FHw $FailMess;
	close(FHw);
	die "\n${Operation} failed\n";
    } else {
	print "\n${Operation} succeeded\n";
	return 1;
    }
}

sub merge_corpora{
    my ($Corpora,$DstFP)=@_;

    open(FHw, '>',$DstFP);
    foreach my $Corpus (@$Corpora){
	open(FHr,'<', $Corpus);
	while (<FHr>){
	    print FHw $_;
	}
	close(FHr);
	    }
    close(FHw);

}

sub run_mecab_evaluate{
    my ($TestFileDir,$ModelRtDir,$MecabLogFP)=@_;
    
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
    ifnosuccess_fail($SysReturnMecab1,"Kansai model mecab",$MecabLogFP);

    my $MecabCmdStd="mecab -d $ModelDir $TestSentsStd > $ResultFileStd";    
    my $SysReturnMecab2=system($MecabCmdStd);
    ifnosuccess_fail($SysReturnMecab2,"Standard model mecab",$MecabLogFP);

    #=== this is an ad hoc addition by ys to avoid k's prob of CRs, but we should investigate where they come from
    
    remove_crs_files(($ResultFileStd,$ResultFileWest));
    #==================================

    print 'Evaluating Kansai model';
    my $KansaiEvalCmd="python3 $EvalProg $ResultFileWest $SolutionsWest";
    my $SysReturnEval1=system("$KansaiEvalCmd > $ScoreFile");
    if ($Debug){print "$KansaiEvalCmd $SysReturnEval1";}
    ifnosuccess_fail($SysReturnEval1,"Kansai model evaluation",$MecabLogFP);
    print 'Evaluating standard model';
    my $StdEvalCmd="python3 $EvalProg $ResultFileStd $SolutionsStd";
    my $SysReturnEval2=system("$StdEvalCmd >> $ScoreFile");
    ifnosuccess_fail($SysReturnEval1,"Standard model evaluation",$MecabLogFP);

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

sub cmd_withredir{
    my ($Cmd,$Debug,$FstTime,$LogFP)=@_;
    my $Tee;
    my $Redir;
    if ($Debug){
	$Tee=' | tee ';
	if (! $FstTime){
	    $Tee="${Tee} -a";
	}
    } else {
	$Tee='';
    }
    if ($Debug){
	    $Redir=''
	}elsif($FstTime){
	    $Redir='>';
        }else{
	   $Redir='>>';
        }
    return "${Cmd} ${Tee} ${Redir} ${LogFP} 2>&1";
    
}
sub mecab_process{

    print "\nGenerating the original dic index\n";
    my $CmdDicInd=cmd_withredir("mecab-dict-index -d $AddSeedDir -o $AddSeedDir ",$Debug,1,$MecabLogFP);
    my $SysReturnDicInd=system($CmdDicInd);
    
    ifnosuccess_fail($SysReturnDicInd,"Orig dic indexing",$MecabLogFP);
    
    print "\nNow the re-training has started (this may take time) ...\n";
    
    mkdir_ifnotexists($CombVersDir);
    unless (mkdir_ifnotexists($CombModelDir)){
	die ("mkdir failed for $CombModelDir\n");
    }

    if ($TrainP eq 'true' || $TrainP eq ""){
	my $CmdRetrain=cmd_withredir("mecab-cost-train -M $OldModelFile -d $AddSeedDir $TrainCorpus $CombModelFile",$Debug,0,$MecabLogFP);
	print $CmdRetrain;
	my $SysReturnTrain=system($CmdRetrain);
	#print $SysReturnTrain;
	ifnosuccess_fail($SysReturnTrain,"Retraining",$MecabLogFP);
    }else{
	print "\nThis run skips retraining (dic only)\n";
    }

    if ($TrainP eq "false"){
	$CombModelFile=$OldModelFile;
    }
    
    print "\nRe-building index (this may also take time) ...\n";
    my $SysReturnDicGen=system("mecab-dict-gen -m $CombModelFile -d $AddSeedDir -o $CombModelDir >> $MecabLogFP 2>&1");

    ifnosuccess_fail($SysReturnDicGen,"New dictionary creation",$MecabLogFP);
     
    my $SysReturnDicReind=system("mecab-dict-index -d $CombModelDir -o $CombModelDir >> $MecabLogFP 2>&1");

    ifnosuccess_fail($SysReturnDicReind,"New dic indexing",$MecabLogFP);

    print 'Congrats, new combined model re-built (retraining finished)';
    sleep(2);
}

sub main{

    # 1. preparing stuff =======================

    my @OldDicConfFPs=glob("${OldModelDir}/*");
 
    print "First we evaluate the original model\n\n";
    
    run_mecab_evaluate($TestFileDir,"${OldDir}/${OldVers}");

    if (! $EvalOnlyP){
	
    print "\nCopying/creating config and dic files for a new model build\n";

    my @TrainCorpora=glob("${AddCorpusDir}/*.mecab");
    my @AddDics=glob("$AddSeedDir/*.csv");
    
    prepare_files(\@AddDics,\@TrainCorpora,\@OldDicConfFPs);


    # 2 the main stuff =========================
    
    print "the main process starting...";
    
    mecab_process;

    }
    
    # 3 evaluating and finishing up =============

    print "\nNow we evaluate the new model (fingers crossed)\n";
    
    run_mecab_evaluate($TestFileDir,"${AddDir}/${CombVers}");

    print "\nCleaning files to finish up\n";
    
    final_clean(@OldDicConfFPs,$CombVersDir);

    print "Everything is done!!\n\n"

}


main;


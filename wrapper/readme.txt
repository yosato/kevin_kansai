Usage: mecab_process.pl <RootDir> <OldModel> <NewModel> <'true' or 'false'>

This script derives a new model based on an older model and evaluates it using the test and training files provided as described below. You can produce either a re-trained model or a lexical-addition-only model.

<RootDir> must contain two immediate subdirectories of the names <OldModel> and <NewModel>. Based on the files in the <OldModel> the script creates the new model under <NewModel>. The last (4th) argument indicates if you want a re-trained model.

Each directory (Root, Old and New) must contain the 'ingredients' as follows:

RootDir must contain four test sentence files for evaluation (with these names):

<RootDir>--- test_sentences_kansai.txt
	  |- solutions_kansai.mecab
	  |- test_sentences_standard.txt
	  |- solutions_standard.mecab

which are used as the golden standard in the evaluations as described at the end of this document. The first and the third are raw texts (kansai and standard), the second and fourth are the mecab-formatted gold standards (solutions) of the first and the third respectively.

<RootDir>---<OldModel>--- model --- model_<OldModel>
			         |- (other files for running mecab -d: def files, dic csv's etc)

OldModel dir must contain a subdirectory called model, which must then contain the old model files, including the binary parameter file called model_<OldModel>. This is the model you start from. It needs to be mecab-ready: you should already be able to run mecab -d <OldDir>.

Finally, <NewModel> dir must contain three directories, 'seed', 'corpus' and 'model. Here the ones that need to be pre-populated are 'seed' and 'corpus' and 'model' dir should be empty first

<RootDir>---<NewModel>--- seed --- (new dic files)
			  corpus --- corpus_train_<NewModel>.mecab 
			  model 

'seed' dir must contain your new dictionaries. 'corpus' dir must contain your training corpus, named corpus_train_<NewModel>.mecab

The process generates new model in the 'model' dir, as well as the new results in the corpus dir. 

Evaluations are run against two sets of gold standards (kansai and standard) at the start and the end of the process respectively: <OldModel> results and <NewModel> results. The evaluation results are outputted to the file called 'scores.txt' in <RootDir> as well as to the standard output.



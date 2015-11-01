Usage: mecab_process.pl <OldModelDir> <OldModel> <AdditionalModelDir> <AdditionalModel> <TestFileDir> <'true' or 'false' for retraining>

This script derives a new model based on an older model plus the dics or corpus provided by the user. It also evaluates the original model and new model on the test corpora provided. Thus, the user needs to provide beforehands

1 new dic or/and new corpus
2 test corpora as well as their solutions

The last argument determines whether you'd like to do the 'full' training with a corpus (default). If false, it only uses a dictionary.

Given the dirs/files provided as below, you get

1 evaluation of the original model
2 re-training with new dics/corpus
3 evaluation of the new (combined) model.

Results are shown on stout as well as stored in 'scores.txt', immediately under <OldModelDir> and <NewModelDir>.

--- How to structure/prepare pre-requisite dirs:

a) Dir structure

A directory with two subdirectories: <RootDir> must contain three immediate subdirectories, <OldModelDir> , <NewModelDir> and <TestFileDir>. Under <OldModelDir> you need a single subdir, 'model', while <NewModelDir> requires two, 'seed' and 'corpus' 

<RootDir>
├── <TestFileDir>
    ├──  test_sentences_<OldModel>.txt
	  |- solutions_<NewModel>.mecab
	  |- test_sentences_<OldModel>.txt
	  |- solutions_<NewModel>.mecab

├── <OldModelDir>
    ├── model
├── <NewModelDir>
    ├── seed
    ├── corpus



├── <OldModelDir>_<NewModelDir>
    ├── model	
			   
b) pupulating files

Each directory (Root, Old and New) must contain the 'ingredients' as follows:

<RootDir> must contain four test sentence files for evaluation (with these names):

<RootDir>---
The first and the third are raw texts (old and new model targets), the second and fourth are the mecab-formatted gold standards (solutions) of the first and the third respectively.

<OldModel> dir must contain a subdirectory called model, which must then contain the old model files, including the binary parameter file called model_<OldModel>. This is the model you start from. It needs to be mecab-ready: you should already be able to run mecab -d <OldDir>.

<RootDir>---<OldModel>--- model --- model_<OldModel>
			         |- (other files for running mecab -d: def files, dic csv's etc)

Finally, <NewModel> dir must contain two directories, 'seed' and 'corpus', which should respectively contain your new dics and your new corpus (that needs to be named as below.)

<RootDir>---<NewModel>--- seed --- (new dic files)
			  corpus --- corpus_train_<NewModel>.mecab 


The process generates new model in a new dir inder <RootDir> named <OldModel>_<NewModel>. 

This new model is used for evaluation at the end of the process.

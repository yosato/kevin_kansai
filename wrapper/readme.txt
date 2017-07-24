Usage: mecab_process.pl <OldModelDir> <OldModel> <AddModelDir> <AddModel> <TestFileDir> <'true' or 'false' for retraining>

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

Three dirs are required, <OldModelDir> , <AddModelDir> and <TestFileDir>, all of which may be independently located. Under <OldModelDir> you need a single subdir, 'model', while <NewModelDir> requires two, 'seed' and 'corpus'. <TestFileDir> must contain four files, those of test sentences and their solution parses for each target.

├── <OldModelDir>
    └── model

├── <AddModelDir>
    ├── seed
    └── corpus

├── <TestFileDir>


b) pupulating files

Each directory must contain the 'ingredients' as follows:

<TestFileDir> must contain four test sentence files for evaluation (with these names):

<TestFileDir>
    ├── test_sentences_<OldModel>.txt
    ├── solutions_<AddModel>.mecab
    ├──	test_sentences_<OldModel>.txt
    └──	solutions_<AddModel>.mecab


The first and third are raw texts (old and new model targets), the second and fourth are the mecab-formatted gold standards (solutions) of the first and the third respectively.

<OldModel>'s subdirectory, model, must then contain the old model files, including the binary parameter file called model_<OldModel>. This is the model you start from. It needs to be mecab-ready: you should already be able to run mecab -d <OldDir>/model.

Finally, <AddModel> dir's two subdirectories, 'seed' and 'corpus', should respectively contain your new dics and your new corpus (that needs to be named as below.)

<AddModelDir>
    ├── seed
    │	└── (new dic files)
    └── corpus
    	└── corpus_train_<NewModel>.mecab 


The process generates new combined model in a new dir inder <RootDir> named <OldModel>_<NewModel>/model. 

├── <OldModel>_<AddModel>
    └── model
    
This new model is used for evaluation at the end of the process.

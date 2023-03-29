import commune

class Launchpad(commune.Module):
    
    
    @classmethod
    def train(cls, models=[f'model::gptj::{i}' for i in [0]], 
              datasets=['dataset::bittensor']):
        
        model_module = commune.get_module('model.transformer')
        for model in models:
            for dataset in datasets:
                model_module.launch(fn='remote_train',name=f'train::{model}', kwargs={'model': model, 'dataset': dataset, 'save': True}, serve=False)
    
    
    @classmethod
    def deploy_fleet(module='model.transformer'):
        module_class = commune.get_module(mode)
        module_class.deploy_fleet()
    
    @classmethod
    def deploy_models(cls):
        '''
        ArXiv/            Gutenberg_PG/
        BookCorpus2/      HackerNews/
        Books3/           NIHExPorter/
        DMMathematics/    OpenSubtitles/
        '''
        cls.deploy_fleet(module='model.transformer')

    @classmethod
    def deploy_datasets(cls):
        '''
        ArXiv/            Gutenberg_PG/
        BookCorpus2/      HackerNews/
        Books3/           NIHExPorter/
        DMMathematics/    OpenSubtitles/
        '''
        dataset_module = cls.deploy_fleet('dataset.text.huggingface')
        
        
if __name__ == "__main__":
    Launchpad.run()
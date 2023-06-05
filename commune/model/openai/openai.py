import openai
import os
import torch
from typing import Union, List, Any, Dict
import commune as c
import json
# class OpenAILLM(c.Module):


class OpenAILLM(c.Module):
    
    
    
    def __init__(self,
                model: str = "text-davinci-003",
                prompt: str = None,
                temperature: float=0.9,
                max_tokens: int=1000,
                top_p: float=1.0,
                frequency_penalty: float=0.0,
                presence_penalty: float=0.0,
                tokenizer: str = None,
                api: str = 'OPENAI_API_KEY',
                stats:dict = None
                ):
        
        self.set_config(kwargs=c.locals2kwargs(locals()))
        self.set_api(api=api)
        self.set_prompt(prompt)
        self.set_tokenizer(tokenizer)
        self.set_stats(stats)
        
        self.params  = dict(
                 model =model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
        )
        
        
     
    def set_stats(self, stats):
        if stats == None:
            stats = {}
        assert isinstance(stats, dict)
        self.stats = stats 
        
    def set_api(self, api: str = None) -> None:
        openai.api_key = os.getenv(api, api)

        
    def resolve_prompt(self, prompt=None, **kwargs):
        if prompt == None:
            prompt = self.prompt
        for var in self.prompt_variables:
            assert var in kwargs
        assert isinstance(prompt, str)
        prompt = prompt.format(**kwargs)
        return prompt
    
    
    def resolve_params(self, params=None, **kwargs):
        if params == None:
            params = self.params
        elif isinstance(params, dict):
            params = {**params, **kwargs}
        return params
    
        
    prompt = """
        Return the following response to the Question as a JSON Dictionary
        Q (str):
        {x}
        A (JSON):
        """

        
    def forward(self,
                *args,
                params = None,
                prompt:str=None,
                choice_idx:int = 0,
                **kwargs) -> str:
        if len(args) > 0 :
            assert len(args) == len(self.prompt_variables), f"Number of arguments must match number of prompt variables: {self.prompt_variables}"
            kwargs = dict(zip(self.prompt_variables, args))
            
        params = self.resolve_params(params)
        if prompt == None:
            prompt = self.resolve_prompt(**kwargs)
        c.print(prompt)
        c.print(openai)
        response = openai.Completion.create(
            prompt=prompt, 
            **params
        )
        
        
        # update token stats
        for k,v in response['usage'].items():
            self.stats[k] = self.stats.get(k, 0) + v
        
        response =  response['choices'][choice_idx]['text']
        if c.jsonable(response):
            response = json.loads(response)
            
        return response
                
    
    
    def set_prompt(self, prompt: str):
        
        if prompt == None:
            prompt = self.prompt
        self.prompt = prompt
        assert isinstance(self.prompt, str), "Prompt must be a string"
        self.prompt_variables = self.get_prompt_variables(self.prompt)

    @staticmethod   
    def get_prompt_variables(prompt):
        variables = []
        tokens = prompt.split('{')
        for token in tokens:
            if '}' in token:
                variables.append(token.split('}')[0])
        return variables
    
        

    @classmethod
    def test(cls, **params:dict):
        
        
        
        model = cls(**params)
        cls.print(model.__dict__)
         

    def set_tokenizer(self, tokenizer: str):

        if tokenizer == None and hasattr(self, 'tokenizer'):
            return self.tokenizer
             
        if tokenizer == None:
            tokenizer = 'gpt2'
        from transformers import AutoTokenizer

        if isinstance(tokenizer, str):
            try:
                tokenizer = AutoTokenizer.from_pretrained(tokenizer, use_fast= True)
            except ValueError:
                print('resorting ot use_fast = False')
                tokenizer = AutoTokenizer.from_pretrained(tokenizer, use_fast=False)
        
        tokenizer.pad_token = tokenizer.eos_token 
            
        self.tokenizer = tokenizer
        
        
        return self.tokenizer
    
    
    def decode_tokens(self,input_ids: Union[torch.Tensor, List[int]], **kwargs) -> Union[str, List[str], torch.Tensor]:
        return self.tokenizer.decode(input_ids, **kwargs)
    def encode_tokens(self, 
                 text: Union[str, List[str], torch.Tensor], 
                 return_tensors='pt', 
                 padding=True, 
                 truncation=True, 
                 max_length=256,
                 **kwargs):
        
        return self.tokenizer(text, 
                         return_tensors=return_tensors, 
                         padding=padding, 
                         truncation=truncation, 
                         max_length=max_length)
    @classmethod
    def test(cls, question = '''
            convert this into a yaml

             model: str = "text-davinci-003",
                prompt: str = None,
                temperature: float=0.9,
                max_tokens: int=1000,
                top_p: float=1.0,
                frequency_penalty: float=0.0,
                presence_penalty: float=0.0,
                tokenizer: str = None,
                api: str = 'OPENAI_API_KEY',
                stats:dict = None
             '''):
        model = cls()
        print(model.forward(question))
            






if __name__ == '__main__':
    OpenAILLM.run()


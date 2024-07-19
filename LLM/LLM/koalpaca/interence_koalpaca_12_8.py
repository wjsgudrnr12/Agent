import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
from transformers.generation import GenerationConfig

from models import *
from module_manager import classregistry

@classregistry.register('koalpaca_12_8', )
class Koalpach_12_8_LLMModel:
    def __init__(self, name):
        self.name = name
        self.model = None
        self.tokenizer = None
        self.gen_cfg = None

    #    self.modelinit()

    def init(self): 
        print("model initializing....")   
        peft_model_id = "hyungkook/koalpaca-polyglot-12.8b-jun"

        config = PeftConfig.from_pretrained(peft_model_id)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path,
                                                    quantization_config=bnb_config,
                                                    device_map='auto')

        model = PeftModel.from_pretrained(model, peft_model_id)
        tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

        model.eval()

        gen_cfg = GenerationConfig.from_model_config(model.config)
        gen_cfg.pad_token_id = tokenizer.eos_token_id
        
        gen_cfg.temperature = 0.3
        gen_cfg.max_new_tokens = 128

        self.model = model
        self.tokenizer = tokenizer
        self.gen_cfg = gen_cfg

        return "LLM loading OK"


    def gen(self,x):
        gened = self.model.generate(
            **self.tokenizer(
                f"User: {x}\n\nAssistant:",
                return_tensors='pt',
                return_token_type_ids=False
            ).to('cuda'),
            do_sample=True,
            generation_config=self.gen_cfg
        )
        result = self.tokenizer.decode(gened[0])
        answer = result.split('Assistant:')

        print(answer[1].strip())

        return answer[1].strip()





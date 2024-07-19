from dotenv import load_dotenv
import os

import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer
import transformers
from datasets import load_dataset

from peft import prepare_model_for_kbit_training
from peft import LoraConfig, get_peft_model

from huggingface_hub import HfApi

import locale

# nvidia check
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.current_device())
print(torch.cuda.get_device_name(torch.cuda.current_device()))

# get a model
model_id = "beomi/polyglot-ko-12.8b-safetensors"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
# model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map={"":0})
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map="auto")

# get training data
data = load_dataset("csv", data_files={"train":"the-age-of-AI-has-begun.csv"})
#data = load_dataset("csv", data_files={"train":"test.csv"})
#rows = [row for row in data["train"]]

data = data.map(
    lambda x: {
        'text': f"""User: {x['instruction']}
        Assistant: {x['output']}<|endoftext|>""" }
)

# get tokenied data
tokenizer = AutoTokenizer.from_pretrained(model_id)
data = data.map(lambda samples: tokenizer(samples["text"]), batched=True)
#print(data["train"][0]["input_ids"])

# peft model setting
model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["query_key_value"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, config)

# output training parameters
trainable_params = 0
all_param = 0
for _, param in model.named_parameters():
    all_param += param.numel()
    if param.requires_grad:
        trainable_params += param.numel()

print(f"""trainable params: {trainable_params}
all params: {all_param}
trainable%: {100 * trainable_params / all_param}""")

# model training
tokenizer.pad_token = tokenizer.eos_token

trainer = transformers.Trainer(
    model=model,
    train_dataset=data['train'],
    args=transformers.TrainingArguments(
        max_steps=100, # 100 step 학습시, V100 기준 약 2분 소요
        per_device_train_batch_size=2,
        gradient_accumulation_steps=1,
        learning_rate=1e-4,
        fp16=True,
        output_dir="outputs",
        optim="paged_adamw_8bit",
        logging_steps=25,
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

model.config.use_cache = False
trainer.train()

# model evaluation
model.eval()
model.config.use_cache = True

from transformers.generation import GenerationConfig

gen_cfg = GenerationConfig.from_model_config(model.config)
gen_cfg.pad_token_id = tokenizer.eos_token_id

def gen(x):
    gen_cfg.temperature = 0.3
    gen_cfg.max_new_tokens = 128

    gened = model.generate(
        **tokenizer(
            f"User: {x}\n\nAssistant:",
            return_tensors='pt',
            return_token_type_ids=False
        ).to('cuda'),
        do_sample=True,
        generation_config=gen_cfg
    )

    return tokenizer.decode(gened[0])

# test fine-tunned model
print(gen('1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?'))

# check huggingface login 
load_dotenv()

api = HfApi()
huggingfacetoken = os.getenv('HUGGINGFACE_TOKEN')
user = api.whoami(huggingfacetoken)
print(user)

# upload model to huggingface
locale.getpreferredencoding = lambda: "UTF-8"
model.push_to_hub('hyungkook/koalpaca-polyglot-12.8b-jun')


# upload local model to huggingface 
# from transformers import AutoModel

# model_path = "outputs/checkpoint-100"
# model = AutoModel.from_pretrained(model_path)
# model.push_to_hub('hyungkook/koalpaca-polyglot-12.8b-jun')
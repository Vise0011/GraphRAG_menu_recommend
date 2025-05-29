# app/llama/model_runner.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_PATH = "app/llama/Llama-3.1-8B-Instruct"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16).to("cuda")

def generate_text(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=200)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

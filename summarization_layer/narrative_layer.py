import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, Optional

class MockLLM:
    def __init__(self):
        model_id = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.llm = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=torch.float16,
            device_map="auto"
        )

    def generate(self, deterministic_summary: str, facts: dict) -> str: 
        sys_prompt = (
            "You are a strict data-to-text editor for a corporate dashboard. "
            "Your only job is to rewrite the provided summary to sound slightly more natural. "
            "CRITICAL RULES: "
            "1. You must NEVER add, change, or invent any number, name, or fact. "
            # "2. Keep the output extremely concise. "
            # "3. Do not include introductory or conversational filler text."
        )

        user_prompt = (
            f"Raw Facts: {facts}\n"
            f"Original Summary: {deterministic_summary}\n\n"
            f"Polished Summary:"
        )

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": user_prompt}
        ]

        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.llm.device)

        with torch.no_grad():
            outputs = self.llm.generate(**model_inputs, max_new_tokens=256, do_sample=False)

        input_length = model_inputs.input_ids.shape[1]
        response = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True).strip()

        return response 


local_model_instance = None

def polish(deterministic_summary: str, facts: dict, llm_callable: Optional[Callable] = None) -> Optional[str]:
    global local_model_instance

    if not llm_callable:
        if local_model_instance is None:
            print("Loading Qwen 1.5B")
            local_model_instance = MockLLM()
            
        llm_callable = local_model_instance.generate
        
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(llm_callable, deterministic_summary, facts)
            result = future.result(timeout=3.0) 
            return str(result) if result else None
            
    except (TimeoutError, Exception):
        return None
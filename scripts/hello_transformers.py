from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import os

path = "./models/gpt-oss-20b"

tok = AutoTokenizer.from_pretrained(path, local_files_only=True)

model = AutoModelForCausalLM.from_pretrained(
    path,
    dtype="auto",              # new arg name (replaces torch_dtype)
    device_map="auto",         # needs 'accelerate' installed
    low_cpu_mem_usage=True,
    local_files_only=True
)

streamer = TextStreamer(tok)
prompt = "You are a cautious first-aid helper. An adult has a shallow forearm cut. Give brief, safe first-aid steps only."
ids = tok.apply_chat_template(
    [{"role":"user","content":prompt}],
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

_ = model.generate(ids, max_new_tokens=160, temperature=0.2, streamer=streamer)

from huggingface_hub import login

# Log in using your Hugging Face token
login(token="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")

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meta-llama/CodeLlama-7b-Instruct-hf"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    low_cpu_mem_usage=True,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompt = " You are an agent expert in data science and SQL.Your are tasked with increasing the complexity of a given SQL query template by inspiring from a sample tutorial document for Oracle SQL. A query template is defined as a SQL query with placeholders for columns, tables, and literals.  For each template, you will be provided with: 1.  SQL keywords and functions. 2.  column or alias.column which is a placeholder for a column name. 3.  table which is a placeholder for a table name. 4.  literal which is a placeholder for a literal value that can be a string, number, or date."
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(response)
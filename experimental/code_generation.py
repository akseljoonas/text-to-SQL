from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Load the tokenizer and model
model_name = "meta/code-llama-7b"  # You can also use "code-llama-13b" or larger models if your system can handle it
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Create a pipeline for text generation (code generation)
generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=-1)  # device=-1 for CPU, change to 0 if using GPU

# Example prompt for code generation
prompt = "def fibonacci(n):"

# Generate code
output = generator(prompt, max_length=100)

# Print generated code
print(output[0]['generated_text'])
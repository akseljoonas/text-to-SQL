import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, Trainer, TrainingArguments
dataset = load_dataset('json', data_files='/Users/mikaumana/Downloads/dataset.json')
tokenizer = AutoTokenizer.from_pretrained("stabilityai/stable-code-3b")
train_dataset = dataset.train_test_split(test_size=0.1)["train"]
eval_dataset = dataset.train_test_split(test_size=0.1)["test"]

model = AutoModelForCausalLM.from_pretrained("stabilityai/stable-code-3b")

def formatting_prompts_func(train_dataset):
  output_texts = []
  for i in range(len(training_dataset['question'])):
    question = training_dataset['question'][i]
    query = training_dataset['SQL'][i]
    database_schema = training_dataset['database_schema'][i]
    user_message = f"""Given the following SQL tables, your job is to generate the Sqlite SQL query given the user's question.
Put your answer inside the ```sql and ``` tags.
{database_schema}
###
Question: {question}

```sql
{query} ;
```
<|EOT|>
"""
    output_texts.append(user_message)
  return output_texts



# Set up training arguments
training_args = TrainingArguments(
    output_dir="./results",          # Output directory
    evaluation_strategy="epoch",     # Evaluation strategy (per epoch)
    learning_rate=5e-5,              # Learning rate
    per_device_train_batch_size=4,   # Batch size for training
    per_device_eval_batch_size=4,    # Batch size for evaluation
    num_train_epochs=3,              # Number of epochs
    weight_decay=0.01,               # Weight decay
    logging_dir="./logs",            # Directory for logs
    save_total_limit=3,              # Number of model checkpoints to save
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=output_texts['train'],  # Training dataset
    eval_dataset=tokenized_datasets['test'],    # Evaluation dataset (if applicable)
)

# Start training
trainer.train()
trainer.save_model("/Users/mikaumana/Downloads")

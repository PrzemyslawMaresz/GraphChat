import os
import json
from PIL import Image
from tqdm import tqdm
import torch
from torch.utils.data import Dataset
from transformers import (
    Blip2Processor,
    Blip2ForConditionalGeneration,
    TrainingArguments,
    Trainer
)

DATA_ROOT = "test_images"
MODEL_ID = "Salesforce/blip2-flan-t5-xl"

processor = Blip2Processor.from_pretrained(MODEL_ID)
model = Blip2ForConditionalGeneration.from_pretrained(MODEL_ID, device_map="auto")

from transformers import Trainer

class CustomTrainer(Trainer):
    def __init__(self, *args, tokenizer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = tokenizer

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)),
            labels.view(-1),
            ignore_index=self.tokenizer.pad_token_id
        )
        return (loss, outputs) if return_outputs else loss

def create_prompt(entry):
    chart_type = entry.get("type", "bar")
    points = entry.get("points", [])
    if len(points) < 3:
        return None, None
    x_val = points[2]["x"]
    y_val = points[2]["y"]
    if chart_type == "bar":
        return f"What is the y value for x = {x_val} in the bar chart?", str(y_val)
    elif chart_type == "line":
        return f"What is the y value for x = {x_val} on the line?", str(round(y_val, 2))
    elif chart_type == "scatter":
        return f"What is the y value of the point closest to x = {x_val}?", str(round(y_val, 2))
    return None, None

class ChartImageDataset(Dataset):
    def __init__(self, folder):
        self.samples = []
        type_to_metadata = {
            "bar_charts": "bar_metadata.jsonl",
            "line_poly_charts": "line_poly_metadata.jsonl",
            "scatter_charts": "scatter_metadata.jsonl"
        }
        for chart_type, metadata_file in type_to_metadata.items():
            type_dir = os.path.join(folder, chart_type)
            metadata_path = os.path.join(type_dir, metadata_file)
            if not os.path.exists(metadata_path):
                continue
            with open(metadata_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    image_path = os.path.join(type_dir, entry["id"] + ".png")
                    if not os.path.exists(image_path):
                        continue
                    entry["type"] = chart_type.split("_")[0]
                    prompt, answer = create_prompt(entry)
                    if prompt and answer:
                        self.samples.append({
                            "image_path": image_path,
                            "prompt": prompt,
                            "answer": answer
                        })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        image = Image.open(item["image_path"]).convert("RGB")
        return {
            "image": image,
            "prompt": item["prompt"],
            "answer": item["answer"]
        }

class Blip2Collator:
    def __init__(self, processor):
        self.processor = processor

    def __call__(self, batch):
        images = [item["image"] for item in batch]
        prompts = [item["prompt"] for item in batch]
        answers = [item["answer"] for item in batch]

        inputs = self.processor(images=images, text=prompts, padding="longest", return_tensors="pt")

        labels = self.processor.tokenizer(answers, padding="longest", return_tensors="pt").input_ids

        decoder_input_ids = labels.clone()
        decoder_input_ids[:, 1:] = labels[:, :-1]
        decoder_input_ids[:, 0] = self.processor.tokenizer.pad_token_id

        inputs["labels"] = labels
        inputs["decoder_input_ids"] = decoder_input_ids

        return inputs

dataset = ChartImageDataset(DATA_ROOT)
print(f"Loaded {len(dataset)} multimodal examples.")

training_args = TrainingArguments(
    output_dir="./finetuned-blip2",
    per_device_train_batch_size=1,  # CPU-friendly
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=500,
    save_total_limit=2,
    remove_unused_columns=False
)

trainer = CustomTrainer(
    tokenizer=processor.tokenizer,
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=Blip2Collator(processor)
)

trainer.train()

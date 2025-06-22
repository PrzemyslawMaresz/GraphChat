import numpy as np
import matplotlib.pyplot as plt
import json
import os
from uuid import uuid4
import random

# Output directory
output_dir = "../test_images_2/bar_charts"
os.makedirs(output_dir, exist_ok=True)

# Parameters
num_charts = 20
noise_std = 3.5

# Store metadata
metadata = []

for i in range(num_charts):
    # Random number of bars
    num_bars = random.randint(10, 30)

    # Generate x positions and base y values
    x = np.arange(num_bars)
    y_base = np.random.uniform(10, 60, size=num_bars)
    y_noise = np.random.normal(0, noise_std, size=num_bars)
    y_shift = np.random.uniform(10, 40)
    y = y_base + y_noise + y_shift

    # Chart ID and file path
    chart_id = str(uuid4())
    filename = f"{chart_id}.png"
    img_path = os.path.join(output_dir, filename)

    # Generate bar chart
    plt.figure(figsize=(8, 4))
    plt.bar(x, y, color="steelblue", alpha=0.9)
    plt.title(f"Bar Chart #{i+1}")
    plt.xlabel("Category Index")
    plt.ylabel("Value")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()

    # Save metadata
    metadata.append({
        "id": chart_id,
        "num_bars": num_bars,
        "y_shift": round(y_shift, 2),
        "image": img_path,
        "points": [{"x": int(xi), "y": round(float(yi), 2)} for xi, yi in zip(x, y)]
    })

# Save to JSONL
jsonl_path = os.path.join(output_dir, "bar_metadata.jsonl")
with open(jsonl_path, "w") as f:
    for entry in metadata:
        f.write(json.dumps(entry) + "\n")

print(f"Generated {num_charts} noisy bar charts in: {output_dir}")
print(f"Metadata file saved as: {jsonl_path}")

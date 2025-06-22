import numpy as np
import matplotlib.pyplot as plt
import json
import os
from uuid import uuid4
import random

# Create output directory
output_dir = "../test_images_2/scatter_charts"
os.makedirs(output_dir, exist_ok=True)

# Parameters
num_charts = 20
noise_std = 1.5

# Define base functions
base_functions = {
    "sin": lambda x: np.sin(x) * 10,
    "cos": lambda x: np.cos(x) * 15,
    "linear": lambda x: 5 * x,
    "quad": lambda x: 0.5 * (x - 5) ** 2
}

# Store metadata
metadata = []

for i in range(num_charts):
    # Random number of points
    num_points = random.randint(20, 50)

    # Random x scale
    x_min = np.random.uniform(0, 5)
    x_max = np.random.uniform(10, 20)
    x = np.linspace(x_min, x_max, num_points)

    # Select a base function and generate y with noise
    func_name = np.random.choice(list(base_functions.keys()))
    y_base = base_functions[func_name](x)
    y_noise = np.random.normal(0, noise_std, num_points)
    y = y_base + y_noise

    # Random y-axis shift
    y_shift = np.random.uniform(20, 80)
    y = y + y_shift

    # Chart ID and file name
    chart_id = str(uuid4())
    filename = f"{chart_id}.png"
    img_path = os.path.join(output_dir, filename)

    # Generate and save scatter plot
    plt.figure(figsize=(6, 4))
    plt.scatter(x, y, color="darkblue", alpha=0.8)
    plt.title(f"Scatter Chart #{i+1} ({func_name})")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()

    # Save chart metadata
    metadata.append({
        "id": chart_id,
        "function": func_name,
        "num_points": num_points,
        "x_range": [round(x_min, 2), round(x_max, 2)],
        "y_shift": round(y_shift, 2),
        "image": img_path,
        "points": [{"x": round(float(xi), 2), "y": round(float(yi), 2)} for xi, yi in zip(x, y)]
    })

# Save metadata to JSONL file
jsonl_path = os.path.join(output_dir, "scatter_metadata.jsonl")
with open(jsonl_path, "w") as f:
    for entry in metadata:
        f.write(json.dumps(entry) + "\n")

print(f"Generated {num_charts} noisy scatter charts with 20-50 points in: {output_dir}")
print(f"Metadata file saved as: {jsonl_path}")

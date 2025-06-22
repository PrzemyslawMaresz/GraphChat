import numpy as np
import matplotlib.pyplot as plt
import json
import os
from uuid import uuid4
import random

# Output directory
output_dir = "../test_images_2/line_poly_charts"
os.makedirs(output_dir, exist_ok=True)

# Parameters
num_charts = 20
noise_std = 2.0

# Store metadata
metadata = []

for i in range(num_charts):
    # Random number of points
    num_points = random.randint(20, 30)

    # Random x range
    x_min = np.random.uniform(0, 5)
    x_max = np.random.uniform(10, 20)
    x = np.linspace(x_min, x_max, num_points)

    # Random polynomial degree (1 to 3)
    degree = random.randint(1, 4)
    coeffs = np.random.uniform(-2, 2, size=degree + 1)
    y_base = np.polyval(coeffs, x)

    # Add Gaussian noise and random vertical shift
    y_noise = np.random.normal(0, noise_std, num_points)
    y_shift = np.random.uniform(20, 80)
    y = y_base + y_noise + y_shift

    # Chart ID and image path
    chart_id = str(uuid4())
    filename = f"{chart_id}.png"
    img_path = os.path.join(output_dir, filename)

    # Plot the line chart
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, linestyle='-', color="darkgreen", alpha=0.9)
    plt.title(f"Line/Poly Chart #{i+1} (degree {degree})")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()

    # Save metadata
    metadata.append({
        "id": chart_id,
        "degree": degree,
        "coefficients": [round(float(c), 3) for c in coeffs],
        "num_points": num_points,
        "x_range": [round(x_min, 2), round(x_max, 2)],
        "y_shift": round(y_shift, 2),
        "image": img_path,
        "points": [{"x": round(float(xi), 2), "y": round(float(yi), 2)} for xi, yi in zip(x, y)]
    })

# Save metadata to JSONL
jsonl_path = os.path.join(output_dir, "line_poly_metadata.jsonl")
with open(jsonl_path, "w") as f:
    for entry in metadata:
        f.write(json.dumps(entry) + "\n")

print(f"Generated {num_charts} noisy line/polynomial charts (deg 1–3) in: {output_dir}")
print(f"Metadata saved as: {jsonl_path}")

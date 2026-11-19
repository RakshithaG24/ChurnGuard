
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

results_path = Path("reports/model_comparison.csv")

df = pd.read_csv(results_path)

metrics = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]

print(df.to_string(index=False))

for metric in metrics:
    plt.figure(figsize=(9, 5))
    plt.bar(df["Model"], df[metric])
    plt.title(f"Model Comparison - {metric}")
    plt.ylabel(metric)
    plt.ylim(0, 1)
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(f"reports/comparison_{metric.lower().replace(' ', '_')}.png")
    plt.show()

print("\nComparison charts saved successfully!")

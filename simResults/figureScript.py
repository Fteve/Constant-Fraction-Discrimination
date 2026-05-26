import pandas as pd
import matplotlib.pyplot as plt
import os

# Ask user for CSV filename
csv_file_name = input("Enter CSV filename: ")
csv_file = "./csvFiles/" + csv_file_name + ".csv"

# Check file exists
if not os.path.exists(csv_file):
    print(f"Error: File '{csv_file}' not found.")
    exit()

# Read CSV
data = pd.read_csv(csv_file)

# Create figure
plt.figure(figsize=(8, 5))

# Number of traces
num_traces = len(data.columns) // 2

# Plot all traces
for i in range(num_traces):

    x_col = data.columns[2 * i]
    y_col = data.columns[2 * i + 1]

    # Legend label
    label = y_col.replace(" Y", "")

    plt.plot(
        data[x_col],
        data[y_col],
        label=label
    )

# Labels
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")

# Grid and legend
plt.grid(True)
plt.legend()

# Better spacing
# plt.tight_layout()

# Save output PDF automatically
output_pdf = "./outputFigures/" + os.path.splitext(csv_file_name)[0] + ".pdf"

plt.savefig(output_pdf)

print(f"Saved plot as: {output_pdf}")

# Show plot
# plt.show()
import pandas as pd
import os

x_max_ns = 4  # adjust to your desired cutoff (ns)

csv_file_name = input("Enter CSV filename: ")
csv_file = "./csvFiles/" + csv_file_name + ".csv"

# Check file exists
if not os.path.exists(csv_file):
    print(f"Error: File '{csv_file}' not found.")
    exit()



df = pd.read_csv(csv_file, header=None)

df = df.replace("'", "", regex=True)
# --- FORCE numeric conversion ---
df = df.apply(pd.to_numeric, errors='coerce')

# optional: drop bad rows if any conversion failed
df = df.dropna()

pairs = []


# scale x columns (0,2,4,...)
for col in range(0, df.shape[1], 2):
    x = df[col] * 1e9
    y = df[col + 1] * 1e3

    mask = x <= x_max_ns

    x_trim = x[mask].reset_index(drop=True)
    y_trim = y[mask].reset_index(drop=True)

    pairs.append((x_trim, y_trim))

# pad all traces to same length with NaN
max_len = max(len(x) for x, y in pairs)

out = pd.DataFrame()

for i, (x, y) in enumerate(pairs):
    x = x.reindex(range(max_len))
    y = y.reindex(range(max_len))

    out[2*i] = x
    out[2*i + 1] = y



output_file = "../../csvFiles/" + os.path.splitext(csv_file_name)[0] + "_CLEANED.csv"

name, ext = os.path.splitext(output_file)
i = 1

while os.path.exists(output_file):
    output_file = f"{name}_{i}{ext}"
    i += 1

out.to_csv(output_file, index=False, header=False)

print("Done: converted to ns scale + trimmed")
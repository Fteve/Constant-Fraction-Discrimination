import pandas as pd
import os

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

# scale x columns (0,2,4,...)
for col in range(0, df.shape[1], 2):
    df[col] = df[col] * 1e9

# scale y columns (1,3,5...)
for col in range(1, df.shape[1], 2):
    df[col] = df[col] * 1e3

# --- define cutoff in ns ---
x_max = 10  # your requested cutoff

# --- build mask: keep rows where ALL x-columns are <= cutoff ---
mask = pd.Series(True, index=df.index)

for col in range(0, df.shape[1], 2):
    mask &= df[col] <= x_max

df = df[mask]

output_file = "./csvFiles/" + os.path.splitext(csv_file_name)[0] + "_CLEANED.csv"
df.to_csv(output_file, index=False, header=False)

print("Done: converted to ns scale + trimmed")
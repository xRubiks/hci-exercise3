import json
import matplotlib.pyplot as plt
import numpy as np

# JSON-Datei einlesen
with open('reaction_results_2025-05-17T13-42-59.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Funktion zum Extrahieren von MT- und ID-Werten
def extract_mt_id(run_data):
    MT = []
    ID = []
    for item in run_data:
        if item['ID'] is not None:
            MT.append(item['MT'])
            ID.append(item['ID'])
    return ID, MT

# Leere Listen zur Speicherung aller IDs und MTs
all_ids = []
all_mts = []

for d in data: 
    id, mt = extract_mt_id(d['data'])
    all_ids +=id
    all_mts += mt

# Umwandlung in NumPy-Arrays
x = np.array(all_ids)
y = np.array(all_mts)

# Berechne Regressionsparameter mit NumPy (Least Squares)
# y = a + b * x
b, a = np.polyfit(x, y, 1)

print(f"Fitts' Gesetz Parameter:")
print(f"a (Intercept): {a:.4f}")
print(f"b (Slope): {b:.4f}")

# Vorhersage der Regressionslinie
x_range = np.linspace(min(x), max(x), 100)
y_pred = a + b * x_range

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(x, y, color='purple', alpha=0.6, label='Messwerte')
plt.plot(x_range, y_pred, color='red', label='Regressionslinie')

plt.title('Fitts’ Law Regression: ID vs. MT')
plt.xlabel('Index of Difficulty (ID)')
plt.ylabel('Movement Time (MT)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
import zipfile
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Pfade definieren
zip_path = "data/json-files.zip"
extract_dir = "data/json-files"
output_dir = "data/analysis_results"

# Ausgabeverzeichnis erstellen
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# ZIP-Datei extrahieren, falls noch nicht geschehen
if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Dateien extrahiert nach {extract_dir}")
else:
    print(f"Verzeichnis {extract_dir} existiert bereits")

# JSON-Dateien laden
json_files = [f for f in os.listdir(extract_dir) if f.endswith('.json')]
print(f"Gefundene JSON-Dateien: {len(json_files)}")

# Datenstrukturen für die drei Experimente
reaction_data = []
binary_data = []
food_data = []

# Daten aus den JSON-Dateien extrahieren
for file in json_files:
    file_path = os.path.join(extract_dir, file)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Teilnehmerinformationen
            participant = data.get('participant', {})
            name = participant.get('name', 'Unbekannt')

            # A.1 Reaktionszeiten-Experiment
            if 'reaction_results' in file:
                reaction_times = data.get('rawData', {}).get('reactionTimes', [])
                if reaction_times:
                    reaction_data.append({
                        'name': name,
                        'mean': np.mean(reaction_times),
                        'std': np.std(reaction_times),
                        'median': np.median(reaction_times),
                        'raw_data': reaction_times
                    })

            # A.2 Binärer Stimulus
            elif 'binary_stimulus' in file:
                purple_times = data.get('rawData', {}).get('purpleReactionTimes', [])
                orange_times = data.get('rawData', {}).get('orangeReactionTimes', [])

                if purple_times:
                    binary_data.append({
                        'name': name,
                        'stimulus_type': 'Lila',
                        'mean': np.mean(purple_times),
                        'std': np.std(purple_times),
                        'median': np.median(purple_times),
                        'raw_data': purple_times
                    })

                if orange_times:
                    binary_data.append({
                        'name': name,
                        'stimulus_type': 'Orange',
                        'mean': np.mean(orange_times),
                        'std': np.std(orange_times),
                        'median': np.median(orange_times),
                        'raw_data': orange_times
                    })

            # A.3 Lebensmittelerkennung
            elif 'food_recognition' in file:
                german_times = data.get('rawData', {}).get('germanReactionTimes', [])
                chinese_times = data.get('rawData', {}).get('chineseReactionTimes', [])
                mexican_times = data.get('rawData', {}).get('mexicanReactionTimes', [])

                if german_times:
                    food_data.append({
                        'name': name,
                        'food_type': 'Deutsch',
                        'mean': np.mean(german_times),
                        'std': np.std(german_times),
                        'median': np.median(german_times),
                        'raw_data': german_times
                    })

                if chinese_times:
                    food_data.append({
                        'name': name,
                        'food_type': 'Chinesisch',
                        'mean': np.mean(chinese_times),
                        'std': np.std(chinese_times),
                        'median': np.median(chinese_times),
                        'raw_data': chinese_times
                    })

                if mexican_times:
                    food_data.append({
                        'name': name,
                        'food_type': 'Mexikanisch',
                        'mean': np.mean(mexican_times),
                        'std': np.std(mexican_times),
                        'median': np.median(mexican_times),
                        'raw_data': mexican_times
                    })
    except Exception as e:
        print(f"Fehler beim Lesen von {file}: {e}")

# DataFrame-Erstellung
reaction_df = pd.DataFrame(reaction_data)
binary_df = pd.DataFrame(binary_data)
food_df = pd.DataFrame(food_data)

# Tabellen für die Zusammenfassung erstellen
print("\n=== Experiment A.1: Einfache Reaktionszeiten ===")
if not reaction_df.empty:
    reaction_table = reaction_df[['name', 'mean', 'median', 'std']].round(2)
    print(tabulate(reaction_table, headers='keys', tablefmt='pretty', showindex=False))

print("\n=== Experiment A.2: Binärer Stimulus ===")
if not binary_df.empty:
    binary_table = binary_df[['name', 'stimulus_type', 'mean', 'median', 'std']].round(2)
    print(tabulate(binary_table, headers='keys', tablefmt='pretty', showindex=False))

print("\n=== Experiment A.3: Lebensmittelerkennung ===")
if not food_df.empty:
    food_table = food_df[['name', 'food_type', 'mean', 'median', 'std']].round(2)
    print(tabulate(food_table, headers='keys', tablefmt='pretty', showindex=False))

# Visualisierungen erstellen
plt.figure(figsize=(15, 12))

# A.1 Reaktionszeit-Boxplots
plt.subplot(3, 1, 1)
if not reaction_df.empty:
    # Erstelle ein DataFrame mit einer Zeile pro Reaktionszeit
    reaction_plot_data = []
    for _, row in reaction_df.iterrows():
        for rt in row['raw_data']:
            reaction_plot_data.append({'name': row['name'], 'reaction_time': rt})
    plot_df = pd.DataFrame(reaction_plot_data)

    sns.boxplot(x='name', y='reaction_time', data=plot_df)
    plt.title('A.1: Einfache Reaktionszeiten nach Testperson')
    plt.xlabel('Testperson')
    plt.ylabel('Reaktionszeit (ms)')
    plt.xticks(rotation=45)

# A.2 Binärer Stimulus Boxplots
plt.subplot(3, 1, 2)
if not binary_df.empty:
    binary_plot_data = []
    for _, row in binary_df.iterrows():
        for rt in row['raw_data']:
            binary_plot_data.append({
                'name': row['name'],
                'reaction_time': rt,
                'stimulus_type': row['stimulus_type']
            })
    binary_plot_df = pd.DataFrame(binary_plot_data)

    sns.boxplot(x='name', y='reaction_time', hue='stimulus_type', data=binary_plot_df)
    plt.title('A.2: Binäre Stimulus Reaktionszeiten nach Testperson')
    plt.xlabel('Testperson')
    plt.ylabel('Reaktionszeit (ms)')
    plt.xticks(rotation=45)
    plt.legend(title='Stimulus-Typ')

# A.3 Lebensmittelerkennung Boxplots
plt.subplot(3, 1, 3)
if not food_df.empty:
    food_plot_data = []
    for _, row in food_df.iterrows():
        for rt in row['raw_data']:
            food_plot_data.append({
                'name': row['name'],
                'reaction_time': rt,
                'food_type': row['food_type']
            })
    food_plot_df = pd.DataFrame(food_plot_data)

    sns.boxplot(x='name', y='reaction_time', hue='food_type', data=food_plot_df)
    plt.title('A.3: Lebensmittelerkennung Reaktionszeiten nach Testperson')
    plt.xlabel('Testperson')
    plt.ylabel('Reaktionszeit (ms)')
    plt.xticks(rotation=45)
    plt.legend(title='Essenskategorie')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'reaktionszeiten_vergleich.png'))
print(f"Visualisierungen gespeichert in: {os.path.join(output_dir, 'reaktionszeiten_vergleich.png')}")

# Statistische Zusammenfassung als CSV exportieren
# A.1 Reaktionszeiten
if not reaction_df.empty:
    reaction_summary = reaction_df[['name', 'mean', 'median', 'std']].round(2)
    reaction_summary.to_csv(os.path.join(output_dir, 'reaktionszeiten_zusammenfassung.csv'), index=False)

# A.2 Binärer Stimulus
if not binary_df.empty:
    binary_summary = binary_df[['name', 'stimulus_type', 'mean', 'median', 'std']].round(2)
    binary_summary.to_csv(os.path.join(output_dir, 'binaerer_stimulus_zusammenfassung.csv'), index=False)

# A.3 Lebensmittelerkennung
if not food_df.empty:
    food_summary = food_df[['name', 'food_type', 'mean', 'median', 'std']].round(2)
    food_summary.to_csv(os.path.join(output_dir, 'lebensmittelerkennung_zusammenfassung.csv'), index=False)

# Vergleichende Analyse zwischen verschiedenen Experimenttypen
print("\n=== Vergleichende Analyse der Experimente ===")

# Durchschnittliche Reaktionszeiten über alle Experimente
mean_reaction = reaction_df['mean'].mean() if not reaction_df.empty else 0
mean_binary_purple = binary_df[binary_df['stimulus_type'] == 'Lila']['mean'].mean() if not binary_df.empty else 0
mean_binary_orange = binary_df[binary_df['stimulus_type'] == 'Orange']['mean'].mean() if not binary_df.empty else 0
mean_food_german = food_df[food_df['food_type'] == 'Deutsch']['mean'].mean() if not food_df.empty else 0
mean_food_chinese = food_df[food_df['food_type'] == 'Chinesisch']['mean'].mean() if not food_df.empty else 0
mean_food_mexican = food_df[food_df['food_type'] == 'Mexikanisch']['mean'].mean() if not food_df.empty else 0

# Erstelle Vergleichsdiagramm für die durchschnittlichen Reaktionszeiten
plt.figure(figsize=(12, 6))
experiment_types = ['Einfach', 'Binär (Lila)', 'Binär (Orange)',
                    'Essen (DE)', 'Essen (CN)', 'Essen (MX)']
reaction_times = [mean_reaction, mean_binary_purple, mean_binary_orange,
                  mean_food_german, mean_food_chinese, mean_food_mexican]

plt.bar(experiment_types, reaction_times)
plt.title('Durchschnittliche Reaktionszeiten nach Experimenttyp')
plt.xlabel('Experimenttyp')
plt.ylabel('Durchschnittliche Reaktionszeit (ms)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'reaktionszeiten_experiment_vergleich.png'))
print(f"Vergleichsdiagramm gespeichert in: {os.path.join(output_dir, 'reaktionszeiten_experiment_vergleich.png')}")

# Zusammenfassung aller Ergebnisse in einer Textdatei
with open(os.path.join(output_dir, 'experiment_zusammenfassung.txt'), 'w', encoding='utf-8') as f:
    f.write("=== Zusammenfassung der Experimente ===\n\n")

    f.write("A.1 Einfache Reaktionszeiten\n")
    f.write(f"Anzahl Teilnehmer: {len(reaction_df.name.unique()) if not reaction_df.empty else 0}\n")
    f.write(f"Durchschnittliche Reaktionszeit: {mean_reaction:.2f} ms\n\n")

    f.write("A.2 Binärer Stimulus\n")
    f.write(f"Anzahl Teilnehmer: {len(binary_df.name.unique()) if not binary_df.empty else 0}\n")
    f.write(f"Durchschnitt (Lila): {mean_binary_purple:.2f} ms\n")
    f.write(f"Durchschnitt (Orange): {mean_binary_orange:.2f} ms\n\n")

    f.write("A.3 Lebensmittelerkennung\n")
    f.write(f"Anzahl Teilnehmer: {len(food_df.name.unique()) if not food_df.empty else 0}\n")
    f.write(f"Durchschnitt (Deutsch): {mean_food_german:.2f} ms\n")
    f.write(f"Durchschnitt (Chinesisch): {mean_food_chinese:.2f} ms\n")
    f.write(f"Durchschnitt (Mexikanisch): {mean_food_mexican:.2f} ms\n")

print(f"Zusammenfassung gespeichert in: {os.path.join(output_dir, 'experiment_zusammenfassung.txt')}")
print("Analyse abgeschlossen.")
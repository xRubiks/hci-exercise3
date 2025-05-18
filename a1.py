import zipfile
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Path to the uploaded zip file
zip_path = "data/json-files.zip"
extract_dir = "data/json-files"

# Extract the zip file if it hasn't been extracted already
if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

# List the extracted files
extracted_files = os.listdir(extract_dir)
print(f"Extrahierte Dateien: {len(extracted_files)}")

# Sammle alle JSON-Daten
all_data = []
for file in extracted_files:
    if file.endswith('.json'):
        file_path = os.path.join(extract_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['filename'] = file
                all_data.append(data)
        except Exception as e:
            print(f"Fehler beim Lesen der Datei {file}: {e}")

print(f"Insgesamt {len(all_data)} JSON-Dateien verarbeitet")

# Extrahiere demographische Daten aus dem "participant"-Objekt
demographics = []
for item in all_data:
    if 'participant' in item:
        participant = item['participant']
        person_data = {
            'name': participant.get('name', ''),
            'age': participant.get('age', None),
            'gender': participant.get('gender', ''),
            'vision_left': participant.get('vision', {}).get('left', None),
            'vision_right': participant.get('vision', {}).get('right', None),
            'colorVision': participant.get('colorVision', ''),
            'browser': participant.get('browserInfo', {}).get('browser', ''),
            'os': participant.get('browserInfo', {}).get('os', ''),
        }

        # Bestimme Experiment-Typ anhand des Dateinamens
        filename = item.get('filename', '')
        if 'reaction_results' in filename:
            person_data['experiment_type'] = 'Reaktionszeiten'
        elif 'binary_stimulus' in filename:
            person_data['experiment_type'] = 'Binärer Stimulus'
        elif 'food_recognition' in filename:
            person_data['experiment_type'] = 'Lebensmittelerkennung'
        else:
            person_data['experiment_type'] = 'Unbekannt'

        # Füge experiment-spezifische Daten hinzu
        if 'summary' in item:
            summary = item['summary']
            if person_data['experiment_type'] == 'Reaktionszeiten':
                person_data['mean_reaction_time'] = summary.get('mean', None)
                person_data['mistakes'] = summary.get('mistakes', 0)
            elif person_data['experiment_type'] == 'Binärer Stimulus':
                person_data['purple_mean'] = summary.get('purpleSquares', {}).get('mean', None)
                person_data['orange_mean'] = summary.get('orangeSquares', {}).get('mean', None)
                person_data['error_rate'] = summary.get('errorRate', 0)
            elif person_data['experiment_type'] == 'Lebensmittelerkennung':
                person_data['german_food_error'] = summary.get('germanFood', {}).get('errorRate', 0)
                person_data['chinese_food_error'] = summary.get('chineseFood', {}).get('errorRate', 0)
                person_data['mexican_food_error'] = summary.get('mexicanFood', {}).get('errorRate', 0)

        demographics.append(person_data)

# Erstelle ein DataFrame für die Analyse
df = pd.DataFrame(demographics)

# Demografische Zusammenfassung erstellen
print("\nZusammenfassung der demographischen Daten:")
print("-" * 40)

# Altersanalyse
if 'age' in df.columns:
    print(f"Durchschnittsalter: {df['age'].mean():.2f} Jahre")
    print(f"Altersverteilung: Min={df['age'].min()}, Max={df['age'].max()}")

    # Altersverteilung visualisieren
    plt.figure(figsize=(10, 6))
    plt.hist(df['age'], bins=range(min(df['age']), max(df['age']) + 2), align='left')
    plt.title('Altersverteilung')
    plt.xlabel('Alter')
    plt.ylabel('Anzahl')
    plt.savefig('data/altersverteilung.png')
    print("Altersverteilung als Grafik gespeichert: data/altersverteilung.png")

# Geschlechterverteilung
if 'gender' in df.columns:
    gender_counts = df['gender'].value_counts()
    print("\nGeschlechterverteilung:")
    for gender, count in gender_counts.items():
        print(f"  {gender}: {count} ({count / len(df) * 100:.2f}%)")

# Sehvermögen-Analyse
if 'vision_left' in df.columns and 'vision_right' in df.columns:
    print("\nSehvermögen:")
    vision_normal = df[(df['vision_left'] == 0) & (df['vision_right'] == 0)].shape[0]
    vision_corrected = df.shape[0] - vision_normal
    print(f"  Normal: {vision_normal} ({vision_normal / len(df) * 100:.2f}%)")
    print(f"  Korrigiert: {vision_corrected} ({vision_corrected / len(df) * 100:.2f}%)")

# Browser-Verteilung
if 'browser' in df.columns:
    browser_counts = df['browser'].value_counts()
    print("\nBrowser-Verteilung:")
    for browser, count in browser_counts.items():
        print(f"  {browser}: {count} ({count / len(df) * 100:.2f}%)")

# Experiment-Typen
if 'experiment_type' in df.columns:
    experiment_counts = df['experiment_type'].value_counts()
    print("\nExperiment-Verteilung:")
    for exp, count in experiment_counts.items():
        print(f"  {exp}: {count}")

# Experiment-spezifische Analysen
print("\nExperiment-spezifische Ergebnisse:")
print("-" * 40)

# Reaktionszeiten-Experiment
reaction_df = df[df['experiment_type'] == 'Reaktionszeiten']
if not reaction_df.empty and 'mean_reaction_time' in reaction_df.columns:
    print("\nReaktionszeiten-Experiment:")
    print(f"  Anzahl Teilnehmer: {len(reaction_df)}")
    print(f"  Durchschnittliche Reaktionszeit: {reaction_df['mean_reaction_time'].mean():.2f} ms")
    print(f"  Fehlerrate: {reaction_df['mistakes'].mean():.2f}")

# Binärer Stimulus Experiment
binary_df = df[df['experiment_type'] == 'Binärer Stimulus']
if not binary_df.empty:
    print("\nBinärer Stimulus Experiment:")
    print(f"  Anzahl Teilnehmer: {len(binary_df)}")
    if 'purple_mean' in binary_df.columns:
        print(f"  Durchschnittliche Reaktionszeit (Lila): {binary_df['purple_mean'].mean():.2f} ms")
    if 'orange_mean' in binary_df.columns:
        print(f"  Durchschnittliche Reaktionszeit (Orange): {binary_df['orange_mean'].mean():.2f} ms")
    if 'error_rate' in binary_df.columns:
        print(f"  Durchschnittliche Fehlerrate: {binary_df['error_rate'].mean():.2f}%")

# Lebensmittelerkennung Experiment
food_df = df[df['experiment_type'] == 'Lebensmittelerkennung']
if not food_df.empty:
    print("\nLebensmittelerkennung Experiment:")
    print(f"  Anzahl Teilnehmer: {len(food_df)}")
    if 'german_food_error' in food_df.columns:
        print(f"  Fehlerrate (Deutsches Essen): {food_df['german_food_error'].mean():.2f}%")
    if 'chinese_food_error' in food_df.columns:
        print(f"  Fehlerrate (Chinesisches Essen): {food_df['chinese_food_error'].mean():.2f}%")
    if 'mexican_food_error' in food_df.columns:
        print(f"  Fehlerrate (Mexikanisches Essen): {food_df['mexican_food_error'].mean():.2f}%")

# Erstelle Übersichtsgrafik
plt.figure(figsize=(14, 10))

# Geschlecht und Alter
plt.subplot(2, 2, 1)
if 'gender' in df.columns:
    gender_counts.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Geschlechterverteilung')
    plt.ylabel('')

plt.subplot(2, 2, 2)

if 'experiment_type' in df.columns:
    experiment_counts.plot(kind='bar')
    plt.title('Experiment-Verteilung')
    plt.ylabel('Anzahl')
    plt.xlabel('Experiment-Typ')
    plt.xticks(rotation=45)

# Reaktionszeiten nach Experimenten
plt.subplot(2, 2, 3)
experiment_reaction_times = []
labels = []

if not reaction_df.empty and 'mean_reaction_time' in reaction_df.columns:
    experiment_reaction_times.append(reaction_df['mean_reaction_time'].mean())
    labels.append('Reaktionszeiten')

if not binary_df.empty:
    if 'purple_mean' in binary_df.columns:
        experiment_reaction_times.append(binary_df['purple_mean'].mean())
        labels.append('Binär (Lila)')
    if 'orange_mean' in binary_df.columns:
        experiment_reaction_times.append(binary_df['orange_mean'].mean())
        labels.append('Binär (Orange)')

plt.bar(labels, experiment_reaction_times)
plt.title('Durchschnittliche Reaktionszeiten nach Experiment')
plt.ylabel('Zeit (ms)')
plt.xticks(rotation=45)

# Fehlerraten
plt.subplot(2, 2, 4)
error_rates = []
error_labels = []

if not food_df.empty:
    if 'german_food_error' in food_df.columns:
        error_rates.append(food_df['german_food_error'].mean())
        error_labels.append('DE Essen')
    if 'chinese_food_error' in food_df.columns:
        error_rates.append(food_df['chinese_food_error'].mean())
        error_labels.append('CN Essen')
    if 'mexican_food_error' in food_df.columns:
        error_rates.append(food_df['mexican_food_error'].mean())
        error_labels.append('MX Essen')

if not binary_df.empty and 'error_rate' in binary_df.columns:
    error_rates.append(binary_df['error_rate'].mean())
    error_labels.append('Binär')

# Nach der bestehenden Browser-Verteilung (ca. Zeile 124)
# Farbsinn-Verteilung
if 'colorVision' in df.columns:
    color_vision_counts = df['colorVision'].value_counts()
    print("\nFarbsinn-Verteilung:")
    for vision, count in color_vision_counts.items():
        print(f"  {vision}: {count} ({count / len(df) * 100:.2f}%)")

# Im Bereich der Grafiken-Erstellung:
# Erstelle neue Grafik für Browser- und Farbsinn-Verteilung
plt.figure(figsize=(12, 6))

# Browser-Verteilung
plt.subplot(1, 2, 1)
plt.subplot(1, 2, 1)
if 'browser' in df.columns:
    browser_counts.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Browser-Verteilung')
    plt.ylabel('')

# Farbsinn-Verteilung
plt.subplot(1, 2, 2)
if 'colorVision' in df.columns:
    color_vision_counts = df['colorVision'].value_counts()
    print("\nFarbsinn-Verteilung:")
    for vision, count in color_vision_counts.items():
        print(f"  {vision}: {count} ({count / len(df) * 100:.2f}%)")

plt.tight_layout()
plt.savefig('data/browser_farbsinn_verteilung.png')
print("Browser- und Farbsinn-Verteilung gespeichert: data/browser_farbsinn_verteilung.png")


plt.bar(error_labels, error_rates)
plt.title('Durchschnittliche Fehlerraten')
plt.ylabel('Fehlerrate (%)')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('data/experiment_uebersicht.png')
print("Übersichtsgrafik gespeichert: data/experiment_uebersicht.png")

# Speichere die demografische Zusammenfassung in einer Datei
with open('data/demografische_zusammenfassung.txt', 'w', encoding='utf-8') as f:
    f.write("Demografische Zusammenfassung\n")
    f.write("=========================\n\n")
    f.write(f"Anzahl Personen: {len(df)}\n\n")

    if 'age' in df.columns:
        f.write(f"Altersstatistik:\n")
        f.write(f"- Durchschnittsalter: {df['age'].mean():.2f} Jahre\n")
        f.write(f"- Minimum: {df['age'].min()} Jahre\n")
        f.write(f"- Maximum: {df['age'].max()} Jahre\n\n")

    if 'gender' in df.columns:
        f.write("Geschlechterverteilung:\n")
        for gender, count in gender_counts.items():
            f.write(f"- {gender}: {count} ({count / len(df) * 100:.2f}%)\n")
        f.write("\n")

    if 'browser' in df.columns:
        f.write("Browser-Nutzung:\n")
        for browser, count in browser_counts.items():
            f.write(f"- {browser}: {count} ({count / len(df) * 100:.2f}%)\n")
        f.write("\n")

    f.write("Experimentzusammenfassung:\n")
    for exp, count in experiment_counts.items():
        f.write(f"- {exp}: {count} Teilnehmer\n")

    # Experiment-spezifische Daten hinzufügen
    f.write("\nDetaillierte Experimentdaten:\n")

    if not reaction_df.empty and 'mean_reaction_time' in reaction_df.columns:
        f.write("\nReaktionszeiten-Experiment:\n")
        f.write(f"- Durchschnittliche Zeit: {reaction_df['mean_reaction_time'].mean():.2f} ms\n")
        f.write(f"- Durchschnittliche Fehler: {reaction_df['mistakes'].mean():.2f}\n")

    if not binary_df.empty:
        f.write("\nBinärer Stimulus Experiment:\n")
        if 'purple_mean' in binary_df.columns:
            f.write(f"- Lila Stimuli Zeit: {binary_df['purple_mean'].mean():.2f} ms\n")
        if 'orange_mean' in binary_df.columns:
            f.write(f"- Orange Stimuli Zeit: {binary_df['orange_mean'].mean():.2f} ms\n")
        if 'error_rate' in binary_df.columns:
            f.write(f"- Fehlerrate: {binary_df['error_rate'].mean():.2f}%\n")

    if not food_df.empty:
        f.write("\nLebensmittelerkennung:\n")
        if 'german_food_error' in food_df.columns:
            f.write(f"- Deutsches Essen Fehlerrate: {food_df['german_food_error'].mean():.2f}%\n")
        if 'chinese_food_error' in food_df.columns:
            f.write(f"- Chinesisches Essen Fehlerrate: {food_df['chinese_food_error'].mean():.2f}%\n")
        if 'mexican_food_error' in food_df.columns:
            f.write(f"- Mexikanisches Essen Fehlerrate: {food_df['mexican_food_error'].mean():.2f}%\n")

print("\nAusführliche Zusammenfassung wurde in data/demografische_zusammenfassung.txt gespeichert")
import zipfile
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter
from scipy import stats


class ReaktionszeitenVergleich:
    def __init__(self, binary_df, food_df, bootstrap_samples=10000, alpha=0.05):
        self.binary_df = binary_df
        self.food_df = food_df
        self.bootstrap_samples = bootstrap_samples
        self.alpha = alpha

        # Extrahiere Reaktionszeiten
        self.binary_times = self._extract_binary_times()
        self.food_times = self._extract_food_times()

        # Berechne Statistiken
        self.binary_mean = np.mean(self.binary_times)
        self.food_mean = np.mean(self.food_times)
        self.binary_n = len(self.binary_times)
        self.food_n = len(self.food_times)

    def _extract_binary_times(self):
        """Extrahiert alle Reaktionszeiten für den binären Stimulus-Test"""
        times = []
        for _, row in self.binary_df.iterrows():
            if 'purple_mean' in row and not pd.isna(row['purple_mean']):
                times.append(row['purple_mean'])
            if 'orange_mean' in row and not pd.isna(row['orange_mean']):
                times.append(row['orange_mean'])
        return times

    def _extract_food_times(self):
        """Extrahiert alle Reaktionszeiten für den Lebensmittelerkennungstest"""
        times = []
        for _, row in self.food_df.iterrows():
            # Extrahiere Mittelwerte für alle Lebensmittelkategorien
            for column in ['german_food_mean', 'chinese_food_mean', 'mexican_food_mean']:
                if column in self.food_df.columns and not pd.isna(row.get(column)):
                    times.append(row[column])
        return times

    def run_bootstrap_test(self):
        """Führt den Bootstrap-Test zwischen den beiden Reaktionstests durch"""
        # Beobachtete Teststatistik (Differenz der Mittelwerte)
        observed_diff = self.food_mean - self.binary_mean

        # Kombiniere alle Daten für Bootstrap
        all_times = np.concatenate([self.binary_times, self.food_times])
        n_all = len(all_times)

        # Bootstrap-Simulation
        bootstrap_diffs = []
        for _ in range(self.bootstrap_samples):
            # Zufälliges Shuffling der Daten
            shuffled = np.random.permutation(all_times)

            # Teile die gemischten Daten wieder in zwei Gruppen auf
            sample_binary = shuffled[:self.binary_n]
            sample_food = shuffled[self.binary_n:n_all]

            # Berechne Differenz der Mittelwerte
            diff = np.mean(sample_food) - np.mean(sample_binary)
            bootstrap_diffs.append(diff)

        # Berechne p-Wert als Anteil der Bootstrap-Ergebnisse, die extremer sind als der beobachtete Wert
        if observed_diff >= 0:
            p_value = np.mean(np.array(bootstrap_diffs) >= observed_diff)
        else:
            p_value = np.mean(np.array(bootstrap_diffs) <= observed_diff)

        # Verdoppeln für zweiseitigen Test
        p_value = min(p_value * 2, 1.0)

        return {
            'binary_mean': self.binary_mean,
            'food_mean': self.food_mean,
            'binary_n': self.binary_n,
            'food_n': self.food_n,
            'observed_diff': observed_diff,
            'bootstrap_samples': self.bootstrap_samples,
            'p_value': p_value,
            'significant': p_value < self.alpha
        }

    def plot_bootstrap_distribution(self):
        """Visualisiert die Bootstrap-Verteilung mit dem beobachteten Wert"""
        observed_diff = self.food_mean - self.binary_mean

        all_times = np.concatenate([self.binary_times, self.food_times])
        n_all = len(all_times)

        bootstrap_diffs = []
        for _ in range(self.bootstrap_samples):
            shuffled = np.random.permutation(all_times)
            sample_binary = shuffled[:self.binary_n]
            sample_food = shuffled[self.binary_n:n_all]
            diff = np.mean(sample_food) - np.mean(sample_binary)
            bootstrap_diffs.append(diff)

        plt.figure(figsize=(10, 6))
        plt.hist(bootstrap_diffs, bins=50, alpha=0.7)
        plt.axvline(observed_diff, color='red', linestyle='--',
                    label=f'Beobachteter Unterschied: {observed_diff:.2f}')
        plt.title('Bootstrap-Verteilung der Mittelwertdifferenzen')
        plt.xlabel('Differenz der Mittelwerte (B.3 - B.2)')
        plt.ylabel('Häufigkeit')
        plt.legend()
        plt.tight_layout()
        plt.savefig('data/bootstrap_verteilung.png')
        print("Bootstrap-Verteilung gespeichert in: data/bootstrap_verteilung.png")

    def print_results(self):
        """Gibt die Ergebnisse des Bootstrap-Tests aus"""
        results = self.run_bootstrap_test()

        print("\n=== Bootstrap-Test: B.2 (Binärer Stimulus) vs. B.3 (Lebensmittelerkennung) ===")
        print(f"Mittelwert B.2: {results['binary_mean']:.2f} ms (n={results['binary_n']})")
        print(f"Mittelwert B.3: {results['food_mean']:.2f} ms (n={results['food_n']})")
        print(f"Beobachteter Unterschied: {results['observed_diff']:.2f} ms")
        print(f"Bootstrap Samples: {results['bootstrap_samples']}")
        print(f"p-Wert: {results['p_value']:.4f}")

        if results['significant']:
            print(f"Ergebnis: Der Unterschied ist statistisch signifikant (p < {self.alpha})")
            print("Die Nullhypothese (kein Unterschied) wird abgelehnt.")
        else:
            print(f"Ergebnis: Der Unterschied ist nicht statistisch signifikant (p ≥ {self.alpha})")
            print("Die Nullhypothese (kein Unterschied) kann nicht abgelehnt werden.")

        # Visualisierung erstellen
        self.plot_bootstrap_distribution()

        # Ergebnisse in Datei speichern
        self.save_results_to_file(results)

    def save_results_to_file(self, results):
        """Speichert die Ergebnisse des Bootstrap-Tests in einer Datei"""
        output_dir = "data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(os.path.join(output_dir, 'bootstrap_test_ergebnisse.txt'), 'w', encoding='utf-8') as f:
            f.write("=== Bootstrap-Test: B.2 (Binärer Stimulus) vs. B.3 (Lebensmittelerkennung) ===\n")
            f.write(f"Mittelwert B.2: {results['binary_mean']:.2f} ms (n={results['binary_n']})\n")
            f.write(f"Mittelwert B.3: {results['food_mean']:.2f} ms (n={results['food_n']})\n")
            f.write(f"Beobachteter Unterschied: {results['observed_diff']:.2f} ms\n")
            f.write(f"Bootstrap Samples: {results['bootstrap_samples']}\n")
            f.write(f"p-Wert: {results['p_value']:.6f}\n\n")

            if results['significant']:
                f.write(f"Ergebnis: Der Unterschied ist statistisch signifikant (p < {self.alpha})\n")
                f.write("Die Nullhypothese (kein Unterschied) wird abgelehnt.\n")
            else:
                f.write(f"Ergebnis: Der Unterschied ist nicht statistisch signifikant (p ≥ {self.alpha})\n")
                f.write("Die Nullhypothese (kein Unterschied) kann nicht abgelehnt werden.\n")

        print(f"Ergebnisse gespeichert in: {os.path.join(output_dir, 'bootstrap_test_ergebnisse.txt')}")


def load_data():
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
    return all_data


def extract_test_data(all_data):
    # Extrahiere Daten für B.2 (Binärer Stimulus) und B.3 (Lebensmittelerkennung)
    binary_data = []
    food_data = []

    for item in all_data:
        if 'participant' in item and 'summary' in item:
            name = item['participant'].get('name', '')

            # Binärer Stimulus
            if 'binary_stimulus' in item.get('filename', ''):
                if 'purpleSquares' in item['summary'] and 'orangeSquares' in item['summary']:
                    binary_data.append({
                        'name': name,
                        'purple_mean': item['summary']['purpleSquares'].get('mean', None),
                        'orange_mean': item['summary']['orangeSquares'].get('mean', None),
                        'error_rate': item['summary'].get('errorRate', 0)
                    })

            # Lebensmittelerkennung
            elif 'food_recognition' in item.get('filename', ''):
                food_entry = {'name': name}

                if 'germanFood' in item['summary']:
                    food_entry['german_food_mean'] = item['summary']['germanFood'].get('mean', None)
                    food_entry['german_food_error'] = item['summary']['germanFood'].get('errorRate', 0)

                if 'chineseFood' in item['summary']:
                    food_entry['chinese_food_mean'] = item['summary']['chineseFood'].get('mean', None)
                    food_entry['chinese_food_error'] = item['summary']['chineseFood'].get('errorRate', 0)

                if 'mexicanFood' in item['summary']:
                    food_entry['mexican_food_mean'] = item['summary']['mexicanFood'].get('mean', None)
                    food_entry['mexican_food_error'] = item['summary']['mexicanFood'].get('errorRate', 0)

                food_data.append(food_entry)

    bin_df = pd.DataFrame(binary_data)
    food_dff = pd.DataFrame(food_data)

    print(f"Binärer Stimulus: {len(bin_df)} Datensätze geladen")
    print(f"Lebensmittelerkennung: {len(food_dff)} Datensätze geladen")

    return bin_df, food_dff


if __name__ == "__main__":
    # Daten laden
    print("Daten werden geladen...")
    all_data = load_data()

    # Testdaten extrahieren
    print("\nExtrahiere Testdaten für statistische Analyse...")
    binary_df, food_df = extract_test_data(all_data)

    # Output-Verzeichnis erstellen, falls es nicht existiert
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Bootstrap-Analyse durchführen
    print("\nFühre Bootstrap-Test durch...")
    vergleich = ReaktionszeitenVergleich(binary_df, food_df, bootstrap_samples=10000)
    vergleich.print_results()

    print("\nAnalyse abgeschlossen.")
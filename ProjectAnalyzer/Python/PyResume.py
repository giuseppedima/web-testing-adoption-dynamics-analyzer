import os
import csv

class CalculateReasume:
    @staticmethod
    def create_res_csv_file(data, res_path='/home/sergio/ICST25-E2EMining/py_test_analysis/result.csv'):
        # Verifica se il file CSV esiste
        file_exists = os.path.isfile(res_path)
        # Apri il file in modalità append
        with open(res_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Se il file non esiste, scrivi l'intestazione
            if not file_exists:
                writer.writerow(['Repository',
                                 'Is JMeter',
                                 'Is Locust',
                                 'Is Selenium',
                                 'Is Playwright',
                                 'Is Puppeteer',
                                 'With Pytest',
                                 'With Unnitest',
                                 'Number of @Test',
                                 'Number of Test'])
            # Scrivi i dati
            writer.writerow(data)

    @staticmethod
    def calculate_reasume(path):
        # Controlla se il percorso esiste ed è una directory
        if os.path.exists(path) and os.path.isdir(path):
            # Scorre i file e le cartelle nel percorso dato
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    print(f"Leggendo il file: {file_path}")
                    with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
                        reader = csv.reader(csv_file)
                        next(reader)  # Salta la prima riga (l'intestazione)
                        reponame = ""
                        jmeter_test = 0
                        locust_test = 0
                        selenium_test = 0
                        playwright_test = 0
                        puppeteer = 0
                        with_pytest = 0
                        with_unittest = 0
                        num_test = 0
                        row_count = sum(1 for _ in reader)
                        csv_file.seek(0)
                        # Rileggi il file dall'inizio e stampa le righe
                        reader = csv.reader(csv_file)
                        next(reader)
                        for row in reader:
                            # print(row)
                            # print(row[0])
                            if len(row) != 0:
                                reponame = row[0]
                                jmeter_test += int(row[2])
                                locust_test += int(row[3])
                                selenium_test += int(row[4])
                                playwright_test += int(row[5])
                                puppeteer += int(row[6])
                                with_pytest += int(row[7])
                                with_unittest += int(row[8])
                                num_test += int(row[9])
                    CalculateReasume.create_res_csv_file(
                        [os.path.basename(csv_file.name), jmeter_test, locust_test,
                         selenium_test,playwright_test, puppeteer,with_pytest,
                         with_unittest, num_test, row_count])
        else:
            print(f"Il percorso {path} non esiste o non è una directory valida.")

    @staticmethod
    def change_first_row(cartella):
        nuova_prima_riga = ['Repository',
                            'File Path',
                            'Is JMeter',
                            'Is Locust',
                            'Is Selenium',
                            'Is Playwright',
                            'Is Puppeteer',
                            'With Pytest',
                            'With Unittest',
                            'Number of @Test',
                            'Number of Test']
        # Itera su tutti i file nella cartella
        for nome_file in os.listdir(cartella):
            if nome_file.endswith('.csv'):
                print(f"Sto esaminando il file: {nome_file}")
                percorso_file = os.path.join(cartella, nome_file)

                # Leggi il contenuto del file CSV
                with open(percorso_file, mode='r', newline='', encoding='utf-8') as file_csv:
                    lettore = list(csv.reader(file_csv))

                # Verifica che il file non sia vuoto e abbia almeno una riga
                if lettore:
                    # Modifica la prima riga
                    lettore[0] = nuova_prima_riga
                else:
                    print(f"Il file {nome_file} è vuoto e sarà saltato.")
                    continue

                # Scrivi il contenuto modificato nel file CSV
                with open(percorso_file, mode='w', newline='', encoding='utf-8') as file_csv:
                    scrittore = csv.writer(file_csv)
                    scrittore.writerows(lettore)

        print("La prima riga di ogni file CSV è stata aggiornata.")



CalculateReasume.calculate_reasume(r'/home/sergio/ICST25-E2EMining/py_test_analysis/')
#CalculateReasume.change_first_row(r'/home/sergio/ICST25-E2EMining/py_test_analysis/')

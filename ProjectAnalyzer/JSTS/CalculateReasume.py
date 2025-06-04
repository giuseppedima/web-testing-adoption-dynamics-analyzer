import os
import csv

class CalculateReasume:
    @staticmethod
    def create_res_csv_file(data, res_path='/home/sergio/ICST25-E2EMining/js_ts_test_analysis/result.csv'):
        # Verifica se il file CSV esiste
        file_exists = os.path.isfile(res_path)
        # Apri il file in modalità append
        with open(res_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Se il file non esiste, scrivi l'intestazione
            if not file_exists:
                writer.writerow(
                    ['Repository',
                     'Is JMeter',
                     'Is Locust',
                     'Is Selenium JS',
                     'Is Selenium TS',
                     'Is Playwright JS',
                     'Is Playwright TS ',
                     'Is Puppeteer JS',
                     'Is Puppeteer TS',
                     'Is Cypress JS',
                     'Is Cypress TS',
                     'With Jest',
                     'With Mocha',
                     'With Jasmine',
                     'Number of @Test',
                     'Number of Files']
                    )
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
                        selenium_test_js = 0
                        selenium_test_ts = 0
                        playwright_test_js = 0
                        playwright_test_ts = 0
                        cypress_js = 0
                        cypress_ts = 0
                        puppeteer_js = 0
                        puppeteer_ts = 0
                        with_jest = 0
                        with_mocha = 0
                        with_jasmine = 0
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
                                selenium_test_js += int(row[4])
                                selenium_test_ts += int(row[5])
                                playwright_test_js += int(row[6])
                                playwright_test_ts += int(row[7])
                                puppeteer_js += int(row[8])
                                puppeteer_ts += int(row[9])
                                cypress_js += int(row[10])
                                cypress_ts += int(row[11])
                                with_jest += int(row[12])
                                with_mocha += int(row[13])
                                with_jasmine += int(row[14])
                                #print(row[15])
                                num1 = row[15].strip('()').split(',')[0].strip()
                                num_test += int(num1)  # Converte num1 in intero
                                #num_test += int(row[15])

                    CalculateReasume.create_res_csv_file(
                        [os.path.basename(csv_file.name), jmeter_test, locust_test,
                         selenium_test_js,selenium_test_ts, playwright_test_js,playwright_test_ts,
                         puppeteer_js,puppeteer_ts,cypress_js,cypress_ts,with_jest,with_mocha,with_jasmine
                         , num_test, row_count])

        else:
            print(f"Il percorso {path} non esiste o non è una directory valida.")


CalculateReasume.calculate_reasume(r'/home/sergio/ICST25-E2EMining/js_ts_test_analysis/')
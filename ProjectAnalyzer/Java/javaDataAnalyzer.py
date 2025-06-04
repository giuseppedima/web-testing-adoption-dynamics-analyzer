import os
import csv
class JavaDataAnalyzer:


    @staticmethod
    def create_res_csv_file(data,res_path='/home/sergio/ICST25-E2EMining/java_test_analysis/result.csv'):
        # Verifica se il file CSV esiste
        file_exists = os.path.isfile(res_path)
        # Apri il file in modalità append
        with open(res_path, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Se il file non esiste, scrivi l'intestazione
            if not file_exists:
                writer.writerow(
                    ['Repository',  'JMeter Files', 'Locust Files', 'Selenium Files', 'Playwright Files', 'With JUnit',
                     'With TestNG',
                     'Number of @Test','Number of Files'])

            # Scrivi i dati
            writer.writerow(data)


    @staticmethod
    def analyze_java_test(path):
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
                        reponame=""
                        jmeter_test= 0
                        locust_test= 0
                        selenium_test= 0
                        playwright_test = 0
                        with_junit = 0
                        with_testng= 0
                        num_test = 0
                        row_count = sum(1 for _ in reader)
                        csv_file.seek(0)
                        # Rileggi il file dall'inizio e stampa le righe
                        reader = csv.reader(csv_file)
                        next(reader)
                        for row in reader:
                            #print(row)
                            #print(row[0])
                            if len(row) != 0:
                                reponame= row[0]
                                jmeter_test += int(row[2])
                                locust_test += int(row[3])
                                selenium_test += int(row[4])
                                playwright_test += int(row[5])
                                with_junit += int(row[6])
                                with_testng += int(row[7])
                                num_test += int(row[8])

                    JavaDataAnalyzer.create_res_csv_file([os.path.basename(csv_file.name),jmeter_test,locust_test,selenium_test,playwright_test,with_junit,with_testng,num_test,row_count])
                    print(f"repo: {reponame} - jm:{jmeter_test} loc:{locust_test} sel:{selenium_test} play:{playwright_test} ju:{with_junit} ng:{with_testng} num_test:{num_test} num_file:{row_count}")

        else:
            print(f"Il percorso {path} non esiste o non è una directory valida.")



JavaDataAnalyzer.analyze_java_test(r'/home/sergio/ICST25-E2EMining/java_test_analysis')
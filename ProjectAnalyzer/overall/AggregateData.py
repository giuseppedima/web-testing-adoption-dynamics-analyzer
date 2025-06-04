import csv
import os
class AggregateData:

    py_js_intersect = ['HumanSignal_label-studio.csv',
                       'LAION-AI_Open-Assistant.csv',
                        'blazemeter_taurus.csv',
                       'determined-ai_determined.csv',
                        'elastos_elastos.csv',
                       'epistimio_orion.csv',
                       'frg-fossee_esim-cloud.csv',
                        'geoadmin_mf-geoadmin3.csv',
                       'geonode_geonode.csv',
                       'kubeshop_testkube.csv',
                        'posthog_posthog-foss.csv',
                       'posthog_posthog.csv',
                        'quadratichq_quadratic.csv',
                       'sefaria_sefaria-project.csv',
     'wso2_product-apim.csv']

    py_java_intersect = ['ant-media_ant-media-server.csv',
                         'apache_roller.csv',
                         'apereo_cas.csv',
                        'azure_azure-sdk-for-java.csv',
                         'eclipse_vorto.csv',
                         'eugenp_tutorials.csv',
                        'gluufederation_oxauth.csv',
                         'googlecloudplatform_bank-of-anthos.csv',
                        'googlecloudplatform_professional-services.csv',
                         'iqss_dataverse.csv',
                        'janssenproject_jans.csv',
                        'knowagelabs_knowage-server.csv',
                        'mapfish_mapfish-print.csv',
                         'nysenate_openlegislation.csv',
                        'openapitools_openapi-generator.csv',
                         'ripe-ncc_whois.csv',
                        'sakaiproject_sakai.csv',
                         'spagobilabs_spagobi.csv',
                        'splicemachine_spliceengine.csv',
                         'undera_jmeter-plugins.csv',
                        'wso2_product-apim.csv',
                         'wso2_product-is.csv',
                         'zkoss_zkspreadsheet.csv']

    js_java_intersect = ['wso2_product-apim.csv']

    overall_intersect = ['wso2_product-apim.csv']

    @staticmethod
    def get_repos_name_by_path(path):
        repos = []
        for name_file in os.listdir(path):
            if(name_file == 'result.csv'):
                percorso_file = os.path.join(path,name_file)
                with open(percorso_file, mode='r', newline='',encoding='utf-8') as file_csv:
                    reader = csv.reader(file_csv)
                    next(reader)
                    for row in reader:
                        repos.append(row[0])
        return repos


    @staticmethod
    def get_row_by_path(r,path):
        try:
            with open(path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    repo = row[0]
                    if repo == r:
                        return row
        except FileNotFoundError:
            print(f"Il file non è stato trovato: {path}")
        except csv.Error as e:
            print(f"Errore durante la lettura del file CSV: {e}")
        except Exception as e:
            print(f"Si è verificato un errore: {e}")
        return []


    @staticmethod
    def write_resrow_csv_file(path,data):
        file_exists = os.path.isfile(path)
        headers = [
            "repository",
            "selenium_java",
            "selenium_js",
            "selenium_ts",
            "selenium_py",
            "playwright_java",
            "playwright_js",
            "playwright_ts",
            "playwright_py",
            "puppeteer_js",
            "puppeteer_ts",
            "puppeteer_py",
            "cypress_js",
            "cypress_ts",
            "locust_java",
            "locust_py",
            "jmeter",
            "with_junit",
            "with_testng",
            "with_jest",
            "with_mocha",
            "with_jasmine",
            "with_pytest",
            "with_unittest",
            "number of test",
            "number of file"
        ]
        with open(path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(data)

    @staticmethod
    def get_data_js_only(row):
        repository = row[0]
        selenium_java = 0
        selenium_js = row[3]
        selenium_ts = row[4]
        selenium_py = 0
        playwright_java = 0
        playwright_js = row[5]
        playwright_ts = row[6]
        playwright_py = 0
        puppeteer_js = row[7]
        puppeteer_ts = row[8]
        puppeteer_py = 0
        cypress_js = row[9]
        cypress_ts = row[10]
        locust_java = 0
        locust_py = row[2]
        jmeter = row[1]
        with_junit = 0
        with_testng = 0
        with_jest = row[11]
        with_mocha = row[12]
        with_jasmine = row[13]
        with_pytest = 0
        with_unittest = 0
        number_of_test = row[14]
        number_of_file = row[15]
        #comments = row[16]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data

    @staticmethod
    def get_data_all_intersect(row_js,row_java,row_py):
        repository = row_js[0]
        selenium_java = row_java[3]
        selenium_js = row_js[3]
        selenium_ts = row_js[4]
        selenium_py = row_py[3]
        playwright_java = row_java[4]
        playwright_js = row_js[5]
        playwright_ts = row_js[6]
        playwright_py = row_py[4]
        puppeteer_js = row_js[7]
        puppeteer_ts = row_js[8]
        puppeteer_py = row_py[5]
        cypress_js = row_js[9]
        cypress_ts = row_js[10]
        locust_java = row_java[2]
        locust_py = row_py[2]
        jmeter = row_py[1]
        with_junit = row_java[5]
        with_testng = row_java[6]
        with_jest = row_js[11]
        with_mocha = row_js[12]
        with_jasmine = row_js[13]
        with_pytest = row_py[6]
        with_unittest = row_py[7]
        number_of_test = int(row_js[14])+int(row_java[7])+int(row_py[8])
        number_of_file =int(selenium_java)+int(selenium_js)+int(selenium_ts)+int(selenium_py)+int(playwright_java)+int(playwright_py)+int(playwright_js)+int(playwright_ts)+int(puppeteer_py)+int(puppeteer_js)+int(puppeteer_ts)+int(cypress_ts)+int(cypress_js)+int(jmeter)+int(locust_java)+int(locust_py)
        #comments = row_js[16]+";"+row_java[9]+";"+row_py[10]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data


    @staticmethod
    def get_data_js_py_intersect (row_js,row_py):
        repository = row_js[0]
        selenium_java = 0
        selenium_js = row_js[3]
        selenium_ts = row_js[4]
        selenium_py = row_py[3]
        playwright_java = 0
        playwright_js = row_js[5]
        playwright_ts = row_js[6]
        playwright_py = row_py[4]
        puppeteer_js = row_js[7]
        puppeteer_ts = row_js[8]
        puppeteer_py = row_py[5]
        cypress_js = row_js[9]
        cypress_ts = row_js[10]
        locust_java = 0
        locust_py = row_py[2]
        jmeter = row_py[1]
        with_junit = 0
        with_testng = 0
        with_jest = row_js[11]
        with_mocha = row_js[12]
        with_jasmine = row_js[13]
        with_pytest = row_py[6]
        with_unittest = row_py[7]
        number_of_test = int(row_js[14]) +int(row_py[8])
        number_of_file =int(selenium_java)+int(selenium_js)+int(selenium_ts)+int(selenium_py)+int(playwright_java)+int(playwright_py)+int(playwright_js)+int(playwright_ts)+int(puppeteer_py)+int(puppeteer_js)+int(puppeteer_ts)+int(cypress_ts)+int(cypress_js)+int(jmeter)+int(locust_java)+int(locust_py)
        #comments = row_js[16]+";"+row_py[10]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data




    @staticmethod
    def get_data_js_java(row_js,row_java):
        repository = row_js[0]
        selenium_java = row_java[3]
        selenium_js = row_js[3]
        selenium_ts = row_js[4]
        selenium_py = 0
        playwright_java = row_java[4]
        playwright_js = row_js[5]
        playwright_ts = row_js[6]
        playwright_py = 0
        puppeteer_js = row_js[7]
        puppeteer_ts = row_js[8]
        puppeteer_py = 0
        cypress_js = row_js[9]
        cypress_ts = row_js[10]
        locust_java = row_java[2]
        locust_py = 0
        jmeter = row_js[1]
        with_junit = row_java[5]
        with_testng = row_java[6]
        with_jest = row_js[11]
        with_mocha = row_js[12]
        with_jasmine = row_js[13]
        with_pytest = 0
        with_unittest = 0
        number_of_test = int(row_js[14])+int(row_java[7])
        number_of_file =int(selenium_java)+int(selenium_js)+int(selenium_ts)+int(selenium_py)+int(playwright_java)+int(playwright_py)+int(playwright_js)+int(playwright_ts)+int(puppeteer_py)+int(puppeteer_js)+int(puppeteer_ts)+int(cypress_ts)+int(cypress_js)+int(jmeter)+int(locust_java)+int(locust_py)

        #comments = row_js[16]+";"+row_java[9]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data



    @staticmethod
    def get_data_py_java_intersect (row_py,row_java):
        repository = row_py[0]
        selenium_java = row_java[3]
        selenium_js = 0
        selenium_ts = 0
        selenium_py = row_py[3]
        playwright_java = row_java[4]
        playwright_js = 0
        playwright_ts = 0
        playwright_py = 0
        puppeteer_js = 0
        puppeteer_ts = 0
        puppeteer_py = row_py[5]
        cypress_js = 0
        cypress_ts = 0
        locust_java = row_java[2]
        locust_py = row_py[2]
        jmeter = row_py[1]
        with_junit = row_java[5]
        with_testng = row_java[6]
        with_jest = 0
        with_mocha = 0
        with_jasmine =0
        with_pytest = row_py[6]
        with_unittest = row_py[7]
        number_of_test = int(row_java[7]) + int(row_py[8])
        number_of_file =int(selenium_java)+int(selenium_js)+int(selenium_ts)+int(selenium_py)+int(playwright_java)+int(playwright_py)+int(playwright_js)+int(playwright_ts)+int(puppeteer_py)+int(puppeteer_js)+int(puppeteer_ts)+int(cypress_ts)+int(cypress_js)+int(jmeter)+int(locust_java)+int(locust_py)
        #comments = row_java[9] + ";" + row_py[10]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data

    @staticmethod
    def get_data_py_only(row):
        repository = row[0]
        selenium_java = 0
        selenium_js = 0
        selenium_ts = 0
        selenium_py = row[3]
        playwright_java = 0
        playwright_js = 0
        playwright_ts = 0
        playwright_py = row[4]
        puppeteer_js = 0
        puppeteer_ts = 0
        puppeteer_py = row[5]
        cypress_js = 0
        cypress_ts = 0
        locust_java = 0
        locust_py = row[2]
        jmeter = row[1]
        with_junit = 0
        with_testng = 0
        with_jest = 0
        with_mocha = 0
        with_jasmine = 0
        with_pytest = row[6]
        with_unittest = row[7]
        number_of_test = row[8]
        number_of_file = row[9]
        #comments = row[10]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data

    @staticmethod
    def get_data_java_only(row):
        repository = row[0]
        selenium_java = row[3]
        selenium_js = 0
        selenium_ts = 0
        selenium_py = 0
        playwright_java = row[4]
        playwright_js = 0
        playwright_ts = 0
        playwright_py = 0
        puppeteer_js = 0
        puppeteer_ts = 0
        puppeteer_py = 0
        cypress_js = 0
        cypress_ts = 0
        locust_java = 0
        locust_py = row[2]
        jmeter = row[1]
        with_junit = row[5]
        with_testng = row[6]
        with_jest = 0
        with_mocha = 0
        with_jasmine = 0
        with_pytest = 0
        with_unittest = 0
        number_of_test = row[7]
        number_of_file = row[8]
        #comments = row[9]

        data = [
            repository,
            selenium_java,
            selenium_js,
            selenium_ts,
            selenium_py,
            playwright_java,
            playwright_js,
            playwright_ts,
            playwright_py,
            puppeteer_js,
            puppeteer_ts,
            puppeteer_py,
            cypress_js,
            cypress_ts,
            locust_java,
            locust_py,
            jmeter,
            with_junit,
            with_testng,
            with_jest,
            with_mocha,
            with_jasmine,
            with_pytest,
            with_unittest,
            number_of_test,
            number_of_file
            #comments
        ]
        return data

    @staticmethod
    def write_overall_file():
        py_path = r'/home/sergio/ICST25-E2EMining/py_test_analysis/result.csv'
        js_ts_path= r'/home/sergio/ICST25-E2EMining/js_ts_test_analysis/result.csv'
        java_path = r'/home/sergio/ICST25-E2EMining/java_test_analysis/result.csv'
        res_path = r'/home/sergio/ICST25-E2EMining/overall_csv'
        try:
            #JS
            with open(js_ts_path, mode ='r',newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                row_num = sum(1 for row in file)
                if row_num <= 1:
                    print(file)
                file.seek(0)
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    repo = row[0]
                    if repo in AggregateData.overall_intersect:
                        java_row = AggregateData.get_row_by_path(repo,java_path)
                        py_row = AggregateData.get_row_by_path(repo,py_path)
                        data = AggregateData.get_data_all_intersect(row,java_row,py_row)
                        #AggregateData.write_resrow_csv_file(res_path,data)
                    elif repo in AggregateData.py_js_intersect:
                        py_row = AggregateData.get_row_by_path(repo,py_path)
                        data = AggregateData.get_data_js_py_intersect(row,py_row)
                        #AggregateData.write_resrow_csv_file(res_path,data)
                    elif repo in AggregateData.js_java_intersect:
                        java_row = AggregateData.get_row_by_path(repo,java_path)
                        data = AggregateData.get_data_js_java(row,java_row)
                        #AggregateData.write_resrow_csv_file(res_path,data)
                    else:
                        data = AggregateData.get_data_js_only(row)
                        if len(data) == 0:
                            print('empty')
                        AggregateData.write_resrow_csv_file(res_path,data)
        except FileNotFoundError:
            print(f"Il file non è stato trovato {file}")
        except csv.Error as e:
            print(f"Errore durante la lettura del file CSV: {e}")

            #PY
        try:
            with open (py_path, mode ='r', newline='',encoding='utf-8') as file_py:
                reader = csv.reader(file_py)
                row_num = sum(1 for row in file_py)
                print(row_num)
                if row_num <= 1:
                    print(file)
                reader = csv.reader(file_py)
                file_py.seek(0)
                next(reader)
                for row in reader:
                    repo = row[0]
                    if repo in AggregateData.py_java_intersect:
                        java_row = AggregateData.get_row_by_path(repo,java_path)
                        data = AggregateData.get_data_py_java_intersect(row,java_row)
                        #AggregateData.write_resrow_csv_file(res_path,data)
                    elif repo not in AggregateData.py_js_intersect and repo not in AggregateData.overall_intersect:
                        data = AggregateData.get_data_py_only(row)
                        if len(data) == 0:
                            print('empty')
                        AggregateData.write_resrow_csv_file(res_path,data)
        except FileNotFoundError:
            print(f"Il file non è stato trovato {file_py}")
        except csv.Error as e:
            print(f"Errore durante la lettura del file CSV: {e}")
        #JAVa
        try:
            with open(java_path, mode='r', newline='', encoding='utf-8') as file_java:
                reader = csv.reader(file_java)
                row_num= sum(1 for row in file_java)
                if row_num <= 1:
                    print(file)
                file_java.seek(0)
                reader = csv.reader(file_java)
                next(reader)
                for row in reader:
                    repo = row[0]
                    if repo not in AggregateData.py_java_intersect and repo not in AggregateData.js_java_intersect and  repo not in AggregateData.overall_intersect:
                        data = AggregateData.get_data_java_only(row)
                        if len(data) == 0:
                            print('empty')
                        AggregateData.write_resrow_csv_file(res_path, data)
        except FileNotFoundError:
            print(f"Il file non è stato trovato {file_java}")
        except csv.Error as e:
            print(f"Errore durante la lettura del file CSV: {e}")




py_repos = AggregateData.get_repos_name_by_path(r'/home/sergio/ICST25-E2EMining/py_test_analysis')
js_ts_repos = AggregateData.get_repos_name_by_path(r'/home/sergio/ICST25-E2EMining/js_ts_test_analysis')
java_repos = AggregateData.get_repos_name_by_path(r'/home/sergio/ICST25-E2EMining/java_test_analysis')
#overall_path = r"C:\Users\sergi\Desktop\ICST25-E2EMining\ICST25-E2EMining_results\ICST25-E2EMining\overall_results.csv"
AggregateData.write_overall_file()

'''
print(len(py_repos))
print(len(js_ts_repos))
print(len(java_repos))
print(len(AggregateData.py_js_intersect))
print(len(AggregateData.py_java_intersect))
print(len(AggregateData.overall_intersect))

'''
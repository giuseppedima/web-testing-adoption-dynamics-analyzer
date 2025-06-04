import os

import pandas as pd


class TemporalFrameworkAdoptionAnalysis:



    java_map = {
        'org.seleniumhq.selenium' : 'selenium',
        'com.microsoft.playwright': 'playwright'
    }

    js_map = {
        'selenium' : 'selenium',
        'selenium-webdriver': 'selenium',
        'playwright': 'playwright',
        'puppeteer': 'puppeteer',
        'cypress': 'cypress'
    }

    ts_map ={
        '@types/selenium': 'selenium',
        '@types/selenium-webdriver': 'selenium',
        'playwright': 'playwright',
        '@types/puppeteer': 'puppeteer',
        'cypress': 'cypress'
    }

    py_map ={
        'playwright' : 'playwright',
        'pytest-playwright':'playwright',
        'pyppeteer': 'puppeteer',
        'selenium':'selenium'
    }

    @staticmethod
    def create_array_dist_dep(file_path,language,deps):

        if language  =='java':
            map = TemporalFrameworkAdoptionAnalysis.java_map
        elif language == 'js':
            map = TemporalFrameworkAdoptionAnalysis.js_map
        elif language == 'ts':
            map = TemporalFrameworkAdoptionAnalysis.ts_map
        elif language == 'py':
            map = TemporalFrameworkAdoptionAnalysis.py_map

        df = pd.read_csv(file_path)
        df_invertito = df.iloc[::-1]

        for index, row in df_invertito.iterrows():
            #print(row)  # Stampa la riga o esegui altre operazioni
            file =row.iloc[0]
            commit = row.iloc[1]
            if not pd.isna(row.iloc[2]):
                tools = row.iloc[2].split(";")
                tools_string= ""
                for tool in tools:
                    if tool in map:
                        tools_string+=map[tool]+";"

                if tools_string not in deps['framework'] and tools_string!="":
                    deps['date'].append(commit)
                    deps['framework'].append(tools_string)



    @staticmethod
    def order_deps(deps):
        # Ordinare le date e i framework
        sorted_dates, sorted_frameworks = zip(*sorted(zip(deps['date'], deps['framework'])))

        # Converti le tuple in liste (se necessario)
        deps['date'] = list(sorted_dates)
        deps['framework'] = list(sorted_frameworks)

        # Visualizza i risultati ordinati
        return deps




    @staticmethod
    def build_df_for_gannt_diagram():

        path =f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/file_dep_analysis'
        '''
        if not os.path.exists(path):
            print(f"Il path {path} non esiste.")
            return

        index = 0
        items = os.listdir(path)
        for item in items:
        '''
        res = []
        df = pd.read_csv(
            f'/home/sergio/PycharmProjects/E2E-Miner-A-tool-for-mining-E2E-tests-from-software-repositories/RQ1/repo_to_analyze.csv',
            header=None)
        # for index, row in islice(df.iterrows(), 0, 1):
        for index, row in df.iterrows():
            item = row[0]
            item_path = os.path.join(path, item)
            print(f'{item} : files: {len(os.listdir(item_path))}')
            deps = {
                'date': [],
                'framework': []
            }
            if os.path.exists(item_path+"/java_deps.csv"):
                TemporalFrameworkAdoptionAnalysis.create_array_dist_dep(item_path+"/java_deps.csv",'java',deps)
            if os.path.exists(item_path+"/js_deps.csv"):
                TemporalFrameworkAdoptionAnalysis.create_array_dist_dep(item_path+"/js_deps.csv",'js',deps)
            if os.path.exists(item_path+"/ts_deps.csv"):
                TemporalFrameworkAdoptionAnalysis.create_array_dist_dep(item_path+"/ts_deps.csv",'ts',deps)
            if os.path.exists(item_path+"/py_deps.csv"):
                TemporalFrameworkAdoptionAnalysis.create_array_dist_dep(item_path+"/py_deps.csv",'py',deps)
            if len(deps['date'])>0:
                deps = TemporalFrameworkAdoptionAnalysis.order_deps(deps)
            new_row =[]
            #df.iat[index,0] = item
            new_row.append(item)
            for index_deps in range(len(deps['date'])):
                #df.iat[index,index_deps+1] = "["+deps['date'][index_deps]+"] : "+deps['framework'][index_deps]
                new_row.append("["+deps['date'][index_deps]+"] : "+deps['framework'][index_deps])
            index+=1
            res.append(new_row)
        df = pd.DataFrame(res)
        df.to_excel(path+'/results.xlsx',index=False,header=False)



if __name__ == "__main__":
    TemporalFrameworkAdoptionAnalysis.build_df_for_gannt_diagram()

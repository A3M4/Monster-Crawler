import re
import pandas

path = r"enter the path of the json file you want to parse"

def get_experience_years(file):
    with open(file, encoding = 'utf-8') as f:
        years_list = []
        content = f.read()
        pattern = re.compile(r'.{8}years')
        matches = pattern.findall(content)
        for match in matches:
            match = re.sub("\D","",str(match))
            years_list.append(str(match))
        while '' in years_list:    #delete empty elements in list
            years_list.remove('')
        years_list = list(map(int, years_list)) #convert string to int in list
        years_list = [year for year in years_list if year <= 10] #remove unreasonable elements in list
        print(years_list)
        return  years_list


def get_degree(file):
    with open(file, encoding = 'utf-8') as f:
        diploma = []
        bachelordegree = []
        masterdegree = []
        PhD = []
        content = f.read()

        pattern1 = re.compile(r'diploma', flags=re.IGNORECASE)
        matches1 = pattern1.findall(content)
        for match in matches1:
            diploma.append(match)
        print("number of diploma: " + str(len(diploma)))

        pattern2 = re.compile(r'bachelor.{0,5}degree', flags=re.IGNORECASE)
        matches2 = pattern2.findall(content)
        for match in matches2:
            bachelordegree.append(match)
        print("number of bachelor's degree: " + str(len(bachelordegree)))

        pattern = re.compile(r'master.{0,5}degree',flags=re.IGNORECASE)
        matches = pattern.findall(content)
        for match in matches:
            masterdegree.append(match)
        print("number of master's degree: "+str(len(masterdegree)))

        pattern3 = re.compile(r'phd', flags=re.IGNORECASE)
        matches3 = pattern3.findall(content)
        for match in matches3:
            PhD.append(match)
        print("number of PhD: " + str(len(PhD)))

def list_to_csv(list):
    df = pandas.DataFrame(data={"col1": list})
    df.to_csv("experience_years.csv", sep=',', index=False)


def main():
    #list_to_csv(get_experience_years(path))
    get_degree(path)

if __name__ == '__main__':
    main()
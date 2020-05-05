import requests
from bs4 import BeautifulSoup
from statistics import mean
from enum import Enum
import pickle
import os

class Gender(Enum):
    MALE="Férfi"
    FEMALE = "Nő"

def collect_data(path):
    data = []
    for page in range(0,100):
        yield page
        r = requests.get(f"https://koronavirus.gov.hu/elhunytak?page={page}")
        soup = BeautifulSoup(r.content, "html.parser")
            
        num_list = [i.text.strip() for i in soup.findAll('td', {"class": "views-field views-field-field-elhunytak-sorszam"})]
        gender_list = [i.text.strip() for i in soup.findAll('td', {"class": "views-field views-field-field-elhunytak-nem"})]
        age_list = [i.text.strip() for i in soup.findAll('td', {"class": "views-field views-field-field-elhunytak-kor"})]
        illness_list = [i.text.strip() for i in soup.findAll('td', {"class": "views-field views-field-field-elhunytak-alapbetegsegek"})]
        
        if len(num_list) == 0:
            break

        for num, gender, age, illness in zip(num_list, gender_list, age_list, illness_list):
            data.append({"num": int(num),
                         "gender": Gender(gender), 
                         "age": int(age), 
                         "illness": illness})

    with open(path, "wb") as f:
        pickle.dump(data, f)


def get_statistics(path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    values = []
    values.append(("Halálozások száma", len(data)))
    values.append(("Halálozási átlag életkor", round(mean(list(map(lambda x: x['age'], data))), 2)))
    values.append(("Elhunyt nők száma", len([item for item in data if item['gender'] is Gender.FEMALE])))
    values.append(("Elhunyt férfiak száma", len([item for item in data if item['gender'] is Gender.MALE])))
    values.append(("Átlagos halálozási életkor nők esetében", round(mean([item['age'] for item in data if item['gender'] is Gender.FEMALE]), 2)))
    values.append(("Átlagos halálozási életkor férfiak esetében", round(mean([item['age'] for item in data if item['gender'] is Gender.MALE]), 2)))
    
    return values

if __name__ == "__main__":
    p = os.path.join(os.path.abspath(os.path.dirname(__file__)), "covid.dat")
    
    print("Adatok olvasása...")
    for page in collect_data(p):
        print(f"{page}. oldal olvasása...")

    data = get_statistics(p)

    for msg, num in data:
        print(f"{msg:.<50}{num}")

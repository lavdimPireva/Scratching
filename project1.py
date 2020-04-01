from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.keys import Keys
from colorama import init,Fore
import sqlite3
import time
import requests
import datetime
from multiprocessing import Pool

init()
driver = ""
links = []
def searchInLinkedIn(keyword,state):

    isFound = False
    f = open("Book1.csv","r")
    for states in f.readlines():
        if states.split(",")[0] == state:
            isFound = True
            driver = webdriver.Chrome('chromedriver.exe')
            driver.maximize_window()
            driver.get("https://www.linkedin.com/")
            driver.find_element_by_class_name("nav__button-secondary").click()
            driver.find_element_by_id("username").send_keys("flamur.berishaa23@gmail.com")
            driver.find_element_by_id("password").send_keys("123flamuri")
            driver.find_element_by_xpath('//*[@id="app__container"]/main/div/form/div[3]/button').click()

            nameArray = ""
            Emri = ""
            Mbiemri = ""
            Pozita = ""
            Kompania=""
            Domeni = ""
            Email = ""

            for i in range(0,2):

                time.sleep(3)
                driver.get("https://www.linkedin.com/search/results/people/?facetGeoRegion="
                               "%5B%22" + states.split(",")[
                                   1] + "%3A0%22%5D&keywords=" + keyword + "&origin=FACETED_SEARCH&page=" + str(i+1))
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                for x in range(0,20,2):
                    time.sleep(1)
                    value = driver.find_elements_by_class_name('search-result__result-link')[x].get_attribute('href')
                    links.append(value)
    if isFound == False:
        print("Shteti te cilin keni kerkuar nuk gjendet ne listeee !")


    for link in links:
            driver.get(link)
            try:
                nameArray = driver.find_element_by_class_name("t-24").text.split()
            except:
                pass
            try:
                positionAndCompanyArray = driver.find_element_by_class_name("t-18").text.split(" at ")
            except:

                pass
            try:
                Emri = nameArray[0]
            except:
                pass
            try:
                Mbiemri = nameArray[1]
            except:
                pass
            try:
                Pozita = positionAndCompanyArray[0]
            except:
                pass
            try:
                Kompania = positionAndCompanyArray[1]
            except:
                pass
            InsertData(Emri, Mbiemri, Pozita, Kompania, Domeni, Email)
    print("Procesi i marrjes se te dhenave ka perfunduar !")
    print("------------------------------------------------------------------------------------------------------------------------")
    print("Procesi i krijimit te domena-ve filloj : ")
    FindDomains()
    print("Procesi i krijimit te domena-ve perfundoj . ")
    print("------------------------------------------------------------------------------------------------------------------------")
    print("Procesi i krijimit te email-ve filloj : ")
    makeEmail()
    print("Procesi i gjetjes se email-ve perfundoj !")
    print("------------------------------------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------------------------------------")




def InsertData(Emri,Mbiemri,Pozita,Kompania,Domeni,Email):
    conn = sqlite3.connect('ProjektiPython.db')
    query = "INSERT INTO USER(Emri,Mbiemri,Pozita,Kompania,Domeni,Email) " \
            "VALUES" + f"('{Emri}','{Mbiemri}','{Pozita}','{Kompania}','{Domeni}','{Email}')"
    try:
        conn.execute(query)
        conn.commit()
        conn.close()
    except:
        conn.close()
        print("Error")


def FindDomains():
    companies = []
    conn = sqlite3.connect('ProjektiPython.db')
    query = "select DISTINCT Kompania from User"
    data = conn.execute(query)
    for company in data:
        companies.append(company[0])
    p = Pool(4)
    p.map(findDomainByCompany,companies)
    time.sleep(5)
    print("Te dhenat u benen update me sukses!")


def updateDomain(domain,company):
    conn = sqlite3.connect('ProjektiPython.db')
    query = f"UPDATE User set Domeni = '{domain}' where Kompania = '{company}' "
    conn.execute(query)
    conn.commit()
    conn.close()


def findDomainByCompany(company):
    domain = ""
    URL = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + company.split(' ')[0]
    r = requests.get(url=URL)
    data = r.json()
    try:
        domain=data[0]["domain"]
        updateDomain(domain,company)
    except:
        domain="not found"
        updateDomain(domain,company)

def makeEmail():
    arrayFullName = []
    arrayDictionary = {}
    array = []
    conn = sqlite3.connect('ProjektiPython.db')
    query = "SELECT ID  from User"
    data = conn.execute(query)
    rows = data.fetchall()
    for i in rows:
        array.append(i[0])
    process = Pool(4)
    process.map(createEmail,array)


def createEmail(ID):

    conn = sqlite3.connect('ProjektiPython.db')
    query = f"SELECT Emri,Mbiemri,Domeni from User where ID = '{ID}'"
    data = conn.execute(query)
    rows = data.fetchall()
    for x in rows:
        emri = x[0]
        mbiemri = x[1]
        domeni = x[2]
        email = emri + "." + mbiemri + "@" + domeni
        email = email.lower()
        query = f"UPDATE User set Email = '{email}' where ID = '{ID}' "
    conn.execute(query)
    conn.commit()
    conn.close()

def getDataByCompany(company):
    conn = sqlite3.connect("ProjektiPython.db")
    query = "SELECT * FROM user WHERE Kompania like '" + company + "%" + "'"
    data = conn.execute(query)
    rows = data.fetchall()
    count = len(rows)
    if count > 0 :
        for company in rows:
            print(Fore.RED + "Emri: " + Fore.GREEN + company[1] + "\n"
                  + Fore.RED + "Mbiemri: " + Fore.GREEN + company[2] + "\n"
                  + Fore.RED + "Pozita: " + Fore.GREEN + company[3] + "\n"
                  + Fore.RED + "Kompania: " + Fore.GREEN + company[4] + "\n"
                  + Fore.RED + "Domeni: " + Fore.GREEN + company[5] + "\n"
                  + Fore.RED + "Email: " + Fore.GREEN + company[6] + "\n")
    else:
        companyData = Fore.RED + "Asnje rezultat nuk eshte gjetur me kompanin:" + Fore.GREEN + company
        print(companyData)
        return companyData


def getDataByPosition(position):
    conn = sqlite3.connect("ProjektiPython.db")
    query = "SELECT * FROM user WHERE Pozita like '" + position + "%"  + "'"
    data = conn.execute(query)
    rows = data.fetchall()
    count = len(rows)
    if count > 0:
        for position in rows:
            print(Fore.RED + "Emri: " + Fore.GREEN + position[1] + "\n"
                  + Fore.RED + "Mbiemri: " + Fore.GREEN + position[2] + "\n"
                  + Fore.RED + "Pozita: " + Fore.GREEN + position[3] + "\n"
                  + Fore.RED + "Kompania: " + Fore.GREEN + position[4] + "\n"
                  + Fore.RED + "Domeni: " + Fore.GREEN + position[5] + "\n"
                  + Fore.RED + "Email: " + Fore.GREEN + position[6] + "\n")
    else:

        positionData = Fore.RED + "Asnje rezultat nuk eshte gjetur me poziten:" + Fore.GREEN + position
        print(positionData)
        return positionData


def getDataByName(name):
    conn = sqlite3.connect("ProjektiPython.db")
    query = "SELECT DISTINCT * FROM user WHERE emri = '" + name + "'"
    data = conn.execute(query)
    rows = data.fetchall()
    count = len(rows)
    if count > 0:
        for name in rows:
            print(Fore.RED + "Emri: " + Fore.GREEN + name[1] + "\n"
                  + Fore.RED + "Mbiemri: " + Fore.GREEN + name[2] + "\n"
                  + Fore.RED + "Pozita: " + Fore.GREEN + name[3] + "\n"
                  + Fore.RED + "Kompania: " + Fore.GREEN + name[4] + "\n"
                  + Fore.RED + "Domeni: " + Fore.GREEN + name[5] + "\n"
                  + Fore.RED + "Email: " + Fore.GREEN + name[6] + "\n")
    else:
        noData = Fore.RED + "Asnje rezultat nuk eshte gjetur me emrin:" + Fore.GREEN +  name
        print(noData)
        return noData


def writeToCsvFileByCompany(company):
    conn = sqlite3.connect("ProjektiPython.db")
    query = "SELECT * FROM user WHERE Kompania = '" + company + "'"
    data = conn.execute(query)
    rows = data.fetchall()
    count = len(rows)
    f = open("Company.csv", "a")
    if count > 0 :
        for item in rows:
            Emri = item[1]
            Mbiemri = item[2]
            Pozita = item[3]
            Kompania = item[4]
            Domeni = item[5]
            Email = item[6]
            f.write(f"{Emri},{Mbiemri},{Pozita},{Kompania},{Domeni},{Email}\n")
    print(f"Te dhenat nga kompania : {company} ,  u ruajten ne csv file me sukses ! ")
    f.close()


def writeToCsvFileByPosition(position):
    conn = sqlite3.connect("ProjektiPython.db")
    query = "SELECT * FROM user WHERE Pozita = '" + position + "'"
    data = conn.execute(query)
    rows = data.fetchall()
    count = len(rows)
    f = open("Position.csv", "a",encoding="UTF-8")
    if count > 0 :
        for item in rows:
            Emri = item[1]
            Mbiemri = item[2]
            Pozita = item[3]
            Kompania = item[4]
            Domeni = item[5]
            Email = item[6]
            f.write(f"{Emri},{Mbiemri},{Pozita},{Kompania},{Domeni},{Email}\n")
    print(f"Te dhenat nga pozita : {position} , u ruajten ne csv file me sukses ! ")
    f.close()


def writeToCsvFileByName(name):
    conn = sqlite3.connect("ProjektiPython.db")
    query = "SELECT * FROM user WHERE Emri = '" + name + "'"
    data = conn.execute(query)
    rows = data.fetchall()
    count = len(rows)
    f = open("name.csv", "a")
    if count > 0 :
        for item in rows:
            Emri = item[1]
            Mbiemri = item[2]
            Pozita = item[3]
            Kompania = item[4]
            Domeni = item[5]
            Email = item[6]
            f.write(f"{Emri},{Mbiemri},{Pozita},{Kompania},{Domeni},{Email}\n")
    print(f"Te dhenat nga emri : {name} , u ruajten ne csv file me sukses ! ")
    f.close()


def searchAboutName():
    while True:
        nameForSearch = input("Jepni emrin qe deshironi ta kerkoni : ")
        nameForSearch = nameForSearch.lower().strip().capitalize()
        nameData = getDataByName(nameForSearch)
        if nameData is None:
            csvFileForName = input(
                Fore.BLACK + "A deshironi qe te dhenat e paraqitura ti ruani ne nje CSV file ?  P ose J ?")
            csvFileForName = csvFileForName.lower().strip()
            if csvFileForName == 'p':
                writeToCsvFileByName(nameForSearch)
                x = input(Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te emrit? , P ose J ").lower()
                if x == 'p':
                    pass
                else:
                    break
            else:
                x = input(Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te emrit? , P ose J ").lower()
                if x == 'p':
                    pass
                else:
                    break
        else:
            x = input(Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te emrit? , P ose J ").lower()
            if x == 'p':
                pass
            else:
                break


def searchAboutPosition():
    while True:
        positionForSearch = input("Jepni poziten qe deshironi ta kerkoni : ")
        positionForSearch = positionForSearch.lower().strip().capitalize()
        positionData = getDataByPosition(positionForSearch)
        if positionData is None:
            csvFileForPosition = input(
                Fore.BLACK + "A deshironi qe te dhenat e paraqitura ti ruani ne nje CSV file ?  P ose J ?")
            csvFileForPosition = csvFileForPosition.lower().strip()
            if csvFileForPosition == 'p':
                writeToCsvFileByPosition(positionForSearch)
                x = input(
                    Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te pozites? , P ose J ").lower()
                if x == 'p':
                    pass
                else:
                    break
            else:
                x = input(
                    Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te pozites? , P ose J ").lower()
                if x == 'p':
                    pass
                else:
                    break
        else:
            x = input(Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te pozites? , P ose J ").lower()
            if x == 'p':
                pass
            else:
                break


def searchAboutCompany():
    while True:
        companyForSearch = input("Jepni kompanine qe deshironi ta kerkoni : ")
        companyForSearch = companyForSearch.lower().strip().capitalize()
        companyData = getDataByCompany(companyForSearch)
        if companyData is None:
            csvFileForCompany = input(
                Fore.BLACK + "A deshironi qe te dhenat e paraqitura ti ruani ne nje CSV file ?  P ose J ?")
            csvFileForCompany = csvFileForCompany.lower().strip()
            if csvFileForCompany == 'p':
                writeToCsvFileByCompany(companyForSearch)
                x = input(
                    Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te kompanise? , P ose J ").lower()
                if x == 'p':
                    pass
                else:
                    break
            else:
                x = input(
                    Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te kompanise? , P ose J ").lower()
                if x == 'p':
                    pass
                else:
                    break
        else:
            x = input(Fore.BLACK + "A deshironi te vashdoni me kerkim ne baze te kompanise? , P ose J ").lower()
            if x == 'p':
                pass
            else:
                break


if __name__ == "__main__":
    print(Fore.MAGENTA + "          Mirsevini ne aplikacionin Python Programming !!"                               )
    print("-------------------------------------------------------------------------------------------------------------")
    print ("Shtypni:")
    print ("1 : Per te bere search ne Linkedin .")
    print("2 : Per te kerkuar puntoret .")
    print("0 : Per te ndalur programin .")
    while True:
        messageNr = input(Fore.GREEN + "Shkruaj njeren nga opsionet : ")
        if messageNr is "0":
            exit()
        elif messageNr is "1":
            keyword = input("Shkruaj keywordin:")
            state = input("Shkruani shtetin :  ")
            searchInLinkedIn(keyword.strip(),state.strip())
        elif messageNr is "2":
            print("Opsionet per te kerkuar puntoret jane : \n" +
                  "1 : Sipas emrit , \n" +
                  "2 : Sipas pozites , \n" +
                  "3 : Sipas kompanis .")
            opsioni = input("Jepni opsionin tuaj:")
            if opsioni=="1":
                searchAboutName()
            elif opsioni=="2":
                searchAboutPosition()
            elif opsioni=="3":
                searchAboutCompany()








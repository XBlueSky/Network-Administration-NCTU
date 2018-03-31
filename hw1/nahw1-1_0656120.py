from argparse import ArgumentParser
from PIL import Image, ImageEnhance
from bs4 import BeautifulSoup
import prettytable as pt
import getpass
import requests
import pytesseract
import numpy as np

parser = ArgumentParser(description= "Web crawler for NCTU class schedule")
parser.add_argument("username", help="username for NCTU portal")
args = parser.parse_args()

session = requests.Session()

def getTable(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = pt.PrettyTable()

    # find title
    dayOfWeek = soup.find_all('td', class_='dayOfWeek')
    titleList = []
    for tag in dayOfWeek:
        titleList.append(tag.font.string)
    table.field_names = titleList

    # find course row
    courseRow = soup.find_all('td', class_=['liststyle1','liststyle2'])
    row = []
    for tag in courseRow:
        string = tag.font.get_text(" ", strip=True)
        row.append(string)

        # row claer until input 9 items
        if len(row) == 9:
            table.add_row(row)
            row.clear()
    print(table)

def loginPreprocess():
    # get captcha and use gray scale method
    l = session.get('https://portal.nctu.edu.tw/captcha/pic.php', stream=True)
    with open('captcha.png', 'wb') as f:
        f.write(l.content)
    captcha = Image.open("captcha.png")
    greyImage = captcha.convert('L')
    greyImage.save("greyImage.png")

    # check which kind of images to be prepocess
    if l.url.find("cool-php-captcha") != -1 :
        opt = greyImage
        opt.save("opt.png")  
        
    elif l.url.find("pitctest") != -1 :
        threshold = 99 
        table = []  
        for i in range(256):  
            if i < threshold:  
                table.append(0)  
            else:  
                table.append(1)  
        opt = greyImage.point(table,'1') 
        opt.save("opt.png")

    elif l.url.find("claviska-simple-php-captcha") != 1 :
        data = np.asarray(greyImage)
        counts = np.bincount(data.ravel())
        threshold = np.argmax(counts)
        table = []  
        for i in range(256):  
            if  threshold-20 <= i <= threshold+2 :  
                table.append(0)  
            else:  
                table.append(1) 
        opt = greyImage.point(table,'1') 
        opt.save("opt.png")
    
    else:
        return "False"
    #print(pytesseract.image_to_string(opt, config='outputbase digits'))
    return pytesseract.image_to_string(opt, config='outputbase digits')

def webCrawler(username, password):

    loginparams = {
        'username':username,
        'Submit2':'%E7%99%BB%E5%85%A5%28Login%29',
        'pwdtype':'static',
        'password':password,
        'seccode':loginPreprocess()
    }
    jwtdata = {}

    # last check the result of pytesseract
    flag = True
    while (True):
        if len(loginparams['seccode']) != 4:
            loginparams['seccode'] = loginPreprocess()
            continue
        for char in loginparams['seccode']:
            if char.isdigit() == False:
                loginparams['seccode'] = loginPreprocess()
                flag = False
                break
        if flag:
            break

    # first log in to chkpas.php(post)
    response = session.post('https://portal.nctu.edu.tw/portal/chkpas.php?', data = loginparams)

    # find the hidden data 
    my_params = {'D': 'cos'}
    response = session.get('https://portal.nctu.edu.tw/portal/relay.php', params = my_params)
    response.encoding = 'utf-8'

    # store data as jwtdata
    soup = BeautifulSoup(response.text, 'html.parser')
    for value in soup.find_all('input'):
        if value['id'] != 'Chk_SSO':
            jwtdata[value['id']] = value['value']
        else :
            jwtdata[value['id']] = 'on'
    
    # key path : post jwt.asp with jwtdata to get cookies
    response = session.post('https://course.nctu.edu.tw/jwt.asp', data = jwtdata)
    
    # get course shedule and return html
    response = session.get('https://course.nctu.edu.tw/adSchedule.asp')
    response.encoding = 'big5'
    return response.text

if __name__ == '__main__':
    username = args.username
    password = getpass.getpass('password: ')
    getTable(webCrawler(username, password))
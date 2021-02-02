import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
sess = requests.Session()
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


date_mappings = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def get_ture_time(text):
    "Feb 20 at 12:00AM"
    parts = text.split(" ")
    month = date_mappings[parts[0].lower()]
    day = parts[1]
    hour = parts[-1].split(":")[0]
    diff = 0 if "am" in parts[-1].lower() else 12
    minute = parts[-1].split(":")[1][:2]
    strs = f"{datetime.datetime.now().year}-{month}-{day}-{int(hour)+diff}:{minute}"
    date = datetime.datetime.strptime(strs,'%Y-%m-%d-%H:%M')
    return get_cn_time(date)

def get_cn_time(date):
    if date.month == 3:
        if date.day>=11:
            d = 15
        else:
            d = 16
    elif date.month == 11:
        if date.day<=7:
            d = 15
        else:
            d = 16
    elif date.month>3 and date.month<11:
        d = 15
    else:
        d = 16
    delta = datetime.timedelta(hours = d)
    cur = date + delta
    dd = datetime.datetime.now()+ datetime.timedelta(days = 7) - cur
    if dd.days>=0 and dd.days< 7:
        return True, cur
    return False, cur

    
def get_authenticity_token():
    url = "https://www.gradescope.com/"
    resp = sess.get(url)
    soup = BeautifulSoup(resp.text)
    #print("index:",resp)
    authenticity_token = soup.find("input", attrs={"name":"authenticity_token"}).get("value")
    return authenticity_token

def login(token):
    cookies = {
    }

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://www.gradescope.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.gradescope.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }

    data = {
      'utf8': '\u2713',
      'authenticity_token': token,
      'session[email]': 'your_email_here',
      'session[password]': 'your_password_here',
      'session[remember_me]': '0',
      'commit': 'Log In',
      'session[remember_me_sso]': '0'
    }

    response = sess.post('https://www.gradescope.com/login', headers=headers, cookies=cookies, data=data)
    return response


def get_all_course():
    resp = sess.get("https://www.gradescope.com/account")
    soup = BeautifulSoup(resp.text, 'lxml')
    clist = soup.find("div", attrs={"class":"courseList--coursesForTerm"})
    alist = clist.find_all("a")
    for a in alist:
        title = a.find("h3",attrs = {"class":"courseBox--shortname"}).text
        url = a.get("href")
        url = urljoin("https://www.gradescope.com/account", url)
        yield url, title

    
        
def get_cur_term(url):
    resp = sess.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    trlist = soup.find_all("tr", attrs={"role":"row"})[1:]
    results = []
    for tr in trlist:
        status = tr.find("div",attrs={"class":"submissionStatus--text"})
        if not status:
            continue
        name = tr.find("th").text
        datespan = tr.find("span", attrs={"class":"submissionTimeChart--dueDate"}).text
        if "no" not in status.text.lower():
            continue
        right,date = get_ture_time(datespan)
        #print(right,date)
        item = {
            "name":name,
            "date":date
        }
        right and results.append(item)
    return results
        
        
def get_all_data():
    all_items = []
    for url,title in get_all_course():
        #print(url, title)
        items = get_cur_term(url)
        for it in items:
            it['title'] = title
            all_items.append(it)
    return all_items

def run_once(retry=20):
    if retry == 0 :
        return "Error occurred when attempting to retrieve the data"
    try:
        authenticity_token = get_authenticity_token()
        #print(authenticity_token)
        resp= login(authenticity_token)
        items = get_all_data()
        if not items:
            return "Hi Sean, nothing for next week. Congratulations"
        message = "Hi Sean, here are your upcoming deadlines:\n"
        i = 1
        items.sort(key = lambda x: x['date']) 
        """
        times = []
        for item in items:
            print(item['name'])
            times.append(item['date'])
        times.sort()
        print(times)
        """
        for item in items:
            message += (str(i) + ": ")
            message += f"{item['title']},\n"
            message += f"   {item['name']},\n"
            message += f"   {item['date'].strftime('%m-%d %H:%M')}\n"
            i+=1
                #break
        return message
    except:
        import traceback
        #print(traceback.format_exc())
        return run_once(retry-1)


def run_loop():
    filename = "./tmp.txt"
    msg = run_once()
    #print(msg)
    with open(filename, "w") as f:
        f.write(msg)

scheduler = BlockingScheduler()
scheduler.add_job(run_loop, 'cron', hour=6, minute=0)
#scheduler.add_job(run_loop)
scheduler.start()

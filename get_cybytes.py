#!/usr/bin/env python

#import time, pycurl, cStringIO, subprocess, sys, requests
import time, subprocess, sys, requests, json
from bs4 import BeautifulSoup

cybpath = <absolute_path_of_the_directory_with_a_slash_at_end>
logfile = cybpath + 'cybrary.log'
schfile = cybpath + 'reschedule_jobs'
conffile = cybpath + 'conf.json'
user = ''
password = ''

def fetch_last_cyb():
    
    global logfile
    with open(logfile, 'r+') as f:
        #seek the last 4 chars of the file
        f.seek(-4, 2)
        #remove the last char which is \n
        cyb = int(f.readline()[:-1])
        return cyb
    f.close()    

def read_conf():

    global user, password
    with open(conffile) as f:
        data = json.load(f)
    f.close()
    user = data['user']
    password = data['password']

read_conf()
lurl = 'https://www.cybrary.it/wp-login.php/'
turl = 'https://www.cybrary.it/api/verify-auth/'
furl = 'https://www.cybrary.it/members/' + user + '/'
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
output = "Updating cybytes on " + time.strftime("%c") + "\n"

def append_log(out):

    global logfile
    with open(logfile, 'a+') as f:
        f.write(out)
    f.close()    

def create_payload():

    global user, password
    payload = {
            'log': user,
            'pwd': password,
            'wp-submit': 'Log In',
            'redirect_to': 'https://www.cybrary.it/',
            'testcookie': 1
            }
    return payload

def login():

    global user, password, lurl, turl
    logged_in = False
    out = "Logging In...\n"
    soup = ""
    s = requests.session()
    payload = create_payload()

    try:
        r = s.get(lurl) #create cookies and headers
        if r.status_code != 200:
            out += "Error while setting cookies!! Status Code: " + str(r.status_code) + '\n'
            return(s, logged_in, soup, out)
        out += "Cookies set successfully!!\n"
    except:
        e = sys.exc_info()
        out += "Could not fetch login page!!\nError: " + str(e[0]) + " " + str(e[1]) + '\n'
        return(s, logged_in, soup)
    
    out += "Authenticating...\n"
    try:
        res_auth = s.post(lurl, data = payload) #authenticate
        if res_auth.status_code != 200:
            out += "Error while sending auth data!! Status Code: " + str(res_auth.status_code) + '\n'
            return(s, logged_in, soup, out)
        out += "Auth data sent successfully!!\n"
    except:
        e = sys.exc_info()
        out += "Could not send auth data!!\nError: " + str(e[0]) + " " + str(e[1]) + '\n' 
        return(s, logged_in, soup)

    out += "Verifying authentication...\n"
    try:
        res_verify = s.post(turl) #test authentication
        if res_verify.status_code != 200:
            out += "Error while verifying auth!! Status Code: " + str(res_verify.status_code) + '\n'
            return(s, logged_in, soup, out)
        if res_verify.content == 'false':
            out += "Authentication Failure!! Unknown Error!!"
        else:
            #d = json.loads(res_verify.content) #convert response to dictionary
            logged_in = True
            out += "Authentication Successful!!\n"
    except:
        e = sys.exc_info()
        out += "Authentication Failure!!\nError: " + str(e[0]) + " " + str(e[1]) + '\n'
    soup = BeautifulSoup(res_verify.content, 'html.parser')

    return (s, logged_in, soup, out)

def fetch_cybytes(s):
    
    global furl
    fetched = False
    cybytes = 0
    soup = ""
    out = "Fetching updated cybytes...\n"
    try:
        res_fetch = s.get(furl)
        soup = BeautifulSoup(res_fetch.content, 'html.parser')
        try:
            cybytes = int(soup.find("img", {"src" : "/wp-content/themes/cybrary/img/profilev3/cybytes.png"}).text)
            fetched = True
            out += "Cybytes Fetched Successfully!!\n"
        except:
            e = sys.exc_info()
            out += "Parsing error while fetching cybytes!!\nError: " + str(e[0]) + " " + str(e[1]) + '\n'
    except:
        e = sys.exc_info()
        out += "Error while fetching cybytes!!\nError: " + str(e[0]) + " " + str(e[1]) + '\n'

    return (fetched, cybytes, soup, out)
    return (fetched, cybytes, soup, out)

def main():

    global cybpath, logfile, schfile, last_cyb, user, password, lurl, turl, furl, data, ua, output
    last_cyb = fetch_last_cyb()
    read_conf()
    s, logged_in, soupl, out = login()
    cybytes = last_cyb
    output += out
    if logged_in:
        fetched, cyb, soupf, out = fetch_cybytes(s)
        output += out
        if fetched:
            cybytes = cyb
    	    output += "Running Scheduler\n"
    	    subprocess.call(schfile)
    	    output += "Job Rescheduled\n"
    output += "Cybytes: " + str(cybytes) + "\n"
    append_log(output)
    return output

def test_main():

    global cybpath, logfile, schfile, last_cyb, user, password, lurl, turl, furl, data, ua, output
    last_cyb = fetch_last_cyb()
    read_conf()
    s, logged_in, soupl, out = login()
    cybytes = last_cyb
    output += out
    if logged_in:
        fetched, cyb, soupf, out = fetch_cybytes(s)
        output += out
        if fetched:
            cybytes = cyb
    	    output += "Running Scheduler\n"
    	    output += "Job Rescheduled\n"
    output += "Cybytes: " + str(cybytes) + "\n"
    return output

if __name__ == '__main__':
    main()


"""
def login(login_url, iurl, data, ua):
    out = "Logging In..." + "\n"
    soup = ""
    cybytes = 0
    headers = cStringIO.StringIO()
    bodyl = cStringIO.StringIO()
    bodyf = cStringIO.StringIO()

    c = create_curl_obj(login_url, data, ua)
    c.setopt(c.HEADERFUNCTION, headers.write)
    c.setopt(c.WRITEFUNCTION, bodyl.write)
    
    try:
    	c.perform()
    except pycurl.error, e:
    	out += "Unexpected error while logging in: " + str(e[0]) + " " + str(e[1]) + "\n"
    	cybytes = -1
    	return (out, cybytes, soup)

    lstatus = c.getinfo(pycurl.HTTP_CODE)
    if lstatus != 200:
        out += "Error logging in!! Login Status: " + str(lstatus) + "\n"
        return (out, cybytes, soup)

    soupl = BeautifulSoup(bodyl.getvalue(), 'html.parser')
    #headers = cStringIO.StringIO()
    #modify options for fetching an inside url which should 
    #be accessible only after a successful authorization
    c.setopt(c.URL, iurl)
    #c.setopt(c.NOBODY, 0)
    c.setopt(c.HTTPGET, 1)
    c.setopt(c.WRITEFUNCTION, bodyf.write)
    try:
    	c.perform()
    except pycurl.error, e:
    	out += "Unexpected error while fetching: " + str(e[0]) + " " + str(e[1]) + "\n"
    	cybytes = -1
    	return (out, cybytes, soupl)
    		
    fstatus = c.getinfo(pycurl.HTTP_CODE)
    if(fstatus != 200):
        out += "Error while fetching!! Fetch Status: " + str(fstatus) + "\n"
        return (out, cybytes, soupl)
    soupf = BeautifulSoup(bodyf.getvalue(), 'html.parser')
    try:
        cybytes_list = soupf.find_all("div", class_="cybytes")
        cybytes = int(cybytes_list[0].text.strip())
        out += "Login Successful!!" + "\n"
    except:
        e = sys.exc_info()
        out += "Parsing error while fetching!!\nError: " + str(e[0]) + " " + str(e[1])
        cybytes = -1
    return (out, cybytes, (soupl, soupf))
"""

"""
def create_curl_obj(login_url, data, ua):
    
    #set options for login
    c = pycurl.Curl()
    c.setopt(c.URL, login_url)
    #c.setopt(c.PROXY, 'https://proxy.iiit.ac.in:8080')
    c.setopt(c.POSTFIELDS, data)
    # Follow redirects
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.USERAGENT, ua)
    c.setopt(c.HEADER, 1)
    #c.setopt(c.NOBODY, 1)#header only, no body
    #c.setopt(c.VERBOSE, True)
    #When we set cookiefile value to an empty string,then cURL is 
    #made cookie-aware, and will catch cookies and re-send cookies
    #upon subsequent requests. Hence, we can keep state between 
    #requests on the same cURL handle intact.
    c.setopt(c.COOKIEFILE, '')
    return c
"""

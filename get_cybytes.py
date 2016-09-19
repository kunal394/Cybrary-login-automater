#!/usr/bin/env python

import time, pycurl, cStringIO, subprocess
from bs4 import BeautifulSoup

def append_log(out, file):
    with open(file, 'a+') as f:
        f.write(out)
    f.close()    

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
    """When we set cookiefile value to an empty string,then cURL is 
    made cookie-aware, and will catch cookies and re-send cookies
    upon subsequent requests. Hence, we can keep state between 
    requests on the same cURL handle intact."""
    c.setopt(c.COOKIEFILE, '')
    return c

def fetch_last_cyb(file):
    with open(file, 'r+') as f:
        #seek the last 4 chars of the file
        f.seek(-4, 2)
        #remove the last char which is \n
        cyb = int(f.readline()[:-1])
        return cyb
    f.close()    

def login(login_url, iurl, data, ua):
    out = "Logging In..." + "\n"

    cybytes = 0
    headers = cStringIO.StringIO()
    body = cStringIO.StringIO()

    c = create_curl_obj(login_url, data, ua)
    c.setopt(c.HEADERFUNCTION, headers.write)
    
    try:
    	c.perform()
    except pycurl.error, e:
    	out += "Unexpected Error: " + str(e[0]) + " " + str(e[1]) + "\n"
    	cybytes = -1
    	return (out, cybytes)

    lstatus = c.getinfo(pycurl.HTTP_CODE)
    if lstatus != 200:
        out += "Error logging in!! Login Status: " + str(lstatus) + "\n"
        return (out, cybytes)

    #headers = cStringIO.StringIO()
    #modify options for fetching an inside url which should 
    #be accessible only after a successful authorization
    c.setopt(c.URL, iurl)
    #c.setopt(c.NOBODY, 0)
    c.setopt(c.HTTPGET, 1)
    c.setopt(c.WRITEFUNCTION, body.write)
    try:
    	c.perform()
    except pycurl.error, e:
    	out += "Unexpected Error: " + str(e[0]) + " " + str(e[1]) + "\n"
    	cybytes = -1
    	return (out, cybytes)
    		
    fstatus = c.getinfo(pycurl.HTTP_CODE)
    if(fstatus != 200):
        out += "Error logging in!! Fetch Status: " + str(fstatus) + "\n"
        return (out, fstatus, cybytes)
    soup = BeautifulSoup(body.getvalue(), 'html.parser')
    cybytes = int(soup.find("div", {"class": "cybytenumber"}).text.strip())
    out += "Login Successful!!" + "\n"
    return (out, cybytes)

def main():
    cybpath = <absolute_path_of_your_folder>
    logfile = cybpath + 'cybrary.log'
    schfile = cybpath + 'reschedule_jobs'
    last_cyb = fetch_last_cyb(logfile)
    user = <your_username>
    password = <your_password>
    login_url = 'https://www.cybrary.it/wp-login.php'
    iurl = 'https://www.cybrary.it/members/' + user + '/messages'
    data = 'log=' + user + '&pwd=' + password + '&wp-submit=Log+In&redirect_to=&testcookie=1'
    ua = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; it; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729)'
    
    output = "Updating cybytes on " + time.strftime("%c") + "\n"
    
    #check login
    out, cybytes = login(login_url, iurl, data, ua)
    output += out
    if cybytes == 0 or cybytes == -1:
        output += "Cybytes: " + str(last_cyb) + "\n"
    else:
    	output += "Running Scheduler\n"
    	subprocess.call(schfile)
    	output += "Job Rescheduled\n"
    	output += "Cybytes: " + str(cybytes) + "\n"    
    #print output
    append_log(output, logfile)


if __name__ == '__main__':
    main()

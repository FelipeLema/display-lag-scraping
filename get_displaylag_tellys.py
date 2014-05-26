'''Gets monitor info from displaylag.com and a few more

See http://forums.shoryuken.com/discussion/comment/8676004#Comment_8676004
'''
import urllib
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
fields = ['brand',   'size',    'model',   'resolution','screen_type','input_lag']
tags   = ['column-3','column-2','column-4','column-5',  'column-8',   'column-10']

def selenium_get_dlcom():
    global fields, tags

    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    base_url = "http://www.displaylag.com"
    verificationErrors = []
    accept_next_alert = True

    driver = driver
    driver.get(base_url + "/display-database/")
    Select(driver.find_element_by_name("tablepress-1_length")).select_by_visible_text("All")

    scr_d=dict()
    for f,t in zip(fields,tags):
        print('fetching {0}'.format(f))
        scr_d[f] = [i.text for i in \
                driver.find_elements_by_class_name(t)][1:]
        '''
        scr_d[f] = [i.text for i in \
                driver.find_elements_by_xpath("//td[@class='{0}']".format(t))][1:]
        '''
    driver.quit()
    return scr_d
 
def get_displaylag_screens(max_screens=30):
    global fields
    by_fields=selenium_get_dlcom()
    l=-1
    for f in fields:
        if l<0:
            l=len(by_fields[f])
        assert l==len(by_fields[f]),'{0} != {1}'.format(l,len(by_fields[f]))
    out=[]
    for i in xrange(l):
        out.append(dict([ \
                (f,by_fields[f][i]) for f in fields]))
    return out
def get_squidoo_monitors():
    '''
    I could've done a parser, but this is a one-time list.
    No use in making it re-runnable
    '''
    data_header = \
            ['brand','size','model','resolution','screen_type','input_lag']
    l = [ \
            'Asus 21.5 VE228H 1x1 monitor 7ms', \
            'BenQ 27 GW2750HM 1X1 monitor 7ms',\
            'Dell 27 S2740L 1x1 monitor 6.3ms',\
            'LG 27 IPS277L-BN 1x1 monitor 6.2ms ',\
            'BenQ 24 GW2450 1920x1080 monitor 4ms',\
            'AOC 23 e2352PHZ 1x1 monitor 5.1ms',\
            'Viewsonic 24 VX2453MH 1920x1080 monitor 4.9ms',\
            'Foris 23 FS2333-BK 1x1 monitor 4.6ms',\
            'Viewsonic 23 VX2370SMH 1920x1080 monitor 4.9ms',\
            'BenQ 24 RL2450HT 1x1 monitor 4.2ms',\
            'Dell 23 S2330MX 1x1 monitor 3.8ms ',\
            'Asus 27 MX279H 1x1 monitor 3.8ms',\
            'Viewsonic 27 VX2770SMH 1x1 monitor 3.5ms',\
            'Acer 27 S27HLbmii 1x1 monitor 3.4ms',\
            'LG 27 VG278HE 1x1 monitor 7.3ms',\
            'LG 27 VG278H 1x1 monitor 6.5ms',\
            'BenQ 24 XL2420T 1x1 monitor 4.9ms',\
            'Asus 24 VG248QE 1x1 monitor 3.1ms',\
            ]
    l = [i.split() for i in l]
    out=[]
    for single in xrange(l):
        if len(single) == 0:
            continue
        out.append(dict([\
                (k,single[idx]) for idx, k in enumerate(data_header)]))
    return out


if __name__ == '__main__':
    for i in get_displaylag_screens()[:12]:
        print i

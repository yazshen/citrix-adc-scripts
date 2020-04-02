import sys, urllib.request, os, subprocess, math, re, time

"""

Author: Robbie Shen
Date: 2020.03.31
Contact: yazhong.shen@citrix.com

Prerequisite:
Install "whois" command first

TODO: 
GenerateCitrixCNIPDB.py ipv4|ipv6

Requirements: Python 3.7.6 or higher

"""

def main() :
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Begin to read IPDB from APNIC...")
    try:
        varApnicDB = urllib.request.urlopen("http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  + " IPDB from APNIC completed!")

        if os.path.exists("APNIC-IPDB-ALL.txt"):
            os.remove("APNIC-IPDB-ALL.txt")
        if os.path.exists("APNIC-IPDB-CN-"+sys.argv[1] + ".txt"):
            os.remove("APNIC-IPDB-CN-"+sys.argv[1] + ".txt")
        if os.path.exists("Citrix-IPDB-CN-"+sys.argv[1] + ".txt"):
            os.remove("Citrix-IPDB-CN-"+sys.argv[1] + ".txt")

        varFileObjectAll = open("APNIC-IPDB-ALL.txt","w")
        varFileObjectCNIP = open("APNIC-IPDB-CN-"+sys.argv[1] + ".txt", "w")
        for varLine in varApnicDB:
            varFileObjectAll.writelines(varLine.decode('utf-8'))
            if varLine.decode('utf-8').find('apnic|CN|'+sys.argv[1]) > -1:
                varFileObjectCNIP.writelines(varLine.decode('utf-8'))
        varFileObjectCNIP.close()
        varFileObjectAll.close()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " DB files dumped")

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Begin to generate Citrix CN IPDB...")
        varFileObjectCitrix = open("Citrix-IPDB-CN-" + sys.argv[1] + ".txt", "w")
        varFileObjectCitrix.write("NSGEO1.0\nContext=custom\nQualifier1=ispname\nStart\n")
        varRetryList = ""
        for varLine in open("APNIC-IPDB-CN-"+sys.argv[1] + ".txt"):
            varTemp1 = varLine.split('|')
            #print(varTemp[3]+"/"+str(int(32-math.log(int(varTemp[4]))/math.log(2))))
            try:
                if sys.argv[1] == "ipv4":
                    varTemp2 = subprocess.check_output(['whois','-h', 'whois.apnic.net',varTemp1[3],'|','grep','-E','"inetnum:|netname:"'], timeout=15).decode('utf-8')
                else:
                    varTemp2 = subprocess.check_output(['whois','-h', 'whois.apnic.net',varTemp1[3],'|','grep','-E','"inet6num:|netname:"'], timeout=15).decode('utf-8')
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Exception: " + "whois -h whois.apnic.net " + varTemp1[3] + " failed!")
                if varRetryList == "":
                    varRetryList = varTemp1[3]
                else:
                    varRetryList = varRetryList + "," + varTemp1[3]
                continue
            if sys.argv[1] == "ipv4":
                varTemp3 = re.search(r'inetnum:        (.*)\n', varTemp2, re.M|re.I)
            else:
                varTemp3 = re.search(r'inet6num:        (.*)\n', varTemp2, re.M | re.I)
            varTemp4 = re.search(r'netname:        (.*)\n', varTemp2, re.M|re.I)
            if varTemp3 and varTemp4:
                #print(varTemp3.group(1) + " " + varTemp4.group(1))
                varFileObjectCitrix.writelines(varTemp3.group(1).replace(' - ',',') + ',' + varTemp4.group(1) + '\n')
            else:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Convert: " + varTemp1[3] + " not found!")
                if varRetryList == "":
                    varRetryList = varTemp1[3]
                else:
                    varRetryList = varRetryList + "," + varTemp1[3]

        varFileObjectCitrix.close()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Citrix CN IPDB successfully generated")
        if varRetryList != "":
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Please try below address(s) using whois: " + varRetryList)
    except Exception as e:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Exception::message is: " + str(e.args))

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " All Done!")

if __name__ == '__main__':
    #print(sys.argv)
    #print(len(sys.argv))
    varArgv = ['ipv4','ipv6']
    if len(sys.argv) != 2:
        print("Usage: GenerateCitrixCNIPDB.py ipv4|ipv6")
        sys.exit()
    else:
        if sys.argv[1] not in varArgv:
            print("Usage: GenerateCitrixCNIPDB.py ipv4|ipv6")
            sys.exit()
        else:
            main()
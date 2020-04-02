import sys, urllib.request, os, subprocess, math, re, time, ipcalc

"""

Author: Robbie Shen
Date: 2020.04.02
Contact: yazhong.shen@citrix.com

Prerequisite:
Existing "whois" command on your client
Install ipcalc module from pip

TODO: 
GenerateCitrixIPDB.py ipv4|ipv6 CN|HK|TW 

Requirements: Python 3.7.6 or higher

"""

def main() :
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Begin to read IPDB from APNIC...")
    try:
        varApnicDB = urllib.request.urlopen("http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  + " IPDB from APNIC completed!")

        if os.path.exists("APNIC-IPDB-ALL.txt"):
            os.remove("APNIC-IPDB-ALL.txt")
        if os.path.exists("APNIC-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt"):
            os.remove("APNIC-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt")
        if os.path.exists("Citrix-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt"):
            os.remove("Citrix-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt")

        varFileObjectAll = open("APNIC-IPDB-ALL.txt","w")
        varFileObjectCNIP = open("APNIC-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt", "w")
        for varLine in varApnicDB:
            varFileObjectAll.writelines(varLine.decode('utf-8'))
            if varLine.decode('utf-8').find('apnic|' + sys.argv[2] + '|' + sys.argv[1]) > -1:
                varFileObjectCNIP.writelines(varLine.decode('utf-8'))
        varFileObjectCNIP.close()
        varFileObjectAll.close()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " DB files dumped")

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Begin to generate Citrix IPDB...")
        varFileObjectCitrix = open("Citrix-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt", "w")
        varFileObjectCitrix.write("NSGEO1.0\nContext=custom\nQualifier1=ispname\nStart\n")
        varRetryList = ""
        for varLine in open("APNIC-IPDB-" + sys.argv[2] + "-" + sys.argv[1] + ".txt"):
            varTemp1 = varLine.split('|')
            #print(varTemp1[3]+"/"+str(int(32-math.log(int(varTemp1[4]))/math.log(2))))
            try:
                if sys.argv[1] == "ipv4":
                    varTemp2 = subprocess.check_output(['whois -h whois.apnic.net ' + varTemp1[3] + ' | grep -E "inetnum:|netname:"'], shell=True, timeout=15).decode('utf-8')
                else:
                    varTemp2 = subprocess.check_output(['whois -h whois.apnic.net ' + varTemp1[3] + ' | grep -E "inet6num:|netname:"'], shell=True, timeout=15).decode('utf-8')
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Exception1: " + "whois -h whois.apnic.net " + varTemp1[3] + " failed! ")
                if varRetryList == "":
                    varRetryList = varTemp1[3]
                else:
                    varRetryList = varRetryList + "," + varTemp1[3]
                continue

            if sys.argv[1] == "ipv4":
                varTemp3 = re.search(r'inetnum:        (.*)\n', varTemp2, re.M|re.I)
            else:
                varTemp3 = re.search(r'inet6num:       (.*)\n', varTemp2, re.M | re.I)
            varTemp4 = re.search(r'netname:        (.*)\n', varTemp2, re.M|re.I)
            if varTemp3 and varTemp4:
                #print(varTemp3.group(1) + " " + varTemp4.group(1))
                if sys.argv[1] == "ipv4":
                    varFileObjectCitrix.writelines(varTemp3.group(1).replace(' - ',',') + ',' + varTemp4.group(1) + '\n')
                else:
                    varFileObjectCitrix.writelines(str(ipcalc.Network(varTemp3.group(1)).host_first()) + ',' + str(ipcalc.Network(varTemp3.group(1)).host_last()) + ',' + varTemp4.group(1) + '\n')
            else:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Convert: " + varTemp1[3] + " not found!")
                if varRetryList == "":
                    varRetryList = varTemp1[3]
                else:
                    varRetryList = varRetryList + "," + varTemp1[3]

        varFileObjectCitrix.close()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Citrix IPDB successfully generated")
        if varRetryList != "":
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Please try below address(s) using whois: " + varRetryList)
    except Exception as e:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " Exception2::message is: " + str(e.args))

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " All Done!")

if __name__ == '__main__':
    #print(sys.argv)
    #print(len(sys.argv))
    varArgv1 = ['ipv4','ipv6']
    varArgv2 = ['CN', 'HK', 'TW']
    if len(sys.argv) != 3:
        print("Usage: GenerateCitrixIPDB.py ipv4|ipv6 CN|HK|TW ")
        sys.exit()
    else:
        if (sys.argv[1] not in varArgv1) or (sys.argv[2] not in varArgv2):
            print("Usage: GenerateCitrixIPDB.py ipv4|ipv6 CN|HK|TW ")
            sys.exit()
        else:
            main()
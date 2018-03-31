from argparse import ArgumentParser
import prettytable as pt
import time

parser = ArgumentParser(description= "Auth log parser")
parser.add_argument("filename", help="Log file path")
parser.add_argument("-u", help="Summary failed login log and sort log by user .", action="store_true")
parser.add_argument("-after", help="Filter log after date. format YYYY-MM-DD-HH:MM:SS ", dest="AFTER", default= False)
parser.add_argument("-before", help="Filter log before date. format YYYY-MM-DD-HH:MM:SS ", dest="BEFORE", default= False)
parser.add_argument("-n", help="Show only the user of most N-th times ", dest="N", default= False)
parser.add_argument("-t", help="Show only the user of attacking equal or more than T times ", dest="T", default= False)
parser.add_argument("-r", help="Sort it reverse order ", action="store_true")
args = parser.parse_args()

name = {}
year = "2018"

def printTable(nameList):
    table = pt.PrettyTable()
    table.field_names = ["user", "count"]
    for data in nameList:
        table.add_row([data,name[data]])
    print(table)

def filterT(T, nameList):
    List = []
    if args.T != False:
        for data in nameList:
            if name[data] >= int(T):
                List.append(data)
    return List

def filterN(N, nameList):
    if args.N != False:
        del nameList[int(N):]
    return nameList

def filterSorted():
    if args.u:
        return sorted(name)
    elif args.r:
        return sorted(name, key=lambda x:name[x])
    else:
        return sorted(name, key=lambda x:name[x], reverse=True)

def filePreprocess():
    filename = args.filename
    fp = open(filename,'r')
    for line in fp:
        parts = line.split()
        datetime = year + "-" + parts[0] + "-" + parts[1] + "-" + parts[2]
        date = time.mktime(time.strptime(datetime, "%Y-%b-%d-%H:%M:%S"))

        if args.AFTER != False:
            after = (time.mktime(time.strptime(args.AFTER, "%Y-%m-%d-%H:%M:%S")))
            if date < after:
                continue           

        if args.BEFORE != False:
            before = (time.mktime(time.strptime(args.BEFORE, "%Y-%m-%d-%H:%M:%S")))
            if before < date:
                continue

        for i, string in enumerate(parts):
            if string == 'Invalid' and parts[i+1] == 'user':
                username = parts[i+2]
                if name.get(username) == None:
                    name[username] = 1
                else:
                    name[username]+= 1
    fp.close()

if __name__ == '__main__':
    filePreprocess()
    nameSorted = filterSorted()
    nameSorted = filterT(args.T, nameSorted)
    nameSorted = filterN(args.N, nameSorted)
    printTable(nameSorted)
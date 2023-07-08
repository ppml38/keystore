"""
Author: Prakash
Created Date: 24/10/2021
License: MIT

This is a commandline keystore manager.
You can use this for your daily secure password storage purposes.
In case you want to change encryption and decryption algorithms to your favourite one, head to encrypt() and decrypt() functions
"""
import getpass
import json
import os
import string
import random
import re

class table:
    def __init__(self,header):
        self.header = list(map(str,header))
        #self.lengths = list(map(len,header))
        self.max_length = 30
        self.lengths = []
        for h in header:
            self.lengths.append(min(self.max_length,len(h)))
        self.rows=[]
        self.title = None
    def add_row(self,row):
        row = list(map(str,row))
        self.rows.append(row)
        for i in range(len(row)):
            self.lengths[i] = min(self.max_length, max(self.lengths[i],len(row[i])))
    def add_title(self,title):
        self.title = title
    def print_header(self):
        string=''
        for i in range(len(self.header)):
            string+=f"|{bcolors.OKCYAN}{self.header[i]:^{self.lengths[i]}}{bcolors.ENDC}"
        print(string+"|")
    def get_chunks(self,x,max_length=None):
        max_length = max_length or self.max_length
        chunks, chunk_size = len(x), max_length
        return [ x[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    def print_row(self,row):
        #rows=[[] for i in range(len(row)]
        rows=[]
        max_height=0
        for field in row:
            rows.append(self.get_chunks(field))
            max_height=max(max_height,len(rows[-1]))
        for i in range(max_height):
            string=''
            for j in range(len(row)):
                text = rows[j][i] if i<len(rows[j]) else ""
                if i>0:
                    string+=f"|{text:<{self.lengths[j]}}"
                else:
                    string+=f"|{text:^{self.lengths[j]}}"
            print(string+"|")
    def print_line(self):
        line=''
        for i in range(len(self.header)):
            line+=f"+{'-'*self.lengths[i]}"
        print(line+"+")
    def print_title(self):
        if self.title==None:
            return
        total_length = sum(self.lengths)
        total_length+=(len(self.header)-1)
        self.print_line()
        chunks=self.get_chunks(self.title,total_length)
        for chunk in chunks:
            print(f"|{bcolors.OKGREEN}{chunk:^{total_length}}{bcolors.ENDC}|")
    def print(self):
        if len(self.rows)==0:
            return False
        self.print_title()
        self.print_line()
        self.print_header()
        self.print_line()
        for row in self.rows:
            self.print_row(row)
            self.print_line()
        return True
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

hdr="----------------\n"+bcolors.OKGREEN+"K E Y  S T O R E"+bcolors.ENDC+"\n----------------"
menu=["Store new site","Search","Delete a site","List all sites","Delete all sites","Edit a site","Reveal All sites","Save","SAVE and "+bcolors.FAIL+"EXIT"+bcolors.ENDC,"Dont save and EXIT","Export plain data","Change master password","Change welcome phrase\n\n"]
masterfilename="master.pwd"

os.system('cls')
masterpassword=getpass.getpass("Master Password : ")
welcomephrase=None
keystore={}

def generatepwd(length=32,caps=True,small=True,numbers=True,specials=True,request=False):
    if request:
        length=int(getdata(prompt="Password length :",regex="\d+\Z",default=32,message="Invalid length"))
        caps=confirm("Do you want to include capital letters(y/n) :")
        small=confirm("Do you want to include small letters(y/n) :")
        numbers=confirm("Do you want to include numbers(y/n) :")
        specials=confirm("Do you want to include punctuation characters(y/n) :")
    samplespace=''
    if caps:
        samplespace+=string.ascii_uppercase
    if small:
        samplespace+=string.ascii_lowercase
    if numbers:
        samplespace+=string.digits
    if specials:
        samplespace+=string.punctuation
    return random.sample(samplespace,length) if samplespace else ''
def success(msg):
    print(bcolors.OKGREEN+msg+bcolors.ENDC)
def error(msg):
    print(bcolors.FAIL+msg+bcolors.ENDC)
def warning(msg):
    print(bcolors.WARNING+msg+bcolors.ENDC)
def showmenu(options=[],header=None):
    if header:
        print(bcolors.HEADER+header+bcolors.ENDC)
    count=1
    for i in options:
        print(bcolors.OKBLUE+str(count)+"."+bcolors.ENDC+str(i))
        count+=1
    while True:
        ch=getdata(regex="\d+\Z")
        if int(ch)>=1 and int(ch)<=len(options):
            return ch
        error("Option not found")
def getdata(prompt=">>",regex=None,default=None,message="Invalid option"):
    #If there is a value in regex, by default it means, this funtion expects a valid value from user.
    #Hence it will infinitely ask user to enter valid data. user cannot escape just by pressing enter.
    #If there is no regex given, All kind of input is acceptable including blank. hence user can just "press any key to continue" using this
    #if user should be allowed to enter valid value and also escape by pressing empty enter. Adjust regex accordingly.
    errcount=0
    while(True):
        data=None
        data=input(bcolors.OKBLUE+prompt+bcolors.ENDC)
        if not data:
            if default:
                return default
        if regex:
            if re.match(regex,data):
                return data
            else:
                if default and errcount==2:
                    error("Invalid again. Default "+str(default)+" assumed")
                    return default
                error(message)
                errcount+=1
                continue
        return data
def confirm(prompt="(y/n):"):
    while True:
        choice=input(bcolors.OKCYAN+prompt+bcolors.ENDC)
        if choice.lower() in ['y','yes','yeah','ya','yep']: #['y','Y','Yes','YES','yes','yeah','Yeah','YEAH','ya','Ya','YA','yep','Yep','YEP']:
            return True
        elif choice.lower() in ['n','no','nope']: #['n','N','no','No','NO','Nope','nope','NOPE']:
            return False
        else:
            error("Invalid option")


def decrypt(cipher,pwd=None):
    if pwd==None:
        pwd=masterpassword
    if pwd=='': #If password is empty data handled in plain. no encryption or decryption
        return cipher
    plain=[]
    for i in range(len(cipher)):
        plain.append(int.from_bytes(cipher[i].encode('utf-8'),byteorder='big')^int.from_bytes(pwd[i%len(pwd)].encode('utf-8'),byteorder='big'))
    return bytes(plain).decode('utf-8')

def encrypt(plain,pwd=None):
    if pwd==None:
        pwd=masterpassword
    if pwd=='': #If password is empty data handled in plain. no encryption or decryption
        return plain
    cipher=[]
    for i in range(len(plain)):
        cipher.append(int.from_bytes(plain[i].encode('utf-8'),byteorder='big')^int.from_bytes(pwd[i%len(pwd)].encode('utf-8'),byteorder='big'))
    return bytes(cipher).decode('utf-8')

def save():
    with open(masterfilename,'w') as f:
        master={"wp":welcomephrase,"ks":keystore}
        f.write(json.dumps(master))

def choose_a_site():
    if keystore:
        count=1
        for s in keystore:
            print(str(count)+'.'+decrypt(s))
            count+=1
        try:
            choice=int(getdata(prompt="Choose a site(1-"+str(len(keystore))+") to view OR Press 'Enter/Return' to continue :"))
            c=1
            for sitename in keystore:
                if c==choice:
                    return {'sitename':sitename,'option':choice}
                else:
                    c+=1
            return {'sitename':None,'option':None}
        except ValueError as e:
            return {'sitename':None,'option':None}
        except Exception as e:
            raise e
    else:
        error("Keystore is empty")
        return {'sitename':None,'option':None}
def show_a_site(option_number):
    if option_number==None:
        return
    c=1
    for i in keystore:
        if c==option_number:
            t=table(["S.No","Field","Value"])
            t.add_title(decrypt(i))
            all_records=keystore[i] #a site can have multiple records, ex. having multiple twitter accounts
            for index in range(len(all_records)):
                record = all_records[index]
                first_field = True
                for field in record:
                    if first_field:
                        t.add_row([index+1,decrypt(field),decrypt(record[field])])
                        first_field=False
                    else:
                        t.add_row(["",decrypt(field),decrypt(record[field])])
            t.print()
            break
        else:
            c+=1
    else:
        error("Invalid option number")

lines=''
try:
    if os.path.isfile(masterfilename):
        with open(masterfilename,'r') as f:
            for line in f:
                lines+=line
        if lines:
            master=json.loads(lines)
            welcomephrase=master['wp']
            keystore=master['ks']
            for c in decrypt(welcomephrase):
                if c not in string.printable[:-5]:
                    error("Probably incorrect master password")
                    quit()
            print("\n"+decrypt(welcomephrase))
            if not confirm("\nIs the welcome phrase recognizable? (y/n) :"):
                print("Please login again")
                quit()
        else:
            print("Looks like the master file is empty/corrupted. Anyway let's start fresh.")
            welcomephrase=encrypt(getdata("\nNew welcome phrase :"))
            keystore={}
            save()
    else:
        print("Welcome to keystore.\nPlease set a welcome phrase below. this will help you to validate master password.")
        welcomephrase=encrypt(getdata("\nWelcome phrase :"))
        save()
except Exception:
    raise
    error("Error reading master file")
    quit()

while(True):
    choice=None
    os.system('cls')
    #choice=input(menu)
    print(hdr)
    choice=showmenu(menu)
    if choice=='1':
        selection=showmenu(options=["Create new site","Add new account to existing site"],header="What you want to do?")
        if selection=='1':
            s=encrypt(getdata("Site : "))
            u=encrypt(getdata("Username/email : "))
            if confirm("Do you want keystore to generate a secure password for you? (y/n):"):
                p=encrypt(generatepwd(request=True))
                print("Password generated and stored.")
            else:
                p=encrypt(getdata("Password : "))
            if s in keystore:
                keystore[s].append({encrypt("Username/Email"):u,encrypt("Password"):p})
                error("Site name already exists.")
                success("Above username and password are appended to it.")
            else:
                keystore[s]=[{encrypt("Username/Email"):u,encrypt("Password"):p}]
            while True:
                if not confirm("Do you want to store any more data with this site (y/n) ?"):
                    break
                f=encrypt(getdata("Field : "))
                if f in keystore[s][-1]:
                    error("This field already exists!")
                    continue
                v=encrypt(getdata("Value: "))
                keystore[s][-1][f]=v
            success("Done")
        elif selection=='2':
            s = choose_a_site()['sitename']
            print("Please provide details of new account/record, to store.")
            u=encrypt(getdata("Username/email : "))
            if confirm("Do you want keystore to generate a secure password for you? (y/n):"):
                p=encrypt(generatepwd(request=True))
                print("Password generated and stored.")
            else:
                p=encrypt(getdata("Password : "))
            if s in keystore:
                keystore[s].append({encrypt("Username/Email"):u,encrypt("Password"):p})
            else:
                success("No existing site found. Added as a new site instead.")
                keystore[s]=[{encrypt("Username/Email"):u,encrypt("Password"):p}]
            while True:
                if not confirm("Do you want to store any more data with this site (y/n) ?"):
                    break
                f=encrypt(getdata("Field : "))
                if f in keystore[s][-1]:
                    error("This field already exists!")
                    continue
                v=encrypt(getdata("Value: "))
                keystore[s][-1][f]=v
            success("Done")
        else:
            error("Invalid option")
    elif choice=='2':
        search_term = getdata("Search Term :")
        if keystore:
            t=table(["Site Name","Field","Value"])
            for site in keystore:
                siteName = decrypt(site)
                for i in keystore[site]:
                    for j in i:
                        var = decrypt(j)
                        val = decrypt(i[j])
                        if var.lower().find(search_term)!=-1 or val.lower().find(search_term)!=-1 or siteName.lower().find(search_term)!=-1:
                            #print(siteName+">>\t"+var+":\t"+val)
                            t.add_row([siteName,var,val])
            if not t.print():
                error("Search result empty")
        else:
            error("Keystore is empty")
    elif choice=='3':
        site_input = choose_a_site()
        show_a_site(site_input['option'])
        if site_input['sitename']==None:
            error("No site deleted")
        elif confirm("Is this the site you want to delete ? (y/n):") and confirm("Are you sure to delete '%s' ? (y/n):"%decrypt(site_input['sitename'])):
            s=site_input['sitename']
            if s in keystore:
                if len(keystore[s])>1:
                    c=1
                    for i in keystore[s]:
                        print("("+str(c)+")")
                        for j in i:
                            print(decrypt(j)+"\t"+decrypt(i[j]))
                        c+=1
                    n=getdata(prompt="Please select the record to delete (1-"+str(len(keystore[s]))+") or enter 'A' to delete all records: ",regex="a|A|\d+\Z",message="Invalid option")
                    if n in ['a','A']:
                        del keystore[s]
                    else:
                        try:
                            n=int(n)
                            if n>0 and n<=len(keystore[s]):
                                del keystore[s][n-1]
                                print("Record no."+str(n)+" Deleted")
                        except ValueError:
                            error("Please enter valid option")
                else:
                    del keystore[s]
                    success("Deleted")
            else:
                error(decrypt(s)+" not found")
        else:
            error("No site deleted.")
    elif choice=='4':
        if keystore:
            choice = choose_a_site()['option']
            if choice!=None:
                show_a_site(choice)
        else:
            error("Keystore is empty")
    elif choice=='5':
        #keystore={}
        error("This option is deprecated.")
    elif choice=='6':
        site_input = choose_a_site()
        show_a_site(site_input['option'])
        if site_input['sitename']==None:
            error("No site edited")
        elif confirm("Is this the site you want to edit ? (y/n):"):
            s=site_input['sitename']
            if s in keystore:
                if len(keystore[s])>1:
                    c=1
                    for i in keystore[s]:
                        print("("+str(c)+")")
                        for j in i:
                            print(decrypt(j)+"\t"+decrypt(i[j]))
                        c+=1
                    n=getdata(prompt="Please select the record to Edit (1-"+str(len(keystore[s]))+"): ",regex="\d+\Z")
                else:
                    n=1        
                try:
                    n=int(n)
                    if n>0 and n<=len(keystore[s]):
                        option=showmenu(options=["Add a field","Edit existing field","Delete a field"],header="What you want to do?")
                        if option=='1':
                            f=encrypt(getdata("Field : "))
                            if f in keystore[s][n-1]:
                                error("This field already exists!")
                            else:
                                v=encrypt(getdata("Value: "))
                                keystore[s][n-1][f]=v
                                success("New field added")
                        elif option=='2':
                            #print("\n")
                            #opts=[]
                            #for i in keystore[s][n-1]:
                                #print(str(cu)+"."+decrypt(i))
                                #opts.append(decrypt(i))
                                #cu+=1
                            f=showmenu(options=list(map(decrypt,keystore[s][n-1])),header="Please select the field to Edit (1-"+str(len(keystore[s][n-1]))+")?")
                            try:
                                f=int(f)
                                if f>0 and f<=len(keystore[s][n-1]):
                                    print("Old value for %s:%s"%(decrypt(list(keystore[s][n-1])[f-1]), decrypt(keystore[s][n-1][list(keystore[s][n-1])[f-1]])))
                                    if confirm("Are you sure to edit ? (y/n):"):
                                        keystore[s][n-1][list(keystore[s][n-1])[f-1]]=encrypt(getdata("New Value for "+decrypt(list(keystore[s][n-1])[f-1])+": "))
                                        success("Updated")
                                    else:
                                        error("Not edited")
                                else:
                                    error("Invalid option")
                            except ValueError:
                                error("Invalid option")

                        elif option=='3':
                            #opts=[]
                            #for i in keystore[s][n-1]:
                                #print(str(cu)+"."+decrypt(i))
                                #opts.append(decrypt(i))
                            f=showmenu(options=list(map(decrypt,keystore[s][n-1])),header="Which field you want to Delete (1-"+str(len(keystore[s][n-1]))+")?")
                            try:
                                f=int(f)
                                if f>0 and f<=len(keystore[s][n-1]):
                                    if confirm("Are you sure to delete? (y/n):"):
                                        del keystore[s][n-1][list(keystore[s][n-1])[f-1]]
                                        success("Deleted")
                                    else:
                                        error("Nothing deleted")
                                else:
                                    error("Invalid option")
                            except ValueError:
                                error("Invalid option")
                        else:
                            error("Invalid option")
                        
                except ValueError:
                    error("Please enter valid option")
            else:
                error(decrypt(s)+" not found")
        else:
            error("No site edited")
    elif choice=='7':
        if keystore:
            for i in range(len(keystore)):
                print("(%s)"%(i+1))
                show_a_site(i+1)
        else:
            error("Keystore is empty")
    elif choice=='8':
        save()
        success("Saved")
    elif choice=='9':
        save()
        success("Changes saved")
        break;
    elif choice=='10':
        success("changes NOT Saved")
        break
    elif choice=='11':
        if keystore:
            with open(getdata("File name:"),"w") as f:
                for s in keystore:
                    f.write(decrypt(s))
                    for i in keystore[s]:
                        for j in i:
                            f.write("\n\t"+decrypt(j)+"\t"+decrypt(i[j]))
                        f.write("\n")
                    f.write("\n")
            success("Data exported")
        else:
            error("Keystore is empty")
    elif choice=='12':
        print(bcolors.FAIL+"WARNING:"+bcolors.ENDC+bcolors.WARNING+"\nThis action will try to decrypt all data, with the master password which you keyed in as you logged in, and encrypt it with new master password"+bcolors.ENDC)
        print(bcolors.WARNING+"Hence if you had provided an incorrect master password, your entire data will be irrecoverably corrupted. So please double check if you have logged in with correct master password. you can do this by checking if you can see and recognize data of any site."+bcolors.ENDC)
        print(bcolors.WARNING+"This will also save all the changes made so far before changing the password, hence invalidating 'Dont save and exit' option."+bcolors.ENDC)
        if confirm("Continue?(y/n):"):
            np=getpass.getpass("\nEnter new password :")
            np1=getdata("Enter new password again :")
            if np==np1:
                nks={}
                for s in keystore:
                    nfs=[]
                    for r in keystore[s]:
                        nr={}
                        for f in r:
                            nr[encrypt(decrypt(f),np)]=encrypt(decrypt(r[f]),np)
                        nfs.append(nr)
                    nks[encrypt(decrypt(s),np)]=nfs
                keystore=nks
                welcomephrase=encrypt(decrypt(welcomephrase),np)
                masterpassword=np
                save()
                success("Master password changed.")
            else:
                error("Password mismatch")
        else:
            success("No changes made")
    elif choice=='13':
        nwp=encrypt(getdata("New welcome phrase :"))
        welcomephrase=nwp
        save()
        success("New welcome phrase saved")
    else:
        error("There is no such option")
    input("\n\nPress any key to continue...")
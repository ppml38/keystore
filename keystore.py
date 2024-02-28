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
import aes
import base64
import hashlib
import shutil
import time
import subprocess
import sys


def copy_to_clipboard(data):
    command = "clip" # windows
    if sys.platform.startswith("darwin"): #macos
        command = "pbcopy" 
    #linux not supported as there is no builtin module for copy afaik, it requires xclip to be installed

    subprocess.run(command, text=True, input=data)
    
class table:
    def __init__(self,header,fields_to_hide=[]):
        self.header = list(map(str,header))
        self.fields_to_hide = fields_to_hide
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
        result=[]
        for line in x.split("\n"):
            if len(line)==0: #empty line in between lines
                result+=[line]
            else:
                chunks, chunk_size = len(line), max_length
                result+=[ line[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
        return result
    def print_row(self,row,row_number):
        #rows=[[] for i in range(len(row)]
        rows=[]
        max_height=0
        for i,field in enumerate(row):
            if i in self.fields_to_hide:
                rows.append(["**** (%s.%s)"%(row_number,i)])
            else:
                rows.append(self.get_chunks(field))
            max_height=max(max_height,len(rows[-1]))
        for i in range(max_height):
            string=''
            for j in range(len(row)):
                text = rows[j][i] if i<len(rows[j]) else ""
                string+=f"|{text:<{self.lengths[j]}}" #replace < with ^ for center align
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
    def show_reveal(self):
        cell = getdata(prompt="Enter cell number to reveal/copy (empty to cancel) :",regex="(\d+\.\d+)?\Z",message="Invalid cell number")
        if len(cell)==0:
            return False
        row,col=cell.split(".")
        row,col=int(row),int(col)
        if row<0 or row>=len(self.rows) or col<0 or col>=len(self.rows[0]):
            error("Cell number not found")
            return True
        copy_or_reveal = getdata(prompt="Copy(c) or Reveal(r) :", regex="c|r\Z")
        val = self.rows[row][col]
        if copy_or_reveal=="r":
            print(val)
        elif copy_or_reveal=="c":
            copy_to_clipboard(val)
            success("Copied to clipboard")
        else:
            error("Invalid option")
        return True
            
    def print(self):
        if len(self.rows)==0:
            return False
        self.print_title()
        self.print_line()
        self.print_header()
        self.print_line()
        for i,row in enumerate(self.rows):
            self.print_row(row,i)
            self.print_line()
        if len(self.fields_to_hide)!=0:
            while self.show_reveal(): # continue as long as user not enter empty string
                pass
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
menu=[
    "Store new site/account",
    "Search",
    "Delete a site",
    "List all sites",
    "Delete all sites",
    "Edit an account",
    "Reveal All sites",
    "Save",
    bcolors.FAIL+"EXIT"+bcolors.ENDC,
    "Export plain data",
    "Change master password",
    "Change welcome phrase\n\n"
    ]
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
def showmenu(options=[],header=None,showCancel=False):
    if header:
        print(bcolors.HEADER+header+bcolors.ENDC)
    count=1
    for i in options:
        print(bcolors.OKBLUE+str(count)+"."+bcolors.ENDC+str(i))
        count+=1
    if showCancel==True:
        print(bcolors.OKBLUE+str(count)+"."+bcolors.ENDC+bcolors.FAIL+"Cancel"+bcolors.ENDC)
    while True:
        ch=getdata(regex="\d+\Z")
        if int(ch)>=1 and int(ch)<=len(options):
            return ch
        if showCancel==True and int(ch)==len(options)+1:
            return None # user chose cancel
        error("Option not found")
def get_multiline_data(prompt):
    print(bcolors.OKBLUE+prompt+bcolors.ENDC)
    print("Enter just Ctrl-D(mac) or Ctrl-Z(windows) IN A NEW SEPERATE LINE to enter and close it.")
    contents = []
    while True:
        try:
            line = input("line/ctrl+z >")
        except EOFError:
            break
        contents.append(line)
    return "\n".join(contents)
def getdata(prompt=">>",regex=None,default=None,message="Invalid option",multiline=False):
    #If there is a value in regex, by default it means, this funtion expects a valid value from user.
    #Hence it will infinitely ask user to enter valid data. user cannot escape just by pressing enter.
    #If there is no regex given, All kind of input is acceptable including blank. hence user can just "press any key to continue" using this
    #if user should be allowed to enter valid value and also escape by pressing empty enter. Adjust regex accordingly.
    errcount=0
    while(True):
        data=None
        if multiline==True:
            data=get_multiline_data(prompt)
        else:
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
    cipher = base64.b64decode(cipher,b"-_")
    plain=[]
    for i in range(len(cipher)): #looping through bytes already fetches int
        plain.append(cipher[i]^int.from_bytes(pwd[i%len(pwd)].encode('utf-8'),byteorder='big'))
    return bytes(plain).decode('utf-8')

def encrypt(plain,pwd=None):
    if pwd==None:
        pwd=masterpassword
    if pwd=='': #If password is empty data handled in plain. no encryption or decryption
        return plain
    cipher=[]
    for i in range(len(plain)):
        cipher.append(int.from_bytes(plain[i].encode('utf-8'),byteorder='big')^int.from_bytes(pwd[i%len(pwd)].encode('utf-8'),byteorder='big'))
    return base64.b64encode(bytes(cipher),b"-_").decode('utf-8')

def digest(string):
    return hashlib.sha256(("%s%s"%(string,masterpassword)).encode()).hexdigest()

def hashit(string):
    return "%s.%s"%(string,digest(string))

def unhashit(hashed_string):
    try:
        string,hash = hashed_string.split(".")
        if hashlib.sha256(("%s%s"%(string,masterpassword)).encode()).hexdigest() == hash:
            return string
        else:
            print("Either your password is wrong or the file is tampered")
            quit()
    except Exception:
        print("Master file is tampered")
        quit()

def secure_read_master_file(masterfilename):
    with open(masterfilename,"r") as masterfile:
        # read base64 encoded cipher from file
        encoded_cipher_string = unhashit(masterfile.read()) #unhash before decrypt
        # convert base64 to bytes - cipher_binary
        cipher_binary = base64.b64decode(encoded_cipher_string)
        # decrypt using master password
        return aes.decrypt(masterpassword,cipher_binary).decode() # decrypt returns bytes, so we convert to text

def secure_write_master_file(content,masterfilename,conf=False):
    # expecting text content as input

    # checking hash of previous file and current json dump to check if the changes made is not working
    # because every time the json dump creates a new hash no matter if edited or not
    # possibly because, AES algorithm padding data with different random bytes every time
    # so we currently dont do that here

    if conf and not confirm("Do you want save the changes? (y/n) :"):
        success("Changes NOT saved")
        return False

    # encrypt content using masterpassword
    cipher_binary=aes.encrypt(masterpassword,content) #encrypt internally converts string to binary
    # convert resultant binary to base64
    encoded_cipher_string = base64.b64encode(cipher_binary).decode()
    # write base64 to file
    data_to_write=hashit(encoded_cipher_string)
    
    with open(masterfilename,"w") as masterfile:
        masterfile.write(data_to_write) # add hash
    success("Saved")
    return True

def take_backup():
    if not os.path.exists("backup"):
        os.makedirs("backup")
    
    change_description_oneliner = getdata(prompt="Change description one-liner for backup :",regex="[a-zA-Z0-9_\- ]*\Z",default="NoDescription",message="Invalid description. only alphabets, numbers, underscore and hyphen are allowed")
    shutil.copyfile(masterfilename,"backup/%s.%s.%s.backup"%(masterfilename,int(time.time()),change_description_oneliner))
    success("Data file backed up")

def save(confirm=False):
    master={"wp":welcomephrase,"ks":keystore}
    if secure_write_master_file(json.dumps(master),masterfilename,confirm)==True:
        # take backup only if actual disk write happens
        take_backup()

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
def show_a_site(option_number,hide_values=False):
    if option_number==None:
        return
    c=1
    for i in keystore:
        if c==option_number:
            t=table(["S.No","Field","Value"],fields_to_hide=[2] if hide_values else [])
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
        lines=secure_read_master_file(masterfilename)
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
        selection=showmenu(options=["Create new site","Add new account to existing site"],header="What you want to do?",showCancel=True)
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
                v=encrypt(getdata("Value: ",multiline=True))
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
                v=encrypt(getdata("Value: ",multiline=True))
                keystore[s][-1][f]=v
            success("Done")
        elif selection==None: #user chose cancel
            success("No changes made.")
        else: # empty input also comes here
            error("Invalid option")
    elif choice=='2':
        search_term = getdata("Search Term :")
        if keystore:
            t=table(["S.no","Site Name","Field","Value"],fields_to_hide=[3])
            sno=0
            for site in keystore:
                sno+=1
                siteName = decrypt(site)
                for i in keystore[site]:
                    for j in i:
                        var = decrypt(j)
                        val = decrypt(i[j])
                        if var.lower().find(search_term)!=-1 or val.lower().find(search_term)!=-1 or siteName.lower().find(search_term)!=-1:
                            #print(siteName+">>\t"+var+":\t"+val)
                            t.add_row([sno,siteName,var,val])
            if not t.print():
                error("Search result empty")
        else:
            error("Keystore is empty")
    elif choice=='3':
        site_input = choose_a_site()
        show_a_site(site_input['option'],hide_values=True)
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
                show_a_site(choice,hide_values=True)
        else:
            error("Keystore is empty")
    elif choice=='5':
        #keystore={}
        error("This option is deprecated.")
    elif choice=='6':
        site_input = choose_a_site()
        show_a_site(site_input['option'],hide_values=True)
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
                        option=showmenu(options=["Add a field","Edit existing field","Delete a field"],header="What you want to do?",showCancel=True)
                        if option=='1':
                            f=encrypt(getdata("Field : "))
                            if f in keystore[s][n-1]:
                                error("This field already exists!")
                            else:
                                v=encrypt(getdata("Value: ", multiline=True))
                                keystore[s][n-1][f]=v
                                success("New field added")
                        elif option=='2':
                            #print("\n")
                            #opts=[]
                            #for i in keystore[s][n-1]:
                                #print(str(cu)+"."+decrypt(i))
                                #opts.append(decrypt(i))
                                #cu+=1
                            f=showmenu(options=list(map(decrypt,keystore[s][n-1])),header="Please select the field to Edit (1-"+str(len(keystore[s][n-1]))+")?",showCancel=True)
                            if f!=None:
                                try:
                                    f=int(f)
                                    if f>0 and f<=len(keystore[s][n-1]):
                                        print("Old value for %s:%s"%(decrypt(list(keystore[s][n-1])[f-1]), decrypt(keystore[s][n-1][list(keystore[s][n-1])[f-1]])))
                                        if confirm("Are you sure to edit ? (y/n):"):
                                            keystore[s][n-1][list(keystore[s][n-1])[f-1]]=encrypt(getdata("New Value for "+decrypt(list(keystore[s][n-1])[f-1])+": ",multiline=True))
                                            success("Updated")
                                        else:
                                            error("Not edited")
                                    else:
                                        error("Invalid option")
                                except ValueError:
                                    error("Invalid option")
                            else:
                                success("No changes made")

                        elif option=='3':
                            #opts=[]
                            #for i in keystore[s][n-1]:
                                #print(str(cu)+"."+decrypt(i))
                                #opts.append(decrypt(i))
                            f=showmenu(options=list(map(decrypt,keystore[s][n-1])),header="Which field you want to Delete (1-"+str(len(keystore[s][n-1]))+")?",showCancel=True)
                            if f!=None:
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
                                success("No changes made")
                        elif option==None: #user chose cancel
                            success("No changes made")
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
    elif choice=='9':
        save(confirm=True)
        break
    elif choice=='10':
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
    elif choice=='11':
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
    elif choice=='12':
        nwp=encrypt(getdata("New welcome phrase :"))
        welcomephrase=nwp
        save()
        success("New welcome phrase saved")
    else:
        error("There is no such option")
    input("\n\nPress any key to continue...")
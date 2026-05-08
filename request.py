import os,subprocess,pip

path = subprocess.Popen(["pwd"],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
        ).communicate()

path = path[0].rstrip()

print("chicking subjects floder .... ")
if os.path.exists(path+"/subjects"):
    print("already exits!!!!!")
else:
    print(f"con,t find any 'subjects' floder on {path}\ncreating floder!!!!")
    os.mkdir(path+"/subjects")
    print("done!!!!")

print("checking kivy module .....")
try:
    import kivy
    print("already installed!!!!")
except:
    print("installing kivy .........")
    if os.system("pip install kivy") == 0:
        print("installation completed with pip !!!! (kivy)")
    elif os.system("pip3 install kivy") == 0:
        print("installation completed with pip3 !!!! (kivy)")
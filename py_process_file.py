import glob
import sys
import string
import os
import re
import shutil
from subprocess import call

def writeListToFile(infoList, outFile):
  for item in infoList:
    outFile.write(item + " ")
  outFile.write("\n")
  
def spark_parser(tmp1,tmp0):
  inFile = open(tmp1,'r')
  outFile = open(tmp0,'w')
  infoList = []
  infoList2 = []
  infoList0 = []
  infoList4 = []
  infoList_previous = []
  infoList_tmp = []

  vUp = ""
  v = ""
  V = ""
  vDown = ""
  vUp_previous = ""
  vDown_previous = ""

  # Get first line informations
  line = inFile.readline()
  infoList = line.split('\n') # In order to remove the '\n' at the end of the line we've just read
  infoList = infoList[0].split('\t')
  # Store first line informations
  vUp = infoList[3]
  vDown = infoList[4]
  # Write first line to output file
  infoList.append("begin") # Add "begin" flag since this is the beginning of the first block
  writeListToFile(infoList, outFile)

  for line in inFile:
    # Store previous line informations in 'previous' variables
    infoList_previous = infoList[:] # Warning: you must clone using 'infoList[:]', else the list is copied as the same object but with two names!
    vUp_previous = vUp
    vDown_previous = vDown
    # Get current line informations
    infoList = line.split('\n')
    infoList = infoList[0].split('\t')
    # Store current line informations
    vUp = infoList[3]
    vDown = infoList[4]
    # If voltage changes, save last line of previous voltage block, and the new line which is the start of a new block
    if vUp_previous != vUp or vDown_previous != vDown:
      infoList_previous.append("end") # Add "end" flag since this is the end of a block
      writeListToFile(infoList_previous, outFile)
      infoList_tmp = infoList[:]
      infoList_tmp.append("begin") # Add "begin" flag since this is the beginning of a new block
      writeListToFile(infoList_tmp, outFile)

    if infoList[7] != '0':
      infoList_tmp = infoList[:]
      infoList_tmp.append("chien") # Add "chien" flag since this is not the beginning neither the end of a block
      writeListToFile(infoList_tmp, outFile)

  infoList.append("end") # Add "end" flag since this is the end of a block
  writeListToFile(infoList, outFile)
    
  inFile.close()
  outFile.close()

  os.system("awk \'!/0$/\' tmp1 > tmp2")
  os.system("sort -k4,5 -u tmp1 > tmp3")  
  os.system("sort -k4,5 -u tmp2 > tmp1")
  os.system("cut -f 4,5 tmp3 > tmp4")
  os.system("cut -f 4,5 tmp1 > tmp2")
  os.system("mkdir tmpdir1")
    
  tmp2=open('tmp2','r')
  tmp4=open('tmp4','r')
  tmp0=open('tmp0','r')
  SpT0=open('SpT0','w')
  found="false"
  
  for line2 in tmp2:
    infoList2 = line2.split('\n')
    infoList2 = infoList2[0].split('\t')
    V=infoList2[0] + infoList2[1]
    tmpV = open('tmpdir1/tmpV' + V,'w')
    tmp0.seek(0)
    for line0 in tmp0:
      infoList0 = line0.split('\n')
      infoList0 = infoList0[0].split(' ')
      v=infoList0[3] + infoList0[4]
      if V == v:
        writeListToFile(infoList0,tmpV)
          
  tmp2.seek(0)
  for line4 in tmp4:
    found='false'
    infoList4 = line4.split('\n')
    infoList4 = infoList4[0].split('\t')
    V=infoList4[0] + " " + infoList4[1]
    tmp2.seek(0)
    for line2 in tmp2:
      infoList2 = line2.split('\n')
      infoList2 = infoList2[0].split('\t')
      v=infoList2[0] + " " + infoList2[1]
      if V == v:
        found='true'
    if found=='false':
      V=V + "\n"
      SpT0.write(V)
        
  tmp0.close()
  tmp2.close()
  tmp4.close()
  SpT0.close()
 
if __name__ == '__main__':

  if os.name == "nt":
    print "ERROR: Please install Linux"
    sys.exit(1)

  if len(sys.argv) != 3: # 1 is addValueInRegion.py + 3 arguments
    print "ERROR: Need 2 arguments: the file to process and the number of LEMs in it."
    sys.exit(1) 
    
  script_name = sys.argv[0]
  input_file = sys.argv[1]
  LEM_number = int(sys.argv[2])
  
  if os.path.isdir(input_file):
    print "ERROR: " + input_file + " is a directory."
    sys.exit(1)
    
  if not os.path.isfile(input_file):
    print "ERROR: Can't find file " + input_file
    sys.exit(1)
    
  if LEM_number !=1 and LEM_number !=2 and LEM_number !=3 and LEM_number !=4:
    print "ERROR: Unexpected number of LEM"
    sys.exit(1)  
    
  Path = os.path.split(os.path.abspath(script_name))
  Dir = os.path.dirname(input_file)
  DIR = Path[0]
  File = os.path.basename(input_file)
    
  for LEM in range(0,LEM_number):
    lemdir = str(DIR) + "/" + str(Dir) + "/LEM" + str(LEM)
    if not os.path.isdir(lemdir):
      os.makedirs(lemdir)
    
  shortVdet = lemdir + "/shortVdet"
  
  if os.path.isfile(shortVdet):
    answer = raw_input("WARNING: shortVdet(s) already exist(s) for LEM " + str(LEM) + ", do you want to recreate it(them)? (yes/no) \n")
    while answer != "no" and answer != "yes":
      answer = raw_input("Please answer by yes or no. \n")
        
    if answer == "no":
      numlines = 0
      with open(input_file, "r") as inFile:
        l = inFile.readlines()
        numlines = len(l)
      inFile.close()
      for i in range(0,LEM_number):
        shortVdet = str(DIR) + "/" + str(Dir) + "/LEM" + str(i) + "/shortVdet"
        with open(shortVdet, "r") as inFile:
          l = inFile.readlines()
          numlinesvdet = len(l)
        os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM" + str(i) + "/\",\"" + str(i) + "\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
    
      sys.exit(0)
    
    for folder in glob.glob(str(DIR) + "/" + str(Dir) + "/LEM*"): #if answer = yes
      os.system("rm " + str(folder) + "/*")
    
  print ("Please indicate, for each LEM, the channels corresponding to the low and high voltages. If one is at ground, write 'ground' \n")
  
  dict_LEM_channel = {}
  already_chosen = []
  for i in range(0,LEM_number):
    dict_LEM_channel["LEM" + str(i)] = [0,0]
    for j in range (0,2):
      if j == 0:
        volt = "low"
      if j == 1:
        volt = "high"
      channel = raw_input("LEM " + str(i) + ", " + volt + " voltage: \n")
      while channel != "0" and channel != "1" and channel != "2" and channel != "3" and channel != "ground" or channel in already_chosen:
        if channel in already_chosen:
          channel = raw_input("Channel already set as another voltage or for another LEM. Try again! \n")
        else:
          channel = raw_input("Channel is not an integer between 0 and 3 or 'ground'. Try again! \n")        
      if channel != "ground":
        already_chosen.append(channel)
      dict_LEM_channel["LEM" + str(i)][j] = channel
    
   
  print "Opening file " + input_file + " containing " + str(LEM_number) + " LEMs..."
  
  os.system("sed -i \'s/[[:blank:]]/ /g\' " + input_file)
  os.system("sed -i \'s/Ch /Ch/g\' " + input_file)
  os.system("sed -i \'s/,/./g\' " + input_file)
  os.system("sed -i \'s/\\//_/g\' " + input_file)  
  
  with open(input_file, "r") as inFile:
    l = inFile.readlines()
    numlines = len(l)
    Chnumber = l[0].count("Ch")
    Chnumber2 = l[1].count("Ch")
    colnumber = len(l[0].split(" "))
    colnumber2 = len(l[1].split(" "))
    if colnumber != colnumber2:
      print "ERROR: Not same number of columns in header and rest of file"
      sys.exit(1)
    if Chnumber != Chnumber2:
      print "ERROR: Not same number of channels in header and rest of file"
      sys.exit(1)
    if l[0].count("Heure") == 0:
      print "ERROR: Should have a column 'Heure'"
      sys.exit(1)
    for i in range(len(l)):
      if len(l[i].split(" ")) != colnumber:
        print "ERROR: line " + str(i) + " is corrupted"
        sys.exit(1)
  print "Analysing file " + input_file + " with " + str(numlines) + " lines, " + str(colnumber) + " columns and " + str(Chnumber) + " channels"
    
  
  os.chdir(str(DIR) + "/" + str(Dir))
  adress = "./"
  j = 0
  with open(File, "r") as inFile:
    l = inFile.readline()
    for i in range(colnumber):
      k=i+1
      variable = l.split(" ")[i]
      if "Ch" in variable:
        Chdir = str(DIR) + "/" + str(Dir) + "/" + str(File) + "_" + variable
        if not os.path.isdir(Chdir):
          os.makedirs(Chdir)
        adress = Chdir
        j += 1
      else:
        if k == colnumber:
          variable = variable[:-1]
        os.system("cut -d \' \' -f " + str(k) + " " + str(DIR) + "/" + str(Dir) + "/" + str(File) + " > " + adress + "/" + variable)
  
  if os.path.isfile("tmp0"):
      os.remove("tmp0")
  if os.path.isfile("tmp1"):
      os.remove("tmp1")
  if os.path.isfile("tmp2"):
      os.remove("tmp2")
  if os.path.isfile("tmp3"):
      os.remove("tmp3")
  if os.path.isfile("tmp4"):
      os.remove("tmp4")      
  if os.path.isdir("tmpdir1"):
      shutil.rmtree("tmpdir1")

      
  os.system("cut -d \'_\' -f 1 Date > day")
  os.system("cut -d \'_\' -f 2 Date > month")
  os.system("cut -d \'_\' -f 3 Date > year")
  os.remove("Date")
  os.system("paste -d \'_\' year month > tmp0")
  os.system("paste -d \'_\' tmp0 day > Date")
  os.remove("day")
  os.remove("month")
  os.remove("year")
      
    
  for i in range(0,LEM_number):
    chLow = dict_LEM_channel["LEM" + str(i)][0]
    chHigh = dict_LEM_channel["LEM" + str(i)][1]
    if chHigh != "ground" and chLow == "ground":
      os.system("paste <yes 0 | head -n $(cat " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Vset | wc -l)) " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Vset > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Vdet tmp0 > tmp1")
      os.system("paste <yes 0 | head -n $(cat tmp1 | wc -l)) tmp1 > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Imon tmp0 > tmp1")
      os.system("paste tmp1 Date > tmp0")
      os.system("paste tmp0 Heure > tmp1")
      os.system("paste tmp1 " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/SpT1 > LEM" + str(i) + "/DVDet")
      
    if chHigh == "ground" and chLow != "ground":
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/Vset  <yes 0 | head -n $(cat " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/Vset | wc -l))> tmp0")
      os.system("paste <yes 0 | head -n $(cat tmp1 | wc -l)) tmp1 > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/Vdet tmp0 > tmp1")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/Imon tmp0 > tmp1")
      os.system("paste tmp1 Date > tmp0")
      os.system("paste tmp0 Heure > tmp1")
      os.system("paste tmp1 " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/SpT1 > LEM" + str(i) + "/DVDet")
      
    if chHigh != "ground" and chLow != "ground":
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/Vset " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Vset > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Vdet tmp0 > tmp1")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chLow + "/Vdet tmp1 > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/Imon tmp0 > tmp1")
      os.system("paste tmp1 Date > tmp0")
      os.system("paste tmp0 Heure > tmp1")
      os.system("paste tmp1 " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + chHigh + "/SpT1 > LEM" + str(i) + "/DVDet")
      
    if chHigh == "ground" and chLow == "ground":
      print("ERROR: both faces set to ground for LEM" + str(i))
      exit(1)
      
    os.system("sed \'1d\' LEM" + str(i) + "/DVDet | sort -k6,7 -u > tmp1")   
              
    spark_parser("tmp1","tmp0")
      
    os.system("mv ./SpT0 ./LEM" + str(i) + "/")
      
    for stuff in glob.glob("tmpdir1/*"):
      os.system("sort -k6,7 " + stuff + " >> LEM" + str(i) + "/shortVdet")
        
    os.system("rm -r tmpdir1 ; rm tmp0 ; rm tmp1 ; rm tmp2 ; rm tmp3 ; rm tmp4")
    with open("LEM" + str(i) + "/shortVdet","r") as inFile:
      numlinesvdet=len(inFile.readlines())
      
    os.chdir(str(DIR))
    os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM" + str(i) + "/\",\"" + str(i) + "\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")

  sys.exit(0)

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
    
  if os.path.isdir(sys.argv[1]):
    print "ERROR: " + sys.argv[1] + " is a directory."
    sys.exit(1)
    
  if not os.path.isfile(sys.argv[1]):
    print "ERROR: Can't find file " + sys.argv[1]
    sys.exit(1)
    
  if int(sys.argv[2]) !=1 and int(sys.argv[2]) !=2 and int(sys.argv[2]) !=4:
    print "ERROR: Unexpected number of LEM"
    sys.exit(1)
    
  print "Opening file " + sys.argv[1] + " containing " + sys.argv[2] + " LEMs..."
  LEMnumber = int(sys.argv[2])
  
  os.system("sed -i \'s/[[:blank:]]/ /g\' " + sys.argv[1])
  os.system("sed -i \'s/Ch /Ch/g\' " + sys.argv[1])
  os.system("sed -i \'s/,/./g\' " + sys.argv[1])
  os.system("sed -i \'s/\\//_/g\' " + sys.argv[1])  
  
  with open(sys.argv[1], "r") as inFile:
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
  print "Analysing file " + sys.argv[1] + " with " + str(numlines) + " lines, " + str(colnumber) + " columns and " + str(Chnumber) + " channels"
  
  Path = os.path.split(os.path.abspath(sys.argv[0]))
  Dir = os.path.dirname(sys.argv[1])
  DIR = Path[0]
  File = os.path.basename(sys.argv[1])
  
  for i in  range(Chnumber):
    Chdir = sys.argv[1] + "_Ch" + str(i)
    if not os.path.isdir(Chdir):
      os.makedirs(Chdir)
    
  for LEM in range(1,LEMnumber + 1):
    lemdir = str(DIR) + "/" + str(Dir) + "/LEM" + str(LEM)
    if not os.path.isdir(lemdir):
      os.makedirs(lemdir)
    
  shortVdet=lemdir + "/shortVdet"
  
  if os.path.isfile(shortVdet):
    answer = raw_input("WARNING: shortVdet(s) already exist(s) for LEM " + str(LEM) + ", do you want to recreate it(them)? (yes/no) \n")
    while answer != "no" and answer != "yes":
      answer = raw_input("Please answer by yes or no. \n")
        
    if answer == "no":
      if LEMnumber != 4:
        shortVdet = str(DIR) + "/" + str(Dir) + "/LEM1/shortVdet"
        with open(shortVdet, "r") as inFile:
          l = inFile.readlines()
          numlinesvdet = len(l)
        os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM1/\",\"1\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
        if LEMnumber == 2:
          shortVdet = str(DIR) + "/" + str(Dir) + "/LEM2/shortVdet"
          with open(shortVdet, "r") as inFile:
            l = inFile.readlines()
            numlinesvdet = len(l)
          os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM2/\",\"2\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
      else:
        shortVdet = str(DIR) + "/" + str(Dir) + "/LEM1/shortVdet"
        with open(shortVdet, "r") as inFile:
          l = inFile.readlines()
          numlinesvdet = len(l)
        os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM1/\",\"1\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
        shortVdet = str(DIR) + "/" + str(Dir) + "/LEM2/shortVdet"
        with open(shortVdet, "r") as inFile:
          l = inFile.readlines()
          numlinesvdet = len(l)
        os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM2/\",\"2\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
        shortVdet = str(DIR) + "/" + str(Dir) + "/LEM3/shortVdet"
        with open(shortVdet, "r") as inFile:
          l = inFile.readlines()
          numlinesvdet = len(l)
        os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM3/\",\"3\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
        shortVdet = str(DIR) + "/" + str(Dir) + "/LEM4/shortVdet"
        with open(shortVdet, "r") as inFile:
          l = inFile.readlines()
          numlinesvdet = len(l)
        os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM4/\",\"4\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
    
      sys.exit(0)
    
    for folder in glob.glob(str(DIR) + "/" + str(Dir) + "/LEM*"):
      os.system("rm " + str(folder) + "/*")
  
  os.chdir(str(DIR) + "/" + str(Dir))
  adress = "./"
  j = 0
  with open(File, "r") as inFile:
    l = inFile.readline()
    for i in range(colnumber):
      k=i+1
      variable = l.split(" ")[i]
      if "Ch" in variable:
        adress = str(DIR) + "/" + str(Dir) + "/" + str(File) + "_Ch" + str(j)
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
      
  if LEMnumber != 4:
    os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch0/Vset " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch1/Vset > tmp0")
    os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch1/Vdet tmp0 > tmp1")
    os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch0/Vdet tmp1 > tmp0")
    os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch1/Imon tmp0 > tmp1")
    os.system("paste tmp1 Date > tmp0")
    os.system("paste tmp0 Heure > tmp1")
    os.system("paste tmp1 " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch1/SpT1 > LEM1/DVDet")    
    os.system("sed \'1d\' LEM1/DVDet | sort -k6,7 -u > tmp1")   
    
    spark_parser("tmp1","tmp0")
    os.system("mv ./SpT0 ./LEM1/")
    
    for stuff in glob.glob("tmpdir1/*"):
      os.system("sort -k6,7 " + stuff + " >> LEM1/shortVdet")
      
    os.system("rm -r tmpdir1 ; rm tmp0 ; rm tmp1 ; rm tmp2 ; rm tmp3 ; rm tmp4")
    with open("LEM1/shortVdet","r") as inFile:
      numlinesvdet=len(inFile.readlines())
    
    os.chdir(str(DIR))
    os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM1/\",\"1\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")
    
    if LEMnumber == 2:
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch2/Vset " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch3/Vset > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch3/Vdet tmp0 > tmp1")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch2/Vdet tmp1 > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch3/Imon tmp0 > tmp1")
      os.system("paste tmp1 Date > tmp0")
      os.system("paste tmp0 Heure > tmp1")
      os.system("paste tmp1 " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch3/SpT1 > LEM1/DVDet")    
      os.system("sed \'1d\' LEM1/DVDet | sort -k6,7 -u > tmp1")   
              
      spark_parser("tmp1","tmp0")
      
      os.system("mv ./SpT0 ./LEM2/")
      
      for stuff in glob.glob("tmpdir1/*"):
        os.system("sort -k6,7 " + stuff + " >> LEM2/shortVdet")
        
      os.system("rm -r tmpdir1 ; rm tmp0 ; rm tmp1 ; rm tmp2 ; rm tmp3 ; rm tmp4")
      with open("LEM1/shortVdet","r") as inFile:
        numlinesvdet=len(inFile.readlines())
      
      os.chdir(str(DIR))
      os.system("time root -l -q -b \'plot_histo.C(\"" + str(DIR) + "/" + str(Dir) + "/LEM2/\",\"2\",\"" + str(numlines) + "\",\"" + str(numlinesvdet) + "\")\'")    
    
  if LEMnumber == 4:
    for i in range(1,LEMnumber):
      j = i-1
      os.system("paste <yes 0 | head -n $(cat " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + str(j) + "/Vset | wc -l)) " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + str(j) + "/Vset > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + str(j) + "/Vdet tmp0 > tmp1")
      os.system("paste <yes 0 | head -n $(cat tmp1 | wc -l)) tmp1 > tmp0")
      os.system("paste " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + str(j) + "/Imon tmp0 > tmp1")
      os.system("paste tmp1 Date > tmp0")
      os.system("paste tmp0 Heure > tmp1")
      os.system("paste tmp1 " + str(DIR) + "/" + str(Dir) + "/" + str(File)  + "_Ch" + str(j) + "/SpT1 > LEM" + str(i) + "/DVDet")    
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

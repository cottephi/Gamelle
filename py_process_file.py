import glob
import sys
import string
import os
import re
import shutil
import math
from subprocess import call
from datetime import datetime
from datetime import timedelta

def writeListToFile(infoList, outFile):
  for item in infoList:
    outFile.write(item + " ")
  outFile.write("\n")
  
def date_to_hms(totaltime):
  days = totaltime.days
  hours = int(totaltime.seconds/3600)
  minutes = int(totaltime.seconds/60)-hours*60
  seconds = totaltime.seconds - 3600*hours - 60*minutes
  hours = hours + 24*days
  time = str(hours) + ":" + str(minutes) + ":" + str(seconds)
  return time
  
def create_time():
  datefile = open("./Date","r")
  timefile = open("./Heure","r")
  durationfile = open("./duration","w")
  durationfile.write("0\n")
  currdate = datefile.readline()
  currtime = timefile.readline()
  currdate = datefile.readline()[:-1].split("_")
  currtime = timefile.readline()[:-1].split(":")
  time0 = datetime(int(currdate[0]), int(currdate[1]), int(currdate[2]), int(currtime[0]), int(currtime[1]), int(currtime[2]))
  for lined, linet in zip(datefile, timefile):
    currdate = lined[:-1].split("_")
    currtime = linet[:-1].split(":")
    time1 = datetime(int(currdate[0]), int(currdate[1]), int(currdate[2]), int(currtime[0]), int(currtime[1]), int(currtime[2]))
    difftime = time1-time0
    durationfile.write(str(float(difftime.days)*24. + float(difftime.seconds)/3600.)+"\n")
  durationfile.close()
  datefile.close()
  timefile.close()
  
def date_to_hours(time1):
  datefile = open("./Date","r")
  timefile = open("./Heure","r")
  currdate = datefile.readline()
  currtime = timefile.readline()
  currdate = datefile.readline()[:-1].split("_")
  currtime = timefile.readline()[:-1].split(":")
  datefile.close()
  timefile.close()
  time0 = datetime(int(currdate[0]), int(currdate[1]), int(currdate[2]), int(currtime[0]), int(currtime[1]), int(currtime[2]))
  difftime = time1-time0
  return(float(difftime.days)*24. + float(difftime.seconds)/3600.)
  
def spark_parser():
  inFile = open("tmp1",'r')
  outFile = open("outfile",'w')
  infoList = []
  infoList2 = []
  infoList0 = []
  infoList4 = []
  infoList_previous = []
  infoList_tmp = []

  v = ""
  V = ""
  vset = ""
  vset_previous = ""

  # Get first line informations
  line = inFile.readline()
  infoList = line.split('\n') # In order to remove the '\n' at the end of the line we've just read
  infoList = infoList[0].split(' ')
  # Store first line informations
  vset = infoList[0]
  # Write first line to output file
  infoList.append("begin") # Add "begin" flag since this is the beginning of the first block
  writeListToFile(infoList, outFile)
  for line in inFile:
    # Store previous line informations in 'previous' variables
    infoList_previous = infoList[:] # Warning: you must clone using 'infoList[:]', else the list is copied as the same object but with two names!
    vset_previous = vset
    # Get current line informations
    infoList = line.split('\n')
    infoList = infoList[0].split(' ')
    # Store current line informations
    vset = infoList[0]
    # If voltage changes, save last line of previous voltage block, and the new line which is the start of a new block
    if vset_previous != vset:
      infoList_previous.append("end") # Add "end" flag since this is the end of a block
      writeListToFile(infoList_previous, outFile)
      infoList_tmp = infoList[:]
      infoList_tmp.append("begin") # Add "begin" flag since this is the beginning of a new block
      writeListToFile(infoList_tmp, outFile)

    if infoList[3] != '0':
      infoList_tmp = infoList[:]
      infoList_tmp.append("chien") # Add "chien" flag since this is not the beginning neither the end of a block
      writeListToFile(infoList_tmp, outFile)

  infoList.append("end") # Add "end" flag since this is the end of a block
  writeListToFile(infoList, outFile)
  inFile.close()
  outFile.close()
  
  os.system("awk \'!/0$/\' tmp1 > tmp2")
  os.system("sort -k1 -u tmp1 > tmp3")
  os.system("sort -k1 -u tmp2 > tmp1")
  os.system("cut -d ' ' -f 1 tmp3 > tmp4")#All lines voltages (spark or not), sorted
  os.system("cut -d ' ' -f 1 tmp1 > tmp2") #keep only voltage of lines with spark, sorted
  
  SpT0 = open('SpT0','w')
  found = "false"
  if os.stat("tmp2").st_size == 0:
    os.system("rm tmp3 ; rm tmp4 ; rm tmp2 ; rm outfile")
    return "empty"

  outfile = open('outfile','r')
  tmp2 = open('tmp2','r')
  for line2 in tmp2:
    V = line2[:-1]
    tmpV = open('./tmpV' + V,'w')
    outfile.seek(0)
    for line0 in outfile:
      v = line0.split(" ")[0]
      if V == v:
        tmpV.write(line0[:-2] + "\n")
  tmpV.close()

  tmp4 = open('tmp4','r')
  for V in tmp4:
    found = 'false'
    tmp2.seek(0)
    for v in tmp2:
      if V == v:
        found='true'
    if found=='false':
      SpT0.write(V)
  tmp4.close()
  tmp2.close()
  SpT0.close()
  os.system("rm tmp2 ; rm tmp3 ; rm tmp4 ; rm outfile")
  return

def spark_analyzer(LEM_list):
  finalelist = []
  Lemdatalist = []
  tmin = 600
  linenumber = []
  listvdetglobal = []
  sparktimeslist = []
  for LEM in LEM_list:
    shortvdet = open("./" + LEM + "/shortVset","r")
    linenumber.append(0)
    totaltime = 0
    Vtotaltime = timedelta(0,0)
    sparktime = 0
    startime = 0
    tmp_spt1 = 0
    real_spt1 = 0
    listspt1 = []
    listvarspt1 = []
    listvdet = []
    listimes = []
    for SVDline in shortvdet:
      line_items = SVDline[:-1].split(" ")
      currtime = line_items[1].split("_")
      time0 = line_items[2].split(":")
      currtime = datetime(int(currtime[0]), int(currtime[1]), int(currtime[2]), int(time0[0]), int(time0[1]), int(time0[2]))
      vdet = float(line_items[0])
      spt1 = int(line_items[3])
      checktime = line_items[4]
      if linenumber[-1] == 0:
        startime = currtime
        sparktime = currtime
        tmp_SpT1 = spt1
        real_SpT1 = spt1
        if spt1 != 0:
          save = True
          for sptime in sparktimeslist:
            if sptime < 4./60.:
              save = False
          if save:
            sparktimeslist.append(0)
      elif checktime == "begin":
        totaltime = 0
        if vdet not in listvdet:
          Vtotaltime = timedelta(0,0)
          real_spt1 = spt1
        else:
          real_spt1 = real_spt1 + spt1
        if spt1 != 0:
          save = True
          for sptime in sparktimeslist:
            if abs(sptime - date_to_hours(currtime)) < 4./60.:
              save = False
          if save:
            sparktimeslist.append(date_to_hours(currtime))
        tmp_spt1 = spt1
        startime = currtime
        sparktime = currtime
      else:
        difftime = currtime - sparktime
        if abs(difftime.seconds) > 30:
          real_spt1 = real_spt1 + spt1
          sparktime = currtime
          tmp_spt1 = spt1
          save = True
          if spt1 != 0:
            for sptime in sparktimeslist:
              if abs(sptime - date_to_hours(currtime)) < 4./60.:
                save = False
            if save:
              sparktimeslist.append(date_to_hours(currtime))
        elif abs(difftime.seconds) < 30:
          real_spt1 = real_spt1 + spt1 - tmp_spt1
          tmp_spt1 = spt1
        if checktime == "end":
          totaltime = currtime - startime
          Vtotaltime = Vtotaltime + totaltime
          listspt1.append(float(3600.*float(real_spt1)/(Vtotaltime.seconds + totaltime.days*24.*3600.)))
          listvarspt1.append(math.sqrt(listspt1[-1]))
          listvdet.append(vdet)
          if vdet not in listvdetglobal:
            listvdetglobal.append(vdet)
          listimes.append(date_to_hms(Vtotaltime))
      linenumber[-1] = linenumber[-1] + 1
    shortvdet.close()
    #if os.stat("./" + LEM + "/SpT0").st_size != 0:
      #with open("./" + LEM + "/SpT0","r") as spt0:
        #linespt0 = spt0.readline()[:-1]
        #listvdet.append(float(linespt0))
        #if float(linespt0) not in listvdetglobal:
          #listvdetglobal.append(float(linespt0))
        #listspt1.append(0)
        #listvarspt1.append(0)
        #listimes.append("0")
    Lemdatalist.append(sorted(zip(listvdet, listimes, listspt1, listvarspt1)))
    
  data = open("./sparks","w")
  lemlist = open("./lemlist","w")
  sparktimeslist_alllems = []
  duration = [line.rstrip() for line in open("./duration","r")]
  for sptime in sparktimeslist:
    found = False
    l = []
    for i in range(0,len(duration)):
      if abs(sptime - float(duration[i])) < 4./60.:
        if not found:
          l.append(i)
        found = True
      else:
        if found:
          l.append(i)
          sparktimeslist_alllems.append(l)
          break
          
  for lem in LEM_list:
    if not os.path.isdir("./" + lem + "/sparks"):
      os.makedirs("./" + lem + "/sparks")
    lineImon = [line.rstrip() for line in open("./" + lem + "/Imon")]
    lineVdet = [line.rstrip() for line in open("./" + lem + "/Vdet")]
    for i in range(0,len(sparktimeslist_alllems)):
      spfile = open("./" + lem + "/sparks/sp" + str(i), "w")
      Imonsubline = lineImon[sparktimeslist_alllems[i][0]:sparktimeslist_alllems[i][1]]
      Vdetsubline = lineVdet[sparktimeslist_alllems[i][0]:sparktimeslist_alllems[i][1]]
      durationsubline = duration[sparktimeslist_alllems[i][0]:sparktimeslist_alllems[i][1]]
      for j in range(0,len(Imonsubline)):
        spfile.write(str(durationsubline[j]) + " " + str(Vdetsubline[j]) + " " + str(Imonsubline[j]) + "\n")
      spfile.close()
  sparknumber = open("./sparknumber","w")
  sparknumber.write(str(len(sparktimeslist_alllems)))
  sparknumber.close()

  length = []
  for i in range(0,len(LEM_list)):
    length.append(len(Lemdatalist[i]))
  finalelist = sorted(zip(length,Lemdatalist,LEM_list), reverse = True)
  writeListToFile(LEM_list,lemlist)
  lemlist.close()
  
  voltspark = []
  for volt in listvdetglobal:
    voltspark.append([])
    for lem in LEM_list:
      voltspark[-1].append("NA")
  for i in range(0,len(LEM_list)):
    for k in range(0,len(listvdetglobal)):
      for j in range (0,len(Lemdatalist[i])):
        found = "NA"
        if listvdetglobal[k] == Lemdatalist[i][j][0]:
          voltspark[k][i] = Lemdatalist[i][j][2]
  
  for i in range(0,len(listvdetglobal)):
    line = str(listvdetglobal[i])
    for j in range(0,len(LEM_list)):
      line = line + " " + str(voltspark[i][j])
    data.write(line + "\n")
    
  return
  #for i in range(0,max(length)):
    #line = ""
    #for j in range(0,len(LEM_list)):
      #if i < finalelist[j][0]:
        #line = line + " " + LEM_list[j]
        #for k in range(0,len(finalelist[j][1][i])):
          #line = line + " " + str(finalelist[j][1][i][k])
    #data.write(line + "\n")

#################################################################
#############################MAIN################################  
#################################################################
 
if __name__ == '__main__':

  if os.name == "nt":
    print "ERROR: Please install Linux"
    sys.exit(1)

  if len(sys.argv) != 2: # 1 is addValueInRegion.py + 3 arguments
    print "ERROR: Need 1 arguments: the file to process."
    sys.exit(1) 
    
  script_name = sys.argv[0]
  input_file = sys.argv[1]
  
  if os.path.isdir(input_file):
    print "ERROR: " + input_file + " is a directory."
    sys.exit(1)
    
  if not os.path.isfile(input_file):
    print "ERROR: Can't find file " + input_file
    sys.exit(1)
    
  Path = os.path.split(os.path.abspath(script_name))
  Dir = os.path.dirname(input_file)
  DIR = Path[0]
  File = os.path.basename(input_file)

  numlines = 0
  l_long = ""
  with open(input_file, "r") as inFile:
    l = inFile.readlines()
    l_long = " ".join(l)
    numlines = len(l)
    inFile.close()
    
  for folder in glob.glob(str(DIR) + "/" + str(Dir) + "/A*"):
    if os.listdir(folder):
      shutil.rmtree(folder)
  
  LEM_list = []
   
  print "Opening file " + input_file + "..."
  
  os.system("sed -i \'s/[[:blank:]]/ /g\' " + input_file)
  os.system("sed -i \'s/,/./g\' " + input_file)
  os.system("sed -i \'s/\\//_/g\' " + input_file)  
  LEM_number = 0
  
  with open(input_file, "r") as inFile:
    LEM_number = l[0].count("A")
    LEM_number2 = l[1].count("A")
    colnumber = len(l[0].split(" "))
    colnumber2 = len(l[1].split(" "))
    if l[0].count("Heure") == 0:
      print "ERROR: Header should have a column 'Heure'"
      sys.exit(1)
    if colnumber != colnumber2:
      print "ERROR: Not same number of columns in header and rest of file"
      sys.exit(1)
    if LEM_number != LEM_number2:
      print "ERROR: Not same number of LEMs in header and rest of file"
      sys.exit(1)
    for i in range(len(l)):
      if len(l[i].split(" ")) != colnumber:
        print "ERROR: line " + str(i) + " is corrupted. Please check it."
        sys.exit(1)
  print "Analysing file " + input_file + " with " + str(numlines) + " lines, " + str(colnumber) + " columns and " + str(LEM_number) + " LEMs"
    
  
  os.chdir(str(DIR) + "/" + str(Dir))
  adress = "./"
  j = 0
  with open(File, "r") as inFile:
    l = inFile.readline()
    for i in range(colnumber):
      k=i+1
      variable = l.split(" ")[i]
      if "A" in variable:
        LEM_list.append(variable)
        Chdir = str(DIR) + "/" + str(Dir) + "/" + variable
        if not os.path.isdir(Chdir):
          os.makedirs(Chdir)
        adress = Chdir
        j += 1
      else:
        if k == colnumber:
          variable = variable[:-2]
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
  if os.path.isfile("outfile"):
      os.remove("outfile")      
      
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
    vset = open(str(DIR) + "/" + str(Dir) + "/" + LEM_list[i] + "/Vset")
    date = open("Date")
    heure = open("Heure")
    spt1 = open(str(DIR) + "/" + str(Dir) + "/" + LEM_list[i] + "/SpT1")
    DVSet = open(str(DIR) + "/" + str(Dir) + "/" + LEM_list[i] + "/DVSet","w")
    k = 0
    for linevs, linedate, linespt, lineheure in zip(vset, date, spt1, heure):
      if k == 0:
        DVSet.write("Vset Date Heure SpT1 \n")
        k = k+1
      else: 
        DVSet.write(str(float(linevs[:-1])) + " " + linedate[:-1] + " " + lineheure[:-1] + " " + str(int(linespt)) + "\n")
    vset.close()
    date.close()
    heure.close()
    spt1.close()
    DVSet.close()
    os.system("sed \'1d\' " + LEM_list[i] + "/DVSet | sort -k2,3 -u > tmp1")

    if spark_parser() == "empty":
      print("No spark in LEM " + LEM_list[i])
      os.system("rm tmp0 ; rm tmp1")
      continue
    
    os.system("mv ./SpT0 ./" + LEM_list[i] + "/")
    for stuff in glob.glob("./tmpV*"):
      os.system("sort -k2,3 " + stuff + " >> " + LEM_list[i] + "/shortVset")
    os.system("rm ./tmp*")
  create_time()
  for lem in LEM_list:
    os.system("sed \'1d\' ./" + lem + "/Vdet > ./tmp")
    os.system("paste -d ' ' duration tmp > TMP")
    os.system("sed \'1d\' ./" + lem + "/Imon > ./tmp")
    os.system("paste -d ' ' TMP tmp > ./" + lem + "/lemdata")
  spark_analyzer(LEM_list)

  os.system("rm tmp ; rm TMP")
  os.chdir(str(DIR))
  os.system("root -l -q -b \'./plot_histo.C(\"" + str(DIR) + "/\",\"" + str(Dir) + "/\")\'")
  os.system("rm ./AutoDict*")
  sys.exit(0)

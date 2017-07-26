
import sys#, string, 
import os
from subprocess import call

def writeListToFile(infoList, outFile):
  for item in infoList:
    outFile.write(item + " ")
  outFile.write("\n")
  
if __name__ == '__main__':
  if len(sys.argv) != 3: # 1 is addValueInRegion.py + 3 arguments
    print "I was expecting 2 arguments: infile and outfile"
    print "Will exit now."
    sys.exit(1) 
  inFile = open(sys.argv[1],'r')
  outFile = open(sys.argv[2],'w')
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
    
  os.system("awk '!/0$/' "+sys.argv[1]+" > tmp2")
  os.system("sort -k4,5 -u "+sys.argv[1]+" > tmp3")  
  os.system("sort -k4,5 -u tmp2 > "+sys.argv[1])
  os.system("cut -f 4,5 tmp3 > tmp4")
  os.system("cut -f 4,5 "+sys.argv[1]+" > tmp2")
  os.system("mkdir tmpdir1")
  
  tmp2=open('tmp2','r')
  tmp4=open('tmp4','r')
  tmp0=open(sys.argv[2],'r')
  SpT0=open('SpT0','w')
  found="false"
  
  for line2 in tmp2:
    infoList2 = line2.split('\n')
    infoList2 = infoList2[0].split('\t')
    V=infoList2[0]+infoList2[1]
    tmpV=open('tmpdir1/tmpV'+V,'w')
    tmp0.seek(0)
    for line0 in tmp0:
      infoList0 = line0.split('\n')
      infoList0 = infoList0[0].split(' ')
      v=infoList0[3]+infoList0[4]
      if V == v:
        writeListToFile(infoList0,tmpV)
        
  tmp2.seek(0)
  for line4 in tmp4:
    found='false'
    infoList4 = line4.split('\n')
    infoList4 = infoList4[0].split('\t')
    V=infoList4[0]+" "+infoList4[1]
    tmp2.seek(0)
    for line2 in tmp2:
      infoList2 = line2.split('\n')
      infoList2 = infoList2[0].split('\t')
      v=infoList2[0]+" "+infoList2[1]
      if V == v:
        found='true'
    if found=='false':
      V=V+"\n"
      SpT0.write(V)
      
  tmp0.close()
  tmp2.close()
  tmp4.close()
  SpT0.close()
         
  sys.exit(2)
  



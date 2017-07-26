#! /bin/bash

if [ $# -ne 2 ] ; then
   echo "Need 2 arguments : the file to process and the number of LEMs in it."
   exit 1
fi


if [ ! -e "$1" ] ; then
   echo "ERROR: Can not find file $1"
   exit 1
fi

if [[ -d $1 ]] ; then
    echo "ERROR: $1 is a directory"
    exit 1
fi

if ! [ "$2" -eq "$2" ] 2>/dev/null ; then
   echo "ERROR: Number of LEM must be integer"
   exit 1
fi
if [ $2 -ne 1 ] && [ $2 -ne 2 ] && [ $2 -ne 4 ] ; then
   echo "ERROR: Unexpected number of LEM"
   exit 1
fi

LEMnumber=$2

sed -i 's/Ch /Ch/g' $1
sed -i 's/[[:blank:]]/ /g' $1
sed -i 's/,/./g' $1
sed -i 's/\//_/g' $1

numlines=$(wc -l < $1)
Chnumber=$(head -n 1 $1 | grep -o "Ch*" | wc -l)
Chnumber2=$(head -n 2 $1 | grep -o "Ch*" | wc -l)
let Chnumber1=2*Chnumber
if [ $Chnumber1 -ne $Chnumber2 ] ; then
   echo "ERROR: not same number of channel on header and in file"
   exit 1
fi
colnumber=$(head -n 1 $1 | wc -w )
colnumbertest=$(head -n 2 $1 | tail -n 1 | wc -w )
if ! grep -q Heure "$1" ; then
   echo "ERROR: Should have a column 'Heure'. Please add it after the column 'Date'."
   exit 0
fi
if [ $colnumbertest -ne $colnumber ] ; then
   echo "ERROR: number of columns in header different from other lines"
   exit 0
fi

echo "Analysing file $1 with $numlines lines, $colnumber columns and $Chnumber channels"

dir=$(dirname $1)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
file=$(basename $1)

let i=0
while [ $i -lt $Chnumber ] ; do
   if [ ! -e $1_Ch$i ] ; then
      mkdir $1_Ch$i
   fi
   let i=i+1
done
let i=1
let j=0

while [ $i -le $LEMnumber ] ; do
   if [ ! -e $dir/LEM$i ] ; then
      mkdir $dir/LEM$i
   fi
   let i=i+1
done
let i=0

if [ -e $dir/LEM1/shortVdet ] ; then
   echo "shortVdet(s) already exist(s). Do you want to recreate it(them)? (y/n)"
   read answer
   while [ "$answer" != "y" ] && [ "$answer" != "n" ] ; do
      echo "Please answer by y or n"
      read answer
   done
   if [ "$answer" == "n" ] ; then
      if [ $LEMnumber -ne 4 ] ; then
         numlinesvdet=$(wc -l < $dir/LEM1/shortVdet)
         time root -l -q -b 'plot_histo.C("'$dir'/LEM1/","1","'$numlines'","'$numlinesvdet'")'
         if [ $LEMnumber -eq 2 ] ; then
            numlinesvdet=$(wc -l < $dir/LEM2/shortVdet)
            time root -l -q -b 'plot_histo.C("'$dir'/LEM2/","2","'$numlines'","'$numlinesvdet'")'
         fi
      elif [ $LEMnumber -eq 4 ] ; then
         numlinesvdet=$(wc -l < $dir/LEM1/shortVdet)
         time root -l -q -b 'plot_histo.C("'$dir'/LEM1/","1","'$numlines'","'$numlinesvdet'")'
         numlinesvdet=$(wc -l < $dir/LEM2/shortVdet)
         time root -l -q -b 'plot_histo.C("'$dir'/LEM2/","2","'$numlines'","'$numlinesvdet'")'
         numlinesvdet=$(wc -l < $dir/LEM3/shortVdet)
         time root -l -q -b 'plot_histo.C("'$dir'/LEM3/","3","'$numlines'","'$numlinesvdet'")'
         numlinesvdet=$(wc -l < $dir/LEM4/shortVdet)
         time root -l -q -b 'plot_histo.C("'$dir'/LEM4/","4","'$numlines'","'$numlinesvdet'")'
      fi
      exit
   fi
   for folder in $dir/LEM* ; do
      if [ -e $folder/shortVdet ] ; then
         rm $folder/shortVdet*
      fi
   done
fi

cd $dir
adress="./"
let i=0
let j=0
while [ $i -lt $colnumber ] ; do
   let k=i+1
   variable=$(head -n 1 $file | cut -d ' ' -f $k)
   if grep "Ch*" <<< $variable > /dev/null ; then
      adress=""$file"_Ch"$j""
      let j=j+1
   else
      if [ $k -eq $colnumber ] ; then 
         variable=${variable%?}
      fi
      cut -d ' ' -f $k "$file" > $adress/$variable
   fi
   let i=i+1
done

for folder in ./* ; do
   if [ -e "$folder/DVDet" ] ; then
      rm $folder/DVDet 
   fi
done
if [ -e "tmp0" ] ; then
   rm tmp0
fi
if [ -e "tmp1" ] ; then
   rm tmp1
fi
if [ -e "tmp2" ] ; then
   rm tmp2
fi
if [ -e "tmp3" ] ; then
   rm tmp3
fi
if [ -e "tmp4" ] ; then
   rm tmp4
fi
if [ -d "tmpdir1" ] ; then
   rm -r tmpdir1
fi


cut -d '_' -f 1 Date > day
cut -d '_' -f 2 Date > month
cut -d '_' -f 3 Date > year
rm Date
paste -d '_' year month > tmp0
paste -d '_' tmp0 day > Date
rm day
rm year
rm month

if [ $LEMnumber -ne 4 ] ; then
   paste ""$file"_Ch0/Vset" ""$file"_Ch1/Vset" > tmp0
   paste ""$file"_Ch1/Vdet" tmp0 > tmp1
   paste ""$file"_Ch0/Vdet" tmp1 > tmp0
   paste ""$file"_Ch1/Imon" tmp0 > tmp1
   paste tmp1 Date > tmp0
   paste tmp0 Heure > tmp1
   paste tmp1 ""$file"_Ch1/SpT1" > LEM1/DVDet
   sed '1d' LEM1/DVDet | sort -k6,7 -u > tmp1

   python ../spark_parser.py tmp1 tmp0
   mv ./SpT0 ./LEM1/

   for stuff in tmpdir1/* ; do
      sort -k6,7 $stuff >> "LEM1/shortVdet"
   done

   rm -r tmpdir1
   rm tmp0
   rm tmp1
   rm tmp2
   rm tmp3
   rm tmp4
   numlinesvdet=$(wc -l < LEM1/shortVdet)

   cd $DIR

   time root -l -q -b 'plot_histo.C("'$dir'/LEM1/","1","'$numlines'","'$numlinesvdet'")'
   if [ $LEMnumber -eq 2 ] ; then
      paste ""$file"_Ch2/Vset" ""$file"_Ch3/Vset" > tmp0
      paste ""$file"_Ch3/Vdet" tmp0 > tmp1
      paste ""$file"_Ch2/Vdet" tmp1 > tmp0
      paste ""$file"_Ch3/Imon" tmp0 > tmp1
      paste tmp1 Date > tmp0
      paste tmp0 Heure > tmp1
      paste tmp1 ""$file"_Ch3/SpT1" > LEM2/DVDet
      sed '1d' LEM1/DVDet | sort -k6,7 -u > tmp1
   
      python ../spark_parser.py tmp1 tmp0
      mv ./SpT0 ./LEM2/
   
      for stuff in tmpdir1/* ; do
         sort -k6,7 $stuff >> "LEM2/shortVdet"
      done

      rm -r tmpdir1
      rm tmp0
      rm tmp1
      rm tmp2
      rm tmp3
      rm tmp4
      numlinesvdet=$(wc -l < LEM2/shortVdet)

      cd $DIR

      time root -l -q -b 'plot_histo.C("'$dir'/LEM2/","2","'$numlines'","'$numlinesvdet'")'
   fi
fi

if [ $LEMnumber -eq 4 ] ; then
   let i=1
   while [ $i -le $LEMnumber ] ; do
      let j=i-1
      paste <(yes 0 | head -n $(cat ""$file"_Ch"$j"/Vset" | wc -l)) ""$file"_Ch$j/Vset" > tmp0
      paste ""$file"_Ch$j/Vdet" tmp0 > tmp1
      paste <(yes 0 | head -n $(cat tmp1 | wc -l)) tmp1 > tmp0
      paste ""$file"_Ch$j/Imon" tmp0 > tmp1
      paste tmp1 Date > tmp0
      paste tmp0 Heure > tmp1
      paste tmp1 ""$file"_Ch$j/SpT1" > LEM$i/DVDet
      sed '1d' LEM$i/DVDet | sort -k6,7 -u > tmp1
   
      python ../spark_parser.py tmp1 tmp0
      mv ./SpT0 ./LEM$i/
   
      for stuff in tmpdir1/* ; do
         sort -k6,7 $stuff >> "LEM"$i"/shortVdet"
      done

      rm -r tmpdir1
      rm tmp0
      rm tmp1
      rm tmp2
      rm tmp3
      rm tmp4
      numlinesvdet=$(wc -l < LEM$i/shortVdet)

      cd $DIR

      time root -l -q -b 'plot_histo.C("'$dir'/LEM'$i'/","'$i'","'$numlines'","'$numlinesvdet'")'
      let i=i+1
   done
fi

exit 0





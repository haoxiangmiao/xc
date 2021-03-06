# -*- coding: utf-8 -*-
import csv

fNameIn= 'arcelor_ipe_shapes.csv'
fNameOut= 'dict_arcelor_ipe_shapes.py'
dictName= 'IPEshapes'

# Section axis:

#    ARCELOR          XC

#                     ^ Y                    
#                     |

#     -----         -----
#       |             | 
#       | -> Y        | -> Z
#       |             |
#     -----         -----

#       |
#       v Z

# The axis used in Arcelor documentation are different from those used in XC
# (strong axis parallel to z axis) in other words: values for Y and Z axis 
# are swapped with respect to those in the catalog.

def writeIPEShapeRecord(out,row):
  name= row[0]
  if(name.find('IPE')!=-1):
    out.write(dictName+"['" + row[0] + "']= ")
    out.write("{")
    out.write("\'nmb\':\'" + row[0] +"\', ")
    out.write("\'P\':" + row[1]+", ")
    out.write("\'h\':" + row[2]+"e-3, ")
    out.write("\'b\':" + row[3]+"e-3, ")
    out.write("\'tw\':" + row[4]+"e-3, ")
    out.write("\'tf\':" + row[5]+"e-3, ")
    out.write("\'r\':" + row[6]+"e-3, ")
    out.write("\'A\':" + row[7]+"e-4, ")
    out.write("\'hi\':" + row[8]+"e-3, ")
    out.write("\'d\':" + row[9]+"e-3, ")
    out.write("\'FI\':" + row[10]+", ")
    out.write("\'Pmin\':" + row[11]+"e-3, ")
    out.write("\'Pmax\':" + row[12]+"e-3, ")
    out.write("\'AL\':" + row[13]+", ")
    out.write("\'AG\':" + row[14]+", ")
    out.write("\'Iz\':" + row[15]+"e-8, ")
    out.write("\'Wzel\':" + row[16]+"e-6, ")
    out.write("\'Wzpl\':" + row[17]+"e-6, ")
    out.write("\'iz\':" + row[18]+"e-2, ")
    out.write("\'Avy\':" + row[19]+"e-4, ")
    out.write("\'Iy\':" + row[20]+"e-8, ")
    out.write("\'Wyel\':" + row[21]+"e-6, ")
    out.write("\'Wypl\':" + row[22]+"e-6, ")
    out.write("\'iy\':" + row[23]+"e-2, ")
    out.write("\'Ss\':" + row[24]+"e-3, ")
    out.write("\'It\':" + row[25]+"e-8, ")

    out.write("\'E\': 210000e6, ")
    out.write("\'nu\': 0.3")
    out.write(" }\n")

outfile= open(fNameOut,mode='w')
with open(fNameIn, mode='r') as infile:
  reader = csv.reader(infile)
  for rows in reader:
    if(len(rows)>0):
      writeIPEShapeRecord(outfile,rows)

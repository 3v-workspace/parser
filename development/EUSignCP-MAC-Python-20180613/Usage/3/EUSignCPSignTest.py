# -*- coding: utf-8 -*-
print("EUSignCP Python Sign Test:")

from EUSignCP import *
EULoad()
pIface = EUGetInterface()
pIface.Initialize()

print("Library Initialized")

dwType = 0
lDescription = []
pIface.EnumKeyMediaTypes(dwType, lDescription)
while lDescription[0] != "файлова система (каталоги користувача)":
	dwType += 1
	if not pIface.EnumKeyMediaTypes(dwType, lDescription):
		print ("KeyMedia not found")
		pIface.Finalize()
		EUUnload()
		exit()

pKM = {"szPassword" : b"12345677", "dwDevIndex": 0, "dwTypeIndex": dwType}
try:
	pIface.ReadPrivateKey(pKM, None)
except:
	print ("Key reading failed")
	pIface.Finalize()
	EUUnload()
	exit()

print("Key success read")

pData = open(b"TestFile.txt", "rb").read()
lSign = []
pIface.SignData(pData, len(pData), None, lSign)

print("Data sign done")

try:
	pIface.VerifyData(pData, len(pData), None, lSign[0], len(lSign[0]), None)
except:
	print ("VerifyData failed")

pIface.Finalize()
EUUnload()

print("EUSignCP Python Sign Test done.")

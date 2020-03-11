print("EUSignCP Python Session Test:")

from EUSignCP import *
EULoad()
pIface = EUGetInterface()
try:
	pIface.Initialize()
except Exception as e:
	print ("Initialize failed"  + str(e))
	EUUnload()
	exit()

print("Library Initialized")

try:
	if not pIface.IsPrivateKeyReaded():
		pIface.ReadPrivateKeyFile("Key-6.dat", "12345677", None)
except Exception as e:
	print ("Key reading failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

if pIface.IsPrivateKeyReaded():
	print("Key success read")
else:
	print("Key read failed")
	pIface.Finalize()
	EUUnload()
	exit()

lData = []
pvSession = []

try:
	pIface.ClientSessionCreateStep1(10000, pvSession, lData)
except Exception as e:
	print ("ClientSessionCreateStep1 failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

pvServer = []

try:
	pIface.ServerSessionCreateStep1(10000, lData[0], len(lData[0]), pvServer, lData)
except Exception as e:
	print ("ServerSessionCreateStep1 failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.ClientSessionCreateStep2(pvSession[0], lData[0], len(lData[0]), lData)
except Exception as e:
	print ("ClientSessionCreateStep2 failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.ServerSessionCreateStep2(pvServer[0], lData[0], len(lData[0]))
except Exception as e:
	print ("ServerSessionCreateStep2 failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

try:
	if pIface.SessionIsInitialized(pvSession[0]) and pIface.SessionIsInitialized(pvServer[0]):
		print("Sessions success created")
	else:
		print("Sessions creation failed")
		pIface.Finalize()
		EUUnload()
		exit()
except Exception as e:
	print ("SessionIsInitialized failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

pCert = {}

try:
	pIface.SessionGetPeerCertificateInfo(pvSession[0], pCert)
except Exception as e:
	print ("SessionIsInitialized failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

print("Session certificate:")
print("Issuer: ", pCert["pszIssuer"])
print("Serial: ", pCert["pszSerial"])
print("BeginTime: ", pCert["stCertBeginTime"])

print("Session encryption:")
print("Plain text: Test")

try:
	pIface.SessionEncrypt(pvSession[0], b"Test", len("Test"), lData);
except Exception as e:
	print ("SessionEncrypt failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

print ("Encrypted text: ", lData[0])

try:
	pIface.SessionDecrypt(pvServer[0], lData[0], len(lData[0]), lData);
except Exception as e:
	print ("SessionDecrypt failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

print ("Decrypted text: ", lData[0])

try:
	pIface.SessionDestroy(pvSession[0])
except Exception as e:
	print ("SessionDestroy failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.SessionIsInitialized(pvSession[0])
except Exception as e:
	print ("SessionIsInitialized failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.SessionDestroy(pvServer[0])
except Exception as e:
	print ("SessionDestroy failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

pIface.Finalize()
EUUnload()

print("EUSignCP Python Session Test done.")

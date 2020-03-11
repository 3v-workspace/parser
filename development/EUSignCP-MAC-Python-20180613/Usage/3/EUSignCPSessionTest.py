print("EUSignCP Python Session Test:")

from EUSignCP import *
EULoad()
pIface = EUGetInterface()
pIface.Initialize()

print("Library Initialized")

if not pIface.IsPrivateKeyReaded():
	pIface.ReadPrivateKeyFile(b"Key-6.dat", b"12345677", None)

if pIface.IsPrivateKeyReaded():
	print("Key success read")
else:
	print("Key read failed")
	exit()

lData = []
pvSession = []
pIface.ClientSessionCreateStep1(10000, pvSession, lData)
pvServer = []
pIface.ServerSessionCreateStep1(10000, lData[0], len(lData[0]), pvServer, lData)
pIface.ClientSessionCreateStep2(pvSession[0], lData[0], len(lData[0]), lData)
pIface.ServerSessionCreateStep2(pvServer[0], lData[0], len(lData[0]))

if pIface.SessionIsInitialized(pvSession[0]) and pIface.SessionIsInitialized(pvServer[0]):
	print("Sessions success created")
else:
	print("Sessions creation failed")
	exit()

pCert = {}
pIface.SessionGetPeerCertificateInfo(pvSession[0], pCert)

print("Session certificate:")
print("Issuer: ", pCert["pszIssuer"])
print("Serial: ", pCert["pszSerial"])
print("BeginTime: ", pCert["stCertBeginTime"])

print("Session encryption:")
print("Plain text: Test")
pIface.SessionEncrypt(pvSession[0], b"Test", len("Test"), lData);
print ("Encrypted text: ", lData[0])
pIface.SessionDecrypt(pvServer[0], lData[0], len(lData[0]), lData);
print ("Decrypted text: ", lData[0])
pIface.SessionDestroy(pvSession[0])
pIface.SessionIsInitialized(pvSession[0])
pIface.SessionDestroy(pvServer[0])
pIface.Finalize()
EUUnload()

print("EUSignCP Python Session Test done.")

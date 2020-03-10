# -*- coding: utf-8 -*-
print("EUSignCP Python Signer Test:")

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

lSigner = []

try:
	pIface.GetFileSigner(0, "FileToSign.txt.p7s", None, lSigner)
except Exception as e:
	print ("GetFileSigner failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

pvContext = []

try:
	pIface.CtxCreate(pvContext)
except Exception as e:
	print ("CtxCreate failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

lCertificate = []
pInfo = {}

try:
	pIface.GetFileSignerInfo(0, "FileToSign.txt.p7s", pInfo, lCertificate)
except Exception as e:
	print ("GetSignerInfo failed"  + str(e))
	pIface.CtxFree(pvContext[0])
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.CtxCreateEmptySignFile(pvContext[0], EU_KEYS_TYPE_DSTU_AND_ECDH_WITH_GOSTS, "FileToSign.txt", lCertificate[0], len(lCertificate[0]), "FileEmptySign.p7s")
except Exception as e:
	print ("CtxCreateEmptySignFile failed"  + str(e))
	pIface.CtxFree(pvContext[0])
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.CtxAppendSignerFile(pvContext[0], EU_KEYS_TYPE_DSTU_AND_ECDH_WITH_GOSTS, lSigner[0], len(lSigner[0]), lCertificate[0], len(lCertificate[0]), "FileEmptySign.p7s", "FileWithSigner.txt.p7s")
except Exception as e:
	print ("CtxAppendSignerFile failed"  + str(e))
	pIface.CtxFree(pvContext[0])
	pIface.Finalize()
	EUUnload()
	exit()

try:
	pIface.CtxFree(pvContext[0])
except Exception as e:
	print ("CtxFree failed"  + str(e))
	pIface.Finalize()
	EUUnload()
	exit()

pIface.Finalize()
EUUnload()

print("EUSignCP Test successed.")

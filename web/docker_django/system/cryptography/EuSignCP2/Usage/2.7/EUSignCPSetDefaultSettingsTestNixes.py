# -*- coding: utf-8 -*-
print("EUSignCP Python Set Default Settings Test:")

from EUSignCP import *
EULoad()
pIface = EUGetInterface()
pIface.Initialize()

print("Library Initialized")

if not pIface.DoesNeedSetSettings():
	print("Setting is already setuped")
	pIface.Finalize()
	EUUnload()
	exit()

dSettings = {}
dSettings["szPath"] = u"/var/certificates"
dSettings["bCheckCRLs"] = False
dSettings["bAutoRefresh"] = True
dSettings["bOwnCRLsOnly"] = False
dSettings["bFullAndDeltaCRLs"] = False
dSettings["bAutoDownloadCRLs"] = False
dSettings["bSaveLoadedCerts"] = True
dSettings["dwExpireTime"] = 3600

pIface.SetFileStoreSettings(dSettings)

dSettings = {}

pIface.GetFileStoreSettings(dSettings)
if len(dSettings["szPath"]) == 0:
	print("Error setup settings")
	pIface.Finalize()
	EUUnload()
	exit()

dSettings = {}
dSettings["bUseProxy"] = False
dSettings["bAnonymous"] = False
dSettings["szAddress"] = ""
dSettings["szPort"] = ""
dSettings["szUser"] = ""
dSettings["szPassword"] = ""
dSettings["bSavePassword"] = False

pIface.SetProxySettings(dSettings)

dSettings = {}
dSettings["bUseOCSP"] = False
dSettings["bBeforeStore"] = False
dSettings["szAddress"] = ""
dSettings["szPort"] = ""

pIface.SetOCSPSettings(dSettings)

dSettings = {}
dSettings["bGetStamps"] = False
dSettings["szAddress"] = ""
dSettings["szPort"] = ""

pIface.SetTSPSettings(dSettings)

dSettings = {}
dSettings["bUseLDAP"] = False
dSettings["szAddress"] = ""
dSettings["szPort"] = ""
dSettings["bAnonymous"] = False
dSettings["szUser"] = ""
dSettings["szPassword"] = ""

pIface.SetLDAPSettings(dSettings)

dSettings = {}
dSettings["bUseCMP"] = False
dSettings["szAddress"] = ""
dSettings["szPort"] = ""
dSettings["szCommonName"] = ""

pIface.SetCMPSettings(dSettings)

dSettings = {}
dSettings["bOfflineMode"] = True

pIface.SetModeSettings(dSettings)

pIface.Finalize()
EUUnload()

print("EUSignCP Python Set Default Setting Test done.")

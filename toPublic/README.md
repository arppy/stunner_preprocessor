# Stunner Dataset

[Stunner](https://github.com/bilickiv/stunner) Android app has been available for download from the [Play Store](https://play.google.com/store/apps/details?id=hu.uszeged.inf.wlab.stunner)  since 26th December 2013. Over the years, stunner has been downloaded and installed by 14,727 users on 745 different device. The functionality of our app is to provide the user with information about the current network environment of the phone: private and public IP, NAT type, MAC address, and some other network related [details](http://www.inf.u-szeged.hu/~berta/publications/P2P2014_46.pdf). At the same time, the app collects data about the phone and logs it to our servers. The data collection includes more than 70 million data records from over 100 countries measuring the NAT characteristics of more than 1300 carriers and over 35000 WiFi environments. 

## Citation Request

The dataset was provided by the University of Szeged as a result of an ongoing data collection campaign, and publicly available at http://www.inf.u-szeged.hu/stunner for non-profit usage. The campaign was supported by the Hungarian Government and the European Regional Development Fund under the grant number GINOP-2.3.2-15-2016-00037 (“Internet of Living Things”) and by the Hungarian Ministry of Human Capacities (grant 20391-3/2018/FEKUSTRAT)

**Please cite this paper:** Zoltán Szabó, Krisztián Téglás, Árpád Berta, Márk Jelasity, Vilmos Bilicki. **Stunner: A Smart Phone Trace for Developing Decentralized Edge Systems.** _In Proceedings of the 19th International Conference on Distributed Applications and Interoperable Systems (DAIS 2019)_, Copenhagen, Denmark, 2019. 

[Download: BibTex](http://www.inf.u-szeged.hu/~berta/publications/STBJB19.bib)

```bibtex
@inproceedings{STBJB19,
  author="Szab{\'o}, Zolt{\'a}n and T{\'e}gl{\'a}s, Kriszti{\'a}n and Berta, {\'A}rp{\'a}d and Jelasity, M{\'a}rk and Bilicki, Vilmos",
  editor="Pereira, Jos{\'e} and Ricci, Laura",
  title="Stunner: A Smart Phone Trace for Developing Decentralized Edge Systems",
  booktitle="Proceedings of the 19th International Conference on Distributed Applications and Interoperable Systems ({DAIS} 2019)",
  year="2019",
  publisher="Springer International Publishing",
  address="Cham",
  pages="108--115",
  abstract="Conducting research into edge and fog computing often involves experimenting with actual deployments, which is costly and time-consuming, so we need to rely on realistic simulations at least in the early phases of research. To be able to do so we need to collect real data that allows us to perform trace-based simulation and to extract crucial statistics. To achieve this for the domain of distributed smartphone applications, for many years we have been collecting data via smartphones concerning NAT type, the availability of WiFi and cellular networks, the battery level, and many more attributes. Recently, we enhanced our data collecting Android app Stunner by taking actual P2P measurements. Here, we outline our data collection method and the technical details, including some challenges we faced with data cleansing. We present a preliminary set of statistics based on the data for illustration. We also make our new database freely available for research purposes.",
  isbn="978-3-030-22496-7"
  location="Copenhagen, Denmark"
  doi="10.1007/978-3-030-22496-7_7"
}
```

[I agree with the terms and conditions. Download: Data](https://drive.google.com/drive/folders/1vChNLYOa57MaJTzpsxmNIrVDN14JoLbO)

## Measurement description

In versions 1-19 measurements were triggered either by the user (when the app is used) or by specific events that signal the change of some of the properties we measure: battery charging status, network availability. There was periodic measurement as well every 10 minutes, if no other events occurred. [More info.](http://www.inf.u-szeged.hu/~berta/publications/P2P2014_46.pdf)


Since version 20, we collect data only when the phone is on a charger. This was necessary because Android has become very hostile to background processes when the phone is not on a charger, in an effort to save energy. Android event handlers have also became more restricted, so we can use them only under limited circumstances or on early Androids. The events raised by connecting to a charger or a network can still be caught by the Android job scheduler, but the timing of these events is not very reliable. We check the state of the phone every minute, and if there is a change in any important locally available networking parameter or in charging availability, we perform a full measurement. A measurement is still triggered if the user explicitly requests one, and it is also triggered by an incoming P2P measurement request. Also, if there is no measurement for at least 10 minutes, a full measurement is performed. [More info.](https://www.doi.org/10.1007/978-3-030-22496-7_7)

P2P connection measurements are also a new feature in the version 20 that are performed every time a measurement is carried out. They are based on the WebRTC protocol, with Firebase as a signaling server, and a STUN server. We build and measure only direct connections, the TURN protocol for relaying is not used. Every node that is online (has network access and is on a charger) attempts to connect to a peer. To do this, the node sends a request to the Firebase server after collecting its own network data. The server attempts to find a random online peer and manages the information exchange using the Session Description Protocol (SDP) to help create a two-way P2P connection over UDP. If the two-way channel is successfully opened then a tiny data massage is exchanged. The channel is always closed at the end of the measurement. One connection is allowed at a time, every additional offer is rejected. The signaling server maintains an online membership list. [More info.](https://www.doi.org/10.1007/978-3-030-22496-7_7)

## Data structure

Stunner Data is available in format of CSV files per user per month.

| Field name | since (version) | column description | Code description |
| ------------|:---:|:-------------:|:-----------:|
| *fileCreationDate* | 13 |  server side timestamp when the file was created on the server which contains the measurement ||
| *serverSideUploadDate* | 1 | server side timestamp when the measured data was uploaded to the server ||
| *deviceID* | 1 | unique [android device ID](https://developer.android.com/reference/android/provider/Settings.Secure.html#ANDROID_ID) (hashed)||
| *measurementID* | 20 | ascendant measurement ID (ID restart is possible) ||
| *timestamp* | 1 | UNIX [timestamp](https://developer.android.com/reference/java/sql/Timestamp) which represent the start of the measurement ||
| *timeZoneUTCOffset* | 9 | difference between UTC and local time ||
| *triggerCode* | 4 | Event that started the measurement | -1: UNKNOWN (since v10), 0: USER, 1 : CONNECTION CHANGED, 2: BATTERY LOW, 3: BATTERY POWER CONNECTED, 4: BATTERY POWER DISCONNECTED  5: SCHEDULED STATE CHECK, 6: BOOT COMPLETED, 7: CONNECTION LOST (v1-19), 8: CONNECTION ESTABLISHED (v1-19), 9: SERVICE TOGGLED, 10: ACTION SHUTDOWN (since v20), 11: FIREBASE MESSAGE IS RECEIVED (since v20), 12: SERVICE TOGGLED OFF (since v22), 13: FIRST START (since v20), 15: TIME CHANGED (v20-22), 16: TIMEZONE CHANGED (since v20), 17: DATE CHANGED (v20-22), 18: LAST DISCONNECT CHANGED (v20-22), 19: AIRPLANE MODE CHANGED (since v20) |
| *androidVersion* | 1 | android [version](https://developer.android.com/reference/android/os/Build.VERSION.html#SDK_INT) of the phone||
| *appVersion* | 11 | current application [version](https://developer.android.com/studio/publish/versioning) on the phone ||
| *connectionMode* | 4 | type of the connection | -1: Not connected, 0: Mobile, 1: WiFi, 2: other |
| *networkInfo* | 20 | network connection [description](https://developer.android.com/reference/android/net/NetworkInfo) | 0: IDLE, 1: SCANNING, 2: CONNECTING, 3: AUTHENTICATING, 4: OBTAINING IPADDR, 5: CONNECTED, 6: SUSPENDED, 7: DISCONNECTING, 8: DISCONNECTED, 9: FAILED, 10: BLOCKED,  11: VERIFYING POOR LINK, 12: CAPTIVE PORTAL CHECK |
| *localIP* | 1 | hashed local(private) IP address ||
| *macAddress* | 1 | hashed MAC [address](https://developer.android.com/reference/android/net/MacAddress) of the WiFi adapter ||
| *ssid:* | 1 | hashed network [ID](https://developer.android.com/reference/android/net/wifi/WifiManager) ||
| *state:* | 20 | wifi [state](https://developer.android.com/reference/android/net/wifi/WifiManager) | 0: WIFI STATE DISABLING, 1: WIFI STATE DISABLED, 2: WIFI STATE ENABLING, <br> 3: WIFI STATE ENABLED, 4: WIFI STATE UNKNOWN|
| *bandwith* | 1 | network [bandwith](https://developer.android.com/reference/android/net/ConnectivityManager) ||
| *rssi* | 1 |  WiFi signal [strength](https://developer.android.com/reference/android/net/wifi/WifiManager) (dBm) ||
| *carrier* | 1 | system organization name ||
| *mobileNetworkType* | 1 | mobile network type [info](https://developer.android.com/reference/androidx/work/NetworkType) ||
| *networkCountryIso* | 20 |  country name based on the [network](https://developer.android.com/reference/android/telephony/TelephonyManager) ||
| *simCountryIso* | 12 | country name based on the [sim](https://developer.android.com/reference/android/telephony/TelephonyManager) ||
| *roaming* | 1 | roaming status [info](https://developer.android.com/reference/android/net/NetworkInfo.html#isRoaming()) ||
| *phoneType* | 20 | phone [type](https://developer.android.com/reference/android/telephony/TelephonyManager) | 0: None, 1: GSM, 2: CDMA, 3: SIP |
| *airplane* | 20 | airplane mode status info ||
| *discoveryResult* | 1 | the request result which describe the type of the measured NAT | -3: DID NOT STARTED (since v20), -2: UNKNOWN (v1-19), -1: ERROR, 0: OPEN ACCESS, 1: FIREWALL BLOCKS, 2: SYMMETRIC UDP FIREWALL, 3: FULL CONE, 4: RESTRICTED CONE, 5: PORT RESTRICTED CONE, 6: SYMMETRIC ONE |
| *discoveryResultExitStatus* | 20 | the NAT measurement result code | -1: UNKNOWN, 0: END_SUCCESSFUL, 1: ERROR, 2: SOCKET EXCEPTION, 3: UNKNOWN HOST EXCEPTION, 4: MESSAGE ATTRIBUTE PARSING EXCEPTION, 5: MESSAGE HEADER PARSING EXCEPTION, 6: UTILITY EXCEPTION, 7: IO EXCEPTION, 8: MESSAGE ATTRIBUTE EXCEPTION, 9: NULL POINTER EXCEPTION |
| *publicIP* | 1 | hashed public IP address ||
| *STUNserver* | 20 | name of the STUN server which was used for the measurement ||
| *lastDiscovery* | 20 | UNIX timestamp of last NAT measurement ||
| *webRTCLocalTestConnectionStart* | 20 | UNIX timestamp of local test webRTC connection start  ||
| *webRTCLocalTestConnectionEnd* | 20 | UNIX timestamp of local test webRTC connection end ||
| *webRTCLocalTestConnectionEnd* | 20 | UNIX timestamp of local test webRTC connection end ||
| *webRTCLocalTestChannelOpen* | 20 | UNIX timestamp of local test webRTC channel open ||
| *webRTCLocalTestChannelClosed* | 20 | UNIX timestamp of local test webRTC channel closed ||
| *webRTCLocalTestExitStatus* | 20 | the local test webRTC measurement result codes | -10: UNKNOWN, -3: DID NOT STARTED, -2: CONNECTION TIMED OUT, 0: NOT CONNECTED TO ANY NETWORK, 2: CONNECTION LOST, 4: STUN SERVER ERROR, 10: P2P CHANNEL FAILED TO OPEN WITHOUT SRFLX, 11: P2P CHANNEL FAILED TO OPEN WITH SRFLX, 19: P2P CHANNEL OPEN BUT MESSAGE ERROR, 20: P2P CHANNEL OPEN AND EXCHANGE MESSAGES SUCCESSFUL |
| *lastDisconnect* | 20 | timestamp of the last connection lost||
| *chargingState* | 1 | battery charging state [info](https://developer.android.com/reference/android/os/BatteryManager) | 1: Unknwn, 2: Charging, 3: Discharging, 4: Not charging, 5: Full |
| *pluggedState* | 4 | battery plugged state [info](https://developer.android.com/reference/android/os/BatteryManager) | -1: Not pLugged or unknown, 1: AC, 2: USB, 4 WIRELESS |
| *percentage* | 1 | battery level [info](https://developer.android.com/reference/android/os/BatteryManager#EXTRA_LEVEL)  ||
| *health* | 1 | battery health [info](https://developer.android.com/reference/android/os/BatteryManager) ||
| *present* | 4 | present of battery - boolean | true if there is a battery otherwise false |
| *technology* | 4|  [type](https://developer.android.com/reference/android/os/BatteryManager#EXTRA_TECHNOLOGY) of battery of device ||
| *temperature* | 1 | the battery [temperature](https://developer.android.com/reference/android/os/BatteryManager#EXTRA_TEMPERATURE) during the measurement ||
| *voltage* | 1 | battery voltage [info](https://developer.android.com/reference/android/os/BatteryManager#EXTRA_VOLTAGE) ||
| *turnOnTimeStamp* | 11 | UNIX timestamp of the last boot. Before version 20, it was only appear once at boot ||
| *shutdownTimestamp* | 11 | UNIX timestamp of the last shut down. Before version 20, it was only appear once at shut down.  ||
| *uptime* | 11 |  [Elapsed](https://developer.android.com/reference/android/os/SystemClock#elapsedRealtime()) time since last turn on ||
| *latitude* | 1 | last known user required GPS location - latitude (hashed). Before version 20, it was the realtime GPS location [info](https://developer.android.com/training/location/display-address)   ||
| *longitude* | 1 | last known user required GPS location - longitude (hashed). Before version 20, it was the realtime GPS location [info](https://developer.android.com/training/location/display-address)  ||
| *locationCaptureTimestamp* | 20 | UNIX timestamp of GPS location info ||
| *countryName* | 1 | The name of the country where the data was recorded. It based on the IP address. ||
| *autonomousSystemOrganization* | 1 | The name of the system organization whose belongs to the IP address. ||
| *continent* | 1 | The name of the continent where the data was recorded. It based on the IP address. ||
| *platform* | 1 | The name of the device platform where the data was recorded ||
| *P2PdeviceID* | 21 |  unique device P2P ID (hashed) ||
| *P2PpeerID* | 21  | unique peer P2P ID (hashed)	||
| *P2PconnectionStart* | 21  | UNIX timestamp of local test webRTC connection start ||
| *P2PchannelOpen* | 21 | UNIX timestamp of local test webRTC channel open ||
| *P2PchannelClosed* | 21 | UNIX timestamp of local test webRTC channel closed ||
| *P2PconnectionEnd* | 21 | UNIX timestamp of local test webRTC connection end ||
| *P2PexitStatus* | 21 | the P2P measurement result codes  | -10: UNKNOWN, -3: DID NOT STARTED, -2: CONNECTION TIMED OUT, 0: NOT CONNECTED TO ANY NETWORK <br> 2: CONNECTION LOST, 3: PEER CONNECTION LOST, 4: STUN SERVER ERROR, 5: OFFER IS REJECTED <br> 10: P2P CHANNEL FAILED TO OPEN WITHOUT SRFLX, 11: P2P CHANNEL FAILED TO OPEN WITH SRFLX <br> 19: P2P CHANNEL OPEN BUT MESSAGE ERROR, 20: P2P CHANNEL OPEN AND EXCHANGE MESSAGES SUCCESSFUL |
| *P2PconnectionID* | 21 |  unique P2P connection ID  ||
| *P2Pinitiator* | 21  | P2P initiator (boolean) |  true if the device starts the connection |


## Vesions/releases

|   Versions  |    Releases   | 
| ------------|:-------------:|
| version 1.  | 2013.dec.20   |
| version 2.  | 2014.jan.6.   |
| version 3.  | 2014.jan.21.  |
| version 4.  | 2014.mar.14.  |
| version 5.  | 2014.mar.26.  |
| version 6.  | 2014.mar.28.  |
| version 7.  | 2014.mar.30.  |
| version 8.  | 2014.apr.10.  |
| version 9.  | 2014.apr.28.  |
| version 10. | 2014.okt.3.   |
| version 11. | 2014.okt.9.   |
| version 12. | 2015.jan.19.  |
| version 13. | 2015.marc.16. |
| version 14. | 2017.apr.25.  |
| version 15. | 2018.apr.18.  |
| version 16. | 2018.apr.21   |
| version 17. | 2018.apr.23.  |
| version 18. | 2018.may.12.  |
| version 19. | 2018.okt.29.  |
| version 20. | 2018.okt.29.  |
| version 21. | 2018.okt.31.  |
| version 22. | 2018.nov.26.  | 
| version 23. | 2018.dec.17.  |
| version 24. | 2019.jan.22.  |
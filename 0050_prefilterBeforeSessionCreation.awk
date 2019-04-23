#! /usr/bin/awk -f
BEGIN{
  FS=";"
  VERSIONS_SINCE_VERSION_2_IS_OK=23
  VERSIONS_SINCE_VERSION_2 = 20
  VERSIONS_SINCE_VERSION_1_IS_OK=9
  VERSIONS_SINCE_VERSION_1_IS_FAILED=15
  ANDROID_VERSION_SINCE_NO_BROADCAST=24
}
{
  if(FNR==1){
    split(FILENAME,filename,"/")
    file="out5/"filename[2]
  }  
  appversion=int($9)
  if (appversion >= VERSIONS_SINCE_VERSION_2_IS_OK && ( versionSupport == 0  || versionSupport == 2 ) ) {
    print($0) >> file
  } else if (appversion < VERSIONS_SINCE_VERSION_2 && ( versionSupport == 0  || versionSupport == 1 ) ) {
    appversion=int($38)
    androidversion=int($15)
    if ( appversion >= VERSIONS_SINCE_VERSION_1_IS_OK && appversion < VERSIONS_SINCE_VERSION_1_IS_FAILED && androidversion < ANDROID_VERSION_SINCE_NO_BROADCAST) {
      print($0) >> file
    }
  }  
}

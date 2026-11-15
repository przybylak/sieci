Scriptname F4SE Native Hidden
int Function GetVersion() global native
int Function GetVersionMinor() global native
int Function GetVersionBeta() global native
int Function GetVersionRelease() global native

; get a plugins version number, -1 if the plugin is not loaded
int Function GetPluginVersion(string name) global native

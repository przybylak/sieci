@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem ===========================================================================
rem  Has the Creation Kit generate the animation data (Meshes\AnimTextData)
rem  for CMB_RiderPose.esm. The game reads the riding clips' timing and root
rem  motion from there; without it the riding clips don't play.
rem
rem  Needs: "Fallout 4: Creation Kit" (Steam, Library > Tools), the riding
rem  clips in Data\Meshes\Actors\Character\Animations\MT\CMB_Rider and
rem  CMB_RiderPose.esm in Data (make_rider_pose.bat).
rem
rem  Mod Organizer 2: the Creation Kit must see MO2's virtual Data folder, so
rem  start this file from MO2 (see docs\ASSETS.md). The new files then land in
rem  MO2's "overwrite"; move them into the motorbike mod.
rem
rem  If Fallout 4 isn't found automatically:  set FO4=D:\Games\Fallout 4
rem ===========================================================================

if defined FO4 goto have_fo4
for /f "tokens=3,*" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4" /v "Installed Path" 2^>nul ^| find /i "Installed Path"') do set "FO4=%%B"
if defined FO4 goto have_fo4
set "FO4=C:\Program Files (x86)\Steam\steamapps\common\Fallout 4"
:have_fo4
if "!FO4:~-1!"=="\" set "FO4=!FO4:~0,-1!"
echo Fallout 4: !FO4!

if not exist "!FO4!\CreationKit.exe" (
  echo Can't find "!FO4!\CreationKit.exe". Install "Fallout 4: Creation Kit" from Steam.
  goto fail
)
if not exist "!FO4!\Data\CMB_RiderPose.esm" (
  echo CMB_RiderPose.esm isn't in "!FO4!\Data".
  echo Run make_rider_pose.bat and install it first. With Mod Organizer, start this file from MO2.
  goto fail
)
if not exist "!FO4!\Data\Meshes\Actors\Character\Animations\MT\CMB_Rider\walkforward.hkx" (
  echo The riding clips aren't in Data\Meshes\Actors\Character\Animations\MT\CMB_Rider.
  echo With Mod Organizer, start this file from MO2.
  goto fail
)

echo Generating animation data; the Creation Kit runs without a window and can take a few minutes...
pushd "!FO4!"
CreationKit.exe -GenerateAnimInfo:CMB_RiderPose.esm "!FO4!\Data" "!FO4!\Data"
set RESULT=!errorlevel!
popd
if not "!RESULT!"=="0" (
  echo The Creation Kit reported error !RESULT!.
  goto fail
)
if not exist "!FO4!\Data\Meshes\AnimTextData" (
  echo No Meshes\AnimTextData folder appeared.
  goto fail
)
echo.
echo Done: Data\Meshes\AnimTextData is up to date.
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong - please send the text above.
echo.
pause
exit /b 1

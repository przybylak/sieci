@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem ===========================================================================
rem  Builds CMB_RiderPose.esp and its AnimTextData (the seated riding
rem  animations) from YOUR game and load order. No Creation Kit needed.
rem
rem  Needs: Python 3 (python.org, tick "Add python.exe to PATH"), the riding
rem  clips installed (Meshes\Actors\Character\Animations\MT\CMB_Rider).
rem
rem  Mod Organizer 2:   make_rider_pose.bat "C:\Modding\MO2" [profile]
rem      Reads that profile's load order and mods, and writes a new mod,
rem      "Commonwealth Motorbike - Rider Pose", to enable in MO2.
rem  No mod manager:   make_rider_pose.bat
rem      Reads %LOCALAPPDATA%\Fallout4\plugins.txt and writes into Data.
rem
rem  Run it again after adding, removing or updating mods that add player
rem  animations (the Unofficial Fallout 4 Patch, for example).
rem  If Fallout 4 isn't found automatically:  set FO4=D:\Games\Fallout 4
rem ===========================================================================

set "HERE=%~dp0"

if defined FO4 goto have_fo4
for /f "tokens=3,*" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4" /v "Installed Path" 2^>nul ^| find /i "Installed Path"') do set "FO4=%%B"
if defined FO4 goto have_fo4
set "FO4=C:\Program Files (x86)\Steam\steamapps\common\Fallout 4"
:have_fo4
if "!FO4:~-1!"=="\" set "FO4=!FO4:~0,-1!"
echo Fallout 4: !FO4!
if not exist "!FO4!\Data\Fallout4.esm" (
  echo Can't find "!FO4!\Data\Fallout4.esm". Set FO4 to your game folder.
  goto fail
)

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo Python 3 not found. Install it from python.org ^(tick "Add python.exe to PATH"^).
  goto fail
)

set "MO2=%~1"
set "PROFILE=%~2"
if not defined PROFILE set "PROFILE=Default"
if defined MO2 (
  if "!MO2:~-1!"=="\" set "MO2=!MO2:~0,-1!"
  if not exist "!MO2!\profiles\!PROFILE!\modlist.txt" (
    echo No MO2 profile at "!MO2!\profiles\!PROFILE!". Check the folder and profile name.
    goto fail
  )
  set "OUT=!MO2!\mods\Commonwealth Motorbike - Rider Pose\CMB_RiderPose.esp"
  !PY! "!HERE!tools\rider\make_rider_plugin.py" --data "!FO4!\Data" --mo2 "!MO2!" --profile "!PROFILE!" --out "!OUT!"
) else (
  set "OUT=!FO4!\Data\CMB_RiderPose.esp"
  !PY! "!HERE!tools\rider\make_rider_plugin.py" --data "!FO4!\Data" --plugins-txt "%LOCALAPPDATA%\Fallout4\plugins.txt" --out "!OUT!"
)
if !errorlevel! neq 0 goto fail

echo.
if defined MO2 (
  echo Done. In MO2: refresh, enable the mod "Commonwealth Motorbike - Rider Pose" and the plugin CMB_RiderPose.esp.
) else (
  echo Done. Enable CMB_RiderPose.esp ^(in-game Mods menu or plugins.txt^).
)
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong - please send the text above.
echo.
pause
exit /b 1

@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem ===========================================================================
rem  Builds CMB_RiderPose.esm (the seated riding animations) from YOUR
rem  Fallout4.esm, into the Data folder next to this file.
rem
rem  Needs: Python 3 (python.org, "Add to PATH"). Nothing else.
rem  Afterwards run generate_anim_info.bat (through Mod Organizer if you use it).
rem
rem  If Fallout 4 isn't found automatically, run it as:
rem     set FO4=D:\Games\Fallout 4
rem     make_rider_pose.bat
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

!PY! "!HERE!tools\rider\make_rider_plugin.py" --fallout4 "!FO4!\Data\Fallout4.esm" --out "!HERE!Data\CMB_RiderPose.esm"
if !errorlevel! neq 0 goto fail

echo.
echo Next: install/copy the Data folder as usual, then run generate_anim_info.bat
echo ^(with Mod Organizer: run it through MO2, see docs\ASSETS.md^).
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong - please send the text above.
echo.
pause
exit /b 1

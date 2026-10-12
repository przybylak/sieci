@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem ===========================================================================
rem  Compiles the Commonwealth Motorbike scripts with the Creation Kit's own
rem  Papyrus compiler. Output goes to Data\Scripts\ next to this file.
rem
rem  Needs: Fallout 4 + "Fallout 4: Creation Kit" (free on Steam, Library > Tools).
rem  Optional: F4SE with its script sources, for the hotkey script.
rem
rem  If Fallout 4 isn't found automatically, run it as:
rem     set FO4=D:\Games\Fallout 4
rem     compile_scripts.bat
rem ===========================================================================

set "HERE=%~dp0"
set "SRC=%HERE%Data\Scripts\Source\User"
set "OUT=%HERE%Data\Scripts"

rem --- Find Fallout 4 -------------------------------------------------------
if defined FO4 goto have_fo4
rem The value name "Installed Path" contains a space, so the path is token 3 onward.
for /f "tokens=3,*" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4" /v "Installed Path" 2^>nul ^| find /i "Installed Path"') do set "FO4=%%B"
if defined FO4 goto have_fo4
set "FO4=C:\Program Files (x86)\Steam\steamapps\common\Fallout 4"
:have_fo4
if "!FO4:~-1!"=="\" set "FO4=!FO4:~0,-1!"
echo Fallout 4: !FO4!

set "COMPILER=!FO4!\Papyrus Compiler\PapyrusCompiler.exe"
set "BASE=!FO4!\Data\Scripts\Source\Base"
set "FLAGS=!BASE!\Institute_Papyrus_Flags.flg"
if not exist "!FLAGS!" if exist "!FO4!\Data\Scripts\Source\Institute_Papyrus_Flags.flg" set "FLAGS=!FO4!\Data\Scripts\Source\Institute_Papyrus_Flags.flg"

if not exist "!COMPILER!" (
  echo.
  echo Can't find the Papyrus compiler at:
  echo   !COMPILER!
  echo Install "Fallout 4: Creation Kit" from Steam ^(Library ^> Tools^), or set FO4 to your game folder.
  goto fail
)

rem --- Vanilla script sources ----------------------------------------------
if exist "!BASE!\Actor.psc" goto have_base
if not exist "!BASE!\Base.zip" (
  echo.
  echo Vanilla script sources not found in !BASE!
  echo Start the Creation Kit once, or reinstall it, so Base.zip appears there.
  goto fail
)
echo.
echo The vanilla script sources are still zipped ^(!BASE!\Base.zip^).
choice /m "Extract them now (needed once, the Creation Kit does the same)"
if errorlevel 2 goto fail
powershell -NoProfile -Command "Expand-Archive -LiteralPath '!BASE!\Base.zip' -DestinationPath '!BASE!' -Force"
if not exist "!BASE!\Actor.psc" (
  echo Extracting failed.
  goto fail
)
:have_base
if not exist "!FLAGS!" (
  echo.
  echo Can't find Institute_Papyrus_Flags.flg in !BASE!
  goto fail
)

rem --- Core scripts (vanilla API only) --------------------------------------
set FAILED=0
echo.
for %%S in (CMB_ControllerScript CMB_BikeActivatorScript CMB_KeysEffectScript CMB_SwimWatchEffectScript CMB_SideBagScript CMB_PlayerAliasScript) do (
  echo Compiling %%S...
  "!COMPILER!" "!SRC!\%%S.psc" -f="!FLAGS!" -i="!SRC!;!BASE!" -o="!OUT!"
  if !errorlevel! neq 0 (
    echo *** %%S FAILED ***
    set FAILED=1
  )
)

rem --- Optional F4SE scripts (need F4SE's script sources) --------------------
set "F4SE_SRC="
if exist "!FO4!\Data\Scripts\Source\F4SE\F4SE.psc" set "F4SE_SRC=!FO4!\Data\Scripts\Source\F4SE"
if exist "!FO4!\Data\Scripts\Source\User\F4SE.psc" set "F4SE_SRC=!FO4!\Data\Scripts\Source\User"
rem The "F4SE Scripts" mod puts them straight into Data\Scripts\Source (with MO2, run this from MO2).
if exist "!FO4!\Data\Scripts\Source\F4SE.psc" set "F4SE_SRC=!FO4!\Data\Scripts\Source"
if exist "!BASE!\F4SE.psc" set "F4SE_SRC=!BASE!"
echo.
if defined F4SE_SRC (
  for %%S in (CMB_HotkeyF4SE CMB_GearRestoreF4SE) do (
    echo Compiling %%S ^(F4SE sources: !F4SE_SRC!^)...
    "!COMPILER!" "!SRC!\%%S.psc" -f="!FLAGS!" -i="!F4SE_SRC!;!SRC!;!BASE!" -o="!OUT!"
    if !errorlevel! neq 0 (
      echo *** %%S FAILED - the mod still works without it ***
    )
  )
) else (
  echo F4SE script sources not found: skipping the optional F4SE scripts.
  echo The mod works without them - favorite the Motorbike Keys for a hotkey instead,
  echo and re-equip gear from slot 57 by hand after a ride.
)

echo.
if "!FAILED!"=="1" goto fail
echo All done. Compiled scripts are in:
echo   !OUT!
echo Next: copy the contents of the Data folder into "!FO4!\Data" ^(see README^).
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong - please send the text above.
echo.
pause
exit /b 1

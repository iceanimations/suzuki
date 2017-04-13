@echo off
setlocal
setlocal EnableDelayedExpansion
set /p user= Enter USER (PRESS ENTER FOR LOCALSYSTEM): 
if not "%user%"=="" (
    set /p phrase= Enter SECRET: 
)
if not "%user%"=="" (
    echo.
    echo python suzuki_service.py --username %user% --password %phrase% --startup auto install
    echo.
    python suzuki_service.py --username %user% --password %phrase% --startup auto install
)
if "%user%"=="" (
    echo.
    echo python suzuki_service.py --startup auto install
    echo.
    python suzuki_service.py --startup auto install
)
set ppath=%PYTHONPATH%
if not "%ppath%"=="" (
    set ppath=%ppath:;=/%
)
set curpath=%~dp0
echo %ppath%   %curpath%
REM if "x!ppath:%curpath%=!"=="x%ppath%" (
    echo setx /m PYTHONPATH %curPath%;%ppath%
    setx /m PYTHONPATH %curPath%;%ppath%
REM )

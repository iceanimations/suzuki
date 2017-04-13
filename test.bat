@echo off
setLocal EnableDelayedExpansion

set variable1=%1
set variable1=%variable1:;=/%
set variable2=%2

echo is %variable2% in %variable1%

if not "x!variable1:%variable2%=!"=="x%variable1%" (
    echo YES
) else (
    echo NO
)

endlocal

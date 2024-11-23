@echo off

:: 检查APP_PROFILE参数是否为空
if "%~1"=="" (
    echo 参数1为空，未设置环境变量。
) else (
    :: 将APP_PROFILE环境变量设为参数1的值
    set APP_PROFILE=%~1
    echo 已将APP_PROFILE环境变量设置为: %KK%
)

:: build.bat
call env\Scripts\activate
python build.py %1
deactivate
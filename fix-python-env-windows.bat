@echo off
chcp 65001 >nul
echo 🔧 修复虚拟环境 Python 版本...

:: 设置目标目录
set "TARGET_DIR=%USERPROFILE%\cursor-extensions\review-gate-v2"

:: 检查目录是否存在
if not exist "%TARGET_DIR%" (
    echo ❌ 目录不存在: %TARGET_DIR%
    echo 正在创建目录...
    mkdir "%TARGET_DIR%"
)

cd /d "%TARGET_DIR%"
echo 📁 当前工作目录: %TARGET_DIR%

:: 删除旧环境
echo 删除旧的虚拟环境...
if exist "venv" (
    rmdir /s /q "venv"
    echo ✅ 旧虚拟环境已删除
)

:: 找到正确的 Python
set "PYTHON_CMD="
for %%p in (python python3 py python.exe) do (
    %%p -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=%%p"
        for /f "tokens=*" %%v in ('%%p --version') do echo ✅ 找到合适的 Python: %%p ^(%%v^)
        goto :found_python
    )
)

:found_python
if "%PYTHON_CMD%"=="" (
    echo ❌ 找不到 Python 3.10+ 版本
    echo 请安装 Python 3.10 或更高版本: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 创建新环境
echo 创建新的虚拟环境...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo ❌ 创建虚拟环境失败
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 激活虚拟环境...
call "venv\Scripts\activate.bat"

:: 验证版本
for /f "tokens=*" %%v in ('python --version') do echo ✅ 新虚拟环境 Python 版本: %%v

:: 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip

:: 安装依赖
echo 安装 MCP 依赖...
pip install mcp

if errorlevel 1 (
    echo ❌ 安装依赖失败
    pause
    exit /b 1
) else (
    echo 🎉 修复完成！虚拟环境已准备就绪
    echo 💡 提示: 要激活此环境，请运行: venv\Scripts\activate.bat
)

:: 停用虚拟环境
call deactivate

echo.
echo 按任意键退出...
pause >nul 
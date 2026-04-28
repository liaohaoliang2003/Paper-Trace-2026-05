@echo off
set "PYTHON_EXE=C:\ProgramData\anaconda3\Python.exe"

if not exist "%PYTHON_EXE%" (
  echo Anaconda Python not found at %PYTHON_EXE%.
  echo Update scripts\paper_trace.cmd or install Anaconda base.
  exit /b 1
)

"%PYTHON_EXE%" -m paper_trace %*
exit /b %ERRORLEVEL%

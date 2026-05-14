@echo off
setlocal

if defined PAPER_TRACE_PYTHON (
  set "PYTHON_EXE=%PAPER_TRACE_PYTHON%"
) else (
  set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m paper_trace %*
set "EXIT_CODE=%ERRORLEVEL%"

if "%EXIT_CODE%"=="9009" (
  echo Could not run "%PYTHON_EXE%".
  echo Set PAPER_TRACE_PYTHON to your Python executable or ensure python is on PATH.
)

exit /b %EXIT_CODE%

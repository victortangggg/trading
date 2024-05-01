@echo off

rem Check if the correct number of arguments are provided
if "%~1" == "" (
    echo Usage: %0 python_script.py
    exit /b
)

rem Define the conda environment name
set conda_env=research

rem Activate the conda environment
call conda activate %conda_env%

rem Run the Python script with the provided argument
shift
python %1 %*

rem Deactivate the conda environment
call conda deactivate

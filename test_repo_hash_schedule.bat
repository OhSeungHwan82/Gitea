@echo off
set YEAR=%date:~0,4%
set MONTH=%date:~5,2%
set DAY=%date:~8,2%
set HOUR=%time:~0,2%
set MINUTE=%time:~3,2%
set SECOND=%time:~6,2%
set "log_filename=test_repo_hash_%YEAR%-%MONTH%-%DAY%_%HOUR%-%MINUTE%-%SECOND%.log"
C:/Users/incar/AppData/Local/Programs/Python/Python311/python.exe  D:\deploy\workspace\test_repo_hash.py >> ../logs/%log_filename%

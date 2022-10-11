# Turplanlegger
Python API for planning trips


## Testing
Run test:
```
pip install pytest
pytest tests/test_*.py`
```

Run test and save result:
```
pip install pytest pytest-csv
pytest tests/test_*.py --csv tests/test_result.csv --csv-columns utc_timestamp,id,module,name,file,status,message,duration
git commit tests/test_result.csv -m "Unitetest result"
```

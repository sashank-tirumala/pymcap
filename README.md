# PyMCAP
This provides a python interface to the go [MCAP cli tool](https://mcap.dev/guides/cli), so that you can merge mcaps and recover them conveniently from your python code

## Installation
```bash
pip install pymcap
```

## Quickstart
```python
from pymcap import PyMCAP
pymc = PyMCAP()
print(pymc.mcap_cli_version)
```

## Contributing
Add the ci tag to your branch to run the CI Tests

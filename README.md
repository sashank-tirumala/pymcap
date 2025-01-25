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

## Features
 - Python interface to MCAP CLI tools.
 - Bundles the MCAP cli with the python package, so you don't need to install the python package separately.

## Requirements
- Python 3.8+
- Operating system: Linux, macOS, or Windows, with arm64 or amd64 architectures.

## Testing
```bash
pytest tests
```

## Contributing
Add the ci tag to your branch to run the CI Tests

## License
MIT License

## Acknowledgements
Built on the official MCAP CLI tool: https://mcap.dev

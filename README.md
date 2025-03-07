# PyMCAP

This provides a Python interface to the Go [MCAP CLI tool](https://mcap.dev/guides/cli), so that you can merge MCAP files and recover corrupted ones conveniently from your Python code.

## Installation

```bash
pip install pymcap
```

## Quickstart

```python
from pathlib import Path
from pymcap import PyMCAP

# Initialize PyMCAP
pymc = PyMCAP()

# Get MCAP CLI version
print(pymc.mcap_cli_version)

# Check if an MCAP file is corrupted
is_corrupted = pymc.is_mcap_corrupted(Path("my_file.mcap"))
print(f"Is file corrupted: {is_corrupted}")

# Recover a corrupted MCAP file
result = pymc.recover(
    file=Path("corrupted.mcap"),
    out=Path("recovered.mcap"),  # Optional, default: file + "_recovered"
    inplace=True,  # Replace original file if True
)
print(f"Recovery successful: {result.success}")
print(f"Recovered file path: {result.output_file}")

# Merge multiple MCAP files
merged_result = pymc.merge(
    merge_files=[Path("file1.mcap"), Path("file2.mcap")],
    out=Path("merged.mcap")
)
print(f"Merge successful: {merged_result.success}")
print(f"Merged file path: {merged_result.output_file}")
```

## Features

- Python interface to MCAP CLI tools with a simple, intuitive API
- Automatically downloads and bundles the MCAP CLI with the Python package - no separate installation needed
- Corrupted MCAP file detection
- Recovery of corrupted MCAP files
- Merging of multiple MCAP files
- Cross-platform support (Linux, macOS, Windows)
- Support for both ARM64 and AMD64 architectures

## API Reference

### PyMCAP Class

```python
PyMCAP(log_level="INFO")
```

Initializes a new PyMCAP instance with specified logging level.

#### Properties

- `mcap_cli_version`: Returns the version of the MCAP CLI being used
- `version`: Returns the version of the PyMCAP package

#### Methods

##### is_mcap_corrupted

```python
is_mcap_corrupted(file: Path) -> bool
```

Checks if an MCAP file is corrupted.

- **Parameters:**
  - `file`: Path to the MCAP file to check
- **Returns:** True if the file is corrupted, False otherwise

##### recover

```python
recover(
    file: Path,
    out: Path | None = None,
    inplace: bool = True,
    flags: str = ""
) -> McapCLIOutput
```

Recovers a corrupted MCAP file.

- **Parameters:**
  - `file`: Path to the corrupted MCAP file
  - `out`: Output path for the recovered file (optional)
  - `inplace`: If True, replaces the original file with the recovered one
  - `flags`: Additional flags to pass to the MCAP CLI
- **Returns:** McapCLIOutput object containing the operation result

##### merge

```python
merge(
    merge_files: list[Path],
    out: Path,
    flags: str = ""
) -> McapCLIOutput
```

Merges multiple MCAP files into a single file.

- **Parameters:**
  - `merge_files`: List of paths to MCAP files to merge
  - `out`: Output path for the merged file
  - `flags`: Additional flags to pass to the MCAP CLI
- **Returns:** McapCLIOutput object containing the operation result

### McapCLIOutput Class

Represents the output of an MCAP CLI command.

#### Properties

- `stdout`: Standard output from the command
- `stderr`: Standard error from the command
- `output_file`: Path to the output file (if applicable)
- `success`: Boolean indicating whether the command succeeded

## Requirements

- Python 3.8+
- Operating system: Linux, macOS, or Windows
- Architecture: ARM64 or AMD64

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
 - Bundles the MCAP cli with the python package, so you don't need to install the MCAP CLI separately.

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

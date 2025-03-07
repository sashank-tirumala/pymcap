from __future__ import annotations

import logging
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests

logging.basicConfig(level=logging.INFO)


class McapCLIOutput:
    def __init__(
        self,
        stdout: str = "",
        stderr: str = "",
        output_file: Path = Path(""),
        success: bool = False,
    ) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.output_file = output_file
        self.success = success

    def __str__(self) -> str:
        return f"Output: {self.stdout}\nError: {self.stderr}\nOutput Path: {self.output_file}\nResult: {self.success}"

    def __getitem__(self, key: str) -> Any:
        if key == "stdout":
            return self.stdout
        elif key == "stderr":
            return self.stderr
        elif key == "output_file":
            return self.output_file
        elif key == "success":
            return self.success
        else:
            raise KeyError(f"Invalid key: {key}")


class PyMCAP:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger("PyMCAP")
        self.logger.setLevel(log_level)
        self.logger = logging.getLogger("PyMCAP")
        self.current_dir = Path(__file__).parent.resolve()
        self.pkg_dir = self.current_dir.parent.parent
        self.executable = self.__get_executable()
        self.__mcap_cli_version: str | None = None
        self.logger.debug(f"MCAP version: {self.mcap_cli_version}")
        self.logger.debug(f"MCAP executable: {self.executable}")

    @property
    def mcap_cli_version(self) -> str:
        if self.__mcap_cli_version is None:
            self.__mcap_cli_version = self.__run("version").stdout.strip("\n")
        return self.__mcap_cli_version

    @property
    def version(self) -> str:
        return "0.2"

    def __download_executable(self, executable_path: Path, executable_url: str) -> None:
        if executable_path.exists():
            pass
        else:
            try:
                self.logger.info("MCAP executable not found, downloading...")
                response = requests.get(executable_url)
                executable_path.parent.mkdir(parents=True, exist_ok=True)
                with open(executable_path, "wb") as f:
                    f.write(response.content)
                self.logger.info("MCAP executable downloaded successfully")
            except Exception as e:
                self.logger.error(f"Error downloading MCAP executable: {e}")
                sys.exit(1)
        result = subprocess.run(
            ["chmod", "+x", str(executable_path)], stdout=subprocess.PIPE
        )
        if result.returncode != 0:
            self.logger.error("Error setting executable permissions")
            sys.exit(1)

    def __get_executable(self) -> str:
        os = self.__get_os()
        self.logger.debug(f"OS: {os}")
        arch = self.__get_architecture()
        self.logger.debug(f"Architecture: {arch}")
        if os == "linux" and arch == "amd64":
            executable_path = self.current_dir / "binaries/linux_amd64/mcap.bin"
            executable_url = "https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.51/mcap-linux-amd64"
        elif os == "linux" and arch == "arm64":
            executable_path = self.current_dir / "binaries/darwin_amd64/mcap.bin"
            executable_url = "https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.51/mcap-linux-arm64"
        elif os == "darwin" and arch == "amd64":
            executable_path = self.current_dir / "binaries/darwin_amd64/mcap.bin"
            executable_url = "https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.51/mcap-macos-amd64"
        elif os == "darwin" and arch == "arm64":
            executable_path = self.current_dir / "binaries/darwin_arm64/mcap.bin"
            executable_url = "https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.51/mcap-macos-arm64"
        elif os == "windows" and arch == "amd64":
            executable_path = self.current_dir / "binaries/windows_amd64/mcap.bin"
            executable_url = "https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.51/mcap-windows-amd64.exe"
        else:
            raise ValueError(f"Unsupported OS: {os} and architecture: {arch}")

        self.logger.debug(f"Executable path: {executable_path}")
        self.logger.debug(f"Executable URL: {executable_url}")
        self.__download_executable(executable_path, executable_url)
        return str(executable_path.resolve())

    def __get_architecture(self) -> str:
        machine = platform.machine().lower()
        if machine in ("x86_64", "amd64"):
            return "amd64"
        elif machine in ("arm64", "aarch64"):
            return "arm64"
        else:
            raise ValueError(f"Unsupported architecture: {machine}")

    def __get_os(self) -> str:
        system = platform.system().lower()
        if system.startswith("linux"):
            return "linux"
        elif system.startswith("darwin"):
            return "darwin"
        elif system.startswith("windows"):
            return "windows"
        else:
            raise ValueError(f"Unsupported OS: {system}")

    def __run(self, command: str, flags: str = "") -> McapCLIOutput:
        final_command = self.executable + " " + command + flags
        self.logger.debug(f"Running command: {final_command}")
        result = subprocess.run(
            final_command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output_res = McapCLIOutput(
            stdout="", stderr="", output_file=Path(""), success=False
        )
        self.logger.debug(f"Command output: {result.stdout.decode('utf-8')}")
        if result.returncode != 0:
            output_res.stderr = result.stderr.decode("utf-8")
            output_res.success = False
            self.logger.error(f"Command failed: {result.stderr.decode('utf-8')}")
        else:
            output_res.stdout = result.stdout.decode("utf-8")
            output_res.success = True
        return output_res

    def run_command(
        self,
        command: str,
    ) -> McapCLIOutput:
        """
        Run a custom command on the mcap executable.
        Args:
            command (str): The command to run.
        Returns:
            McapCLIOutput: The output of the command.
        """
        return self.__run(command)

    def recover(
        self, file: Path, out: Path | None = None, inplace: bool = True, flags: str = ""
    ) -> McapCLIOutput:
        if out is None:
            out = file.parent / (str(file.stem) + "_recovered" + file.suffix)
        if file.suffix != ".mcap":
            raise ValueError("Can only recover .mcap files")
        if not self.is_mcap_corrupted(file):
            self.logger.debug("File is not corrupted, no need to recover")
            if inplace:
                return McapCLIOutput(output_file=file, success=True)
            else:
                with open(out, "wb") as f2:
                    f2.write(file.read_bytes())
                return McapCLIOutput(output_file=out, success=True)
        output = self.__run(f"recover {file} -o {out}", flags=flags)
        output_res = McapCLIOutput(
            stdout=output.stdout,
            stderr=output.stderr,
            success=output.success,
        )
        if output.success:
            if inplace:
                file.unlink()
                out.rename(file)
                output_res.output_file = file
            else:
                output_res.output_file = out
        else:
            out.unlink()
        return output_res

    def is_mcap_corrupted(self, file: Path) -> bool:
        output = self.__run(f"info {file}")
        if not output.success:
            return True
        else:
            return False

    def merge(
        self, merge_files: list[Path], out: Path, flags: str = ""
    ) -> McapCLIOutput:
        command = "merge "
        for merge_file in merge_files:
            if merge_file.suffix != ".mcap":
                raise ValueError("Can only merge .mcap files")
            self.recover(merge_file, inplace=True)
            command += f"{merge_file} "
        command += f"-o {out}"
        output = self.__run(command, flags=flags)
        return McapCLIOutput(
            stdout=output.stdout,
            stderr=output.stderr,
            output_file=out,
            success=output.success,
        )

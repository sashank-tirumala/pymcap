from __future__ import annotations

import logging
import platform
import subprocess
import sys
from pathlib import Path

import requests
import tomli

logging.basicConfig(level=logging.DEBUG)


class McapInstallError(Exception):
    pass


class McapCLIOutput:
    def __init__(self, output: str, result: bool):
        self.output = output
        self.result = result
        pass


class PyMCAP:
    def __init__(self, log_level: str = "INFO") -> None:
        self.logger = logging.getLogger("PyMCAP")
        self.logger.setLevel(log_level)
        self.logger = logging.getLogger("PyMCAP")
        self.current_dir = Path(__file__).parent.resolve()
        self.pkg_dir = self.current_dir.parent.parent
        self.executable = self.__get_executable()
        self.__mcap_cli_version: str | None = None
        self.__version: str | None = None
        self.logger.debug(f"MCAP version: {self.__version}")

    @property
    def mcap_cli_version(self) -> str:
        if self.__mcap_cli_version is None:
            self.__mcap_cli_version = self.__run("version").output.strip("\n")
        return self.__mcap_cli_version

    @property
    def version(self) -> str:
        if self.__version is None:
            with open((self.pkg_dir / "pyproject.toml"), "rb") as f:
                data = tomli.load(f)
            self.__version = data["project"]["version"]
        return self.__version

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

    def __run(self, command: str) -> McapCLIOutput:
        final_command = self.executable + " " + command
        self.logger.debug(f"Running command: {final_command}")
        result = subprocess.run(
            final_command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.logger.debug(f"Command output: {result.stdout.decode('utf-8')}")
        res_bool = True
        if result.returncode != 0:
            self.logger.error(f"Command failed: {result.stderr.decode('utf-8')}")
            res_bool = False
        return McapCLIOutput(result.stdout.decode("utf-8"), res_bool)

    def recover(
        self, file: Path, out: Path | None = None, inplace: bool = True
    ) -> Path | None:
        if out is None:
            out = file.parent / (str(file.stem) + "_recovered" + file.suffix)
        if file.suffix != ".mcap":
            raise ValueError("Can only recover .mcap files")
        if not self.is_mcap_corrupted(file):
            self.logger.debug("File is not corrupted, no need to recover")
            if inplace:
                return file
            else:
                with open(out, "wb") as f2:
                    f2.write(file.read_bytes())
                return out
        output = self.__run(f"recover {file} -o {out}")
        if output.result:
            if inplace:
                file.unlink()
                out.rename(file)
        else:
            out.unlink()
            out = None
        return out

    def is_mcap_corrupted(self, file: Path) -> bool:
        output = self.__run(f"info {file}")
        if not output.result:
            return True
        else:
            return "Failed" in output.output

    # def is_mcap_corrupted(file_path: str) -> bool:
    #     try:
    #         output = subprocess.check_output(
    #             f"/usr/local/bin/mcap info {file_path}", shell=True, stderr=subprocess.STDOUT, text=True
    #         )
    #         return "Failed" in output
    #     except subprocess.CalledProcessError as e:
    #         if e.returncode == 127:
    #             raise McapInstallError
    #         return "Failed" in e.output


if __name__ == "__main__":
    p = PyMCAP(log_level="DEBUG")
    print(p.mcap_cli_version)
    print(p.version)
    print(p.mcap_cli_version)
    print(p.version)

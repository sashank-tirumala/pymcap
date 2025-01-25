import logging
import platform
import subprocess
import sys
from pathlib import Path

import requests
import tomli

logging.basicConfig(level=logging.DEBUG)


class PyMCAP:
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger("PyMCAP")
        self.logger.setLevel(log_level)
        self.logger = logging.getLogger("PyMCAP")
        self.current_dir = Path(__file__).parent
        self.executable = self.get_executable()
        self.__version = subprocess.run(
            [self.executable, "version"], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        self.logger.debug(f"MCAP version: {self.__version}")

    @property
    def mcap_cli_version(self):
        return self.__version

    @property
    def version(self):
        with open("pyproject.toml", "rb") as f:
            data = tomli.load(f)
        return data["project"]["version"]

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

    def get_executable(self) -> str:
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


if __name__ == "__main__":
    p = PyMCAP()
    print(p.version)

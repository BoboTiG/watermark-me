# Usage: powershell ".\packaging\windows\deploy.ps1" [ARG]
#
# Possible ARG:
#     -build: build the installer
#     -check_upgrade: check the auto-update works
#     -install: install all dependencies
#     -start: start the application
#     -tests: launch the tests suite
#
# Source: https://github.com/nuxeo/nuxeo-drive/blob/master/tools/windows/deploy_jenkins_slave.ps1
#
param (
	[switch]$build = $false,
	[switch]$check_upgrade = $false,
	[switch]$install = $false,
	[switch]$start = $false,
	[switch]$tests = $false
)

# Stop the execution on the first error
$ErrorActionPreference = "Stop"

# Global variables
$global:PYTHON_OPT = "-Xutf8", "-E", "-s"
$global:PIP_OPT = "-m", "pip", "install", "--upgrade", "--upgrade-strategy=only-if-needed"


function add_missing_ddls {
	# Missing DLLS for Windows 7
	$folder = "C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x86\"
	if (Test-Path $folder) {
		Get-ChildItem $folder | Copy -Verbose -Force -Destination "dist\$Env:APP_NAME_DIST"
	}
}

function build($app_real_version, $script) {
	# Build an executable
	Write-Output ">>> [$app_real_version] Building $script"
	if (-Not (Test-Path "$Env:ISCC_PATH")) {
		Write-Output ">>> ISCC does not exist: $Env:ISCC_PATH. Aborting."
		ExitWithCode 1
	}

	# Remove the beta notation
	$app_version = $app_real_version.split("b")[0]

	& $Env:ISCC_PATH\iscc /DMyAppVersion="$app_version" /DMyAppVersion="$app_version" /DMyAppRealVersion="$app_real_version" "$script"
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
}

function build_installer {
	# Build the installer
	$app_version = (Get-Content $Env:APP_NAME_DIST\__init__.py) -match "__version__" -replace '"', "" -replace "__version__ = ", ""

	Write-Output ">>> [$app_version] Freezing the application"
	freeze_pyinstaller

	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT packaging\scripts\cleanup_application_tree.py "dist\$Env:APP_NAME_DIST"
	add_missing_ddls

	# Stop now if we only want the application to be frozen (for integration tests)
	if ($Env:FREEZE_ONLY) {
		return 0
	}

	build "$app_version" "packaging\windows\setup.iss"
}

function check_import($import) {
	# Check module import to know if it must be installed
	# i.e: check_import "from PyQt4 import QtWebKit"
	#  or: check_import "import cx_Freeze"
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -c $import
	if ($lastExitCode -eq 0) {
		return 1
	}
	return 0
}

function check_upgrade {
	# Ensure a new version can be released by checking the auto-update process.
    & $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT packaging\scripts\check_update_process.py
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
}


function check_vars {
	# Check required variables
	if (-Not ($Env:PYTHON_VERSION)) {
		$Env:PYTHON_VERSION = '3.8.3'  # XXX_PYTHON
	} elseif (-Not ($Env:WORKSPACE)) {
		Write-Output ">>> WORKSPACE not defined. Aborting."
		ExitWithCode 1
	}
	if (-Not ($Env:ISCC_PATH)) {
		$Env:ISCC_PATH = "C:\Program Files (x86)\Inno Setup 6"  # XXX_INNO_SETUP
	}
	if (-Not ($Env:PYTHON_DIR)) {
		$ver_major, $ver_minor = $Env:PYTHON_VERSION.split('.')[0,1]
		$Env:PYTHON_DIR = "C:\Python$ver_major$ver_minor-32"
	}

	$Env:STORAGE_DIR = (New-Item -ItemType Directory -Force -Path "$($Env:WORKSPACE)\..\deploy-dir\$Env:PYTHON_VERSION").FullName

	Write-Output "    PYTHON_VERSION = $Env:PYTHON_VERSION"
	Write-Output "    WORKSPACE      = $Env:WORKSPACE"
	Write-Output "    STORAGE_DIR    = $Env:STORAGE_DIR"
	Write-Output "    PYTHON_DIR     = $Env:PYTHON_DIR"
	Write-Output "    ISCC_PATH      = $Env:ISCC_PATH"
}

function ExitWithCode($retCode) {
	$host.SetShouldExit($retCode)
	exit
}

function freeze_pyinstaller() {
	# Note: -OO option cannot be set with PyInstaller
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -m PyInstaller "$Env:REPOSITORY_NAME.spec" --noconfirm

	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
}

function install_deps {
	if (-Not (check_import "import pip")) {
		Write-Output ">>> Installing pip"
		# https://github.com/python/cpython/blob/master/Tools/msi/pip/pip.wxs#L28
		& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -OO -m ensurepip -U --default-pip
		if ($lastExitCode -ne 0) {
			ExitWithCode $lastExitCode
		}
	}

	Write-Output ">>> Installing requirements"
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -OO $global:PIP_OPT pip
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -OO $global:PIP_OPT -r requirements.txt
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -OO $global:PIP_OPT -r requirements-dev.txt
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
}

function install_python {
	if (Test-Path "$Env:STORAGE_DIR\Scripts\activate.bat") {
		& $Env:STORAGE_DIR\Scripts\activate.bat
		if ($lastExitCode -ne 0) {
			ExitWithCode $lastExitCode
		}
		return
	}

	Write-Output ">>> Setting-up the Python virtual environment"

	& $Env:PYTHON_DIR\python.exe $global:PYTHON_OPT -OO -m venv --copies "$Env:STORAGE_DIR"
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}

	& $Env:STORAGE_DIR\Scripts\activate.bat
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
}

function launch_tests {
	# Launch tests
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -OO $global:PIP_OPT tox
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -m tox
	if ($lastExitCode -ne 0) {
		ExitWithCode $lastExitCode
	}
}

function start_app {
	# Start the application
	$Env:PYTHONPATH = "$Env:WORKSPACE"
	& $Env:STORAGE_DIR\Scripts\python.exe $global:PYTHON_OPT -OO -m $Env:REPOSITORY_NAME
}

function main {
	# Launch operations
	check_vars
	install_python

	if ($build) {
		build_installer
	} elseif ($check_upgrade) {
		check_upgrade
	} elseif ($install) {
		install_deps
		if ((check_import "import PyQt5") -ne 1) {
			Write-Output ">>> No PyQt5. Installation failed."
			ExitWithCode 1
		}
	} elseif ($start) {
		start_app
	} elseif ($tests) {
		launch_tests
	}
}

main

# Scripts

Utility scripts for running and managing the application.

## Windows Scripts

- `RUN_ME.bat` - Main launcher (recommended)
- `start.bat` - Start the server
- `start_server.bat` - Alternative start script
- `setup.ps1` - PowerShell setup script

## Linux/Mac Scripts

- `setup.sh` - Bash setup script

## Usage

### Windows
```bash
# First time setup
.\scripts\setup.ps1

# Run the application
.\scripts\RUN_ME.bat
```

### Linux/Mac
```bash
# First time setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# Run the application
cd backend
python main.py
```

## Notes

All scripts should be run from the project root directory.

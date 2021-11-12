# Setup
1. create venv `python -m venv .venv`
2. open command line terminal
3. activate venv with `.venv/Sripts/Activate.bat`
4. install requirents with `pip install -r requirements.txt`
5. In VS Code, select interpreter from ".venv"
6. (with admin privileges) execute in command line `powershell Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` to get rid of permission warnings when running Activate.ps1

# Credits
HDLC implementation is based on https://github.com/wuttem/simple-hdlc

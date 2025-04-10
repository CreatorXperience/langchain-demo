isActivateFilePath="$(find . -type f -name "activate")"
if [[ $isActivateFilePath ]]; then
    echo "python3 virtual env environment found\n"
else
    python3 -m venv .venv
fi;


echo "run:\n\n"source ./.venv/bin/activate" then \npip install -qU  -r requirements.txt\n\nto start the virtual env and install project dependencies"

python3 ./src/chatbot.py
# Holocron

Holocron is a Python testing playground for generating bot responses. If offers tooling to experiment with memory creation/recall, prompt construction, and inference strategies.

## Setup

1. Create a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install the required packages:
    ```sh
    pip3 install -r requirements.txt
    xargs brew install < my_brew.txt
    ```
Note: if you don't have brew installed, run 
```
xcode-select --install
```

3. Add API keys
    Create a `config.ini` file at the root level with the following content:
    ```ini
    [Api]
    OPENAI_API_KEY = sk-<your-key>
    ```

### Run from command line

1. Run `python scripts/chat/test.py` to start a conversation between bots

### Run with VSCode

1. Switch to the virtual environment kernel (use the button on the top right)
2. Install `ipykernel` if prompted
4. Open and execute the available iPython notebook (e.g., scripts/chat/ipython_notbooks/test.ipynb)

### Set up memory

To run the text pipeline against a memory context you will need to set up a postgres instance with pg_vector. To do that, run the script `scripts/create_db.sh`. If you ever need to clear the database, run the script `scripts/delete_db.sh`. 

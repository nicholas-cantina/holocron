# Holocron

Holocron is a Python testing playground for generating bot responses and exploring hallucinated memories.

## Setup

Follow these steps to set up the project:

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

3. Add keys
    Create a `config.ini` file with the following content:
    ```ini
    [OPENAI]
    OPENAI_API_KEY = sk-<your-key>
    ```

### Debug in VSCode

1. Switch to the virtual environment kernel (use the button on the top right)
2. Install `ipykernel` if prompted
4. Open and execute the available iPython notebook (e.g., scripts/ipython_notbooks/test.ipynb)

## Updating the Virtual Environment

To update the list of dependencies, run:
```sh
pipreqs . --force
pip freeze > requirements.txt
```
```sh
brew leaves > my_brews.txt
```

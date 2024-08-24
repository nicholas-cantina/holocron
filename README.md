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

To update the list of dependencies, run:
```sh
pipreqs . --force
pip freeze > requirements.txt
```
```sh
brew leaves > my_brews.txt
```


### Debug in VSCode

1. Switch to the virtual environment kernel (use the button on the top right)
2. Install `ipykernel` if prompted
4. Open and execute the available iPython notebook (e.g., scripts/ipython_notbooks/test.ipynb)

## What's available

### Questions/answer

One way to improve a bot's uniqueness and depth is give it the opportuntity to hallucinate new information that becomes cannon going forward. We can accomplish that by asking the bot questions and store answers for future retrieval.

### Action history

The message history is a project of who/what a bot is an the messages that precede it. This is a little one dimensional compared to how humans communicate in that it disregards that bots do things beyond the chat they're having in the room. We can emulate that by mantaining a "action history" that describes, in real time, what a bot is doing. That way, when it messages, it can be consistent with an inner/outer life, giving it more information to user when creating a response.



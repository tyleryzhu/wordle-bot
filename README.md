# Wordle Bot

<p align="center">
  <img src="wordlebot.png"/>
</p>

Discord Bot for playing wordle. You can either add my bot (which will be generally running 24/7 outside of bug fixes) or add your own. Here is a quick trailer of two people demonstrating the battle functionality.

https://user-images.githubusercontent.com/22010655/149846021-cacd2e34-6921-463b-a7a3-732ee62e574d.mov

You can find the full demo [here](https://youtu.be/zLEQyjqtegk). If you have questions/bugs, shoot me a message on discord at tzhu#3585. 

## How to play

Wordle utilizes slash commands in discord to function. There are a few commands that you can use to play wordle.

* `/start`: Begins a Wordle game for the server in one of three modes:
  * `collab`, where you work together on a Wordle game
  * `custom`, where one person can provide a custom word for others to guess
  * `battle`, a multiplayer mode where multiple people compete on the same world at once.
* `/guess`: Make a guess for Wordle. Words must be real words.  
* `/letters`: Get a list of letters that you haven't guessed yet or are in the word.
* `/review`: Get a list of all your previous guesses.
* `/end`: Ends the game regardless of where it is at.

Battle Mode Specific Commands:

* `/join`: Joins an open battle party. Hosts do not need this, as they are automatically in the party.
* `/leave`: Leaves the currently joined battle party. Hosts cannot use this. 
* `/ready`: Ready up for the battle, closing the party and starting the game.

## Using my wordle bot (easy)

To add my bot, you can add it to your own discord server using [this link](https://discord.com/api/oauth2/authorize?client_id=928178745209155625&permissions=274878237696&scope=bot). It's running on a server 24/7 and periodically will be reset in case things break. Please file bug reports so I can fix them!

One thing to note is that the owner of the server will always see all private channels (this is a discord feature unfortunately), so this means the owner of the server should mute all notifications from the server temporarily to prevent guessees from being spoiled. 

## Setting up your own bot on discord 

You can also set up your own bot to run this script by creating a discord application and running this script with your bot token. Follow these steps for that:

1. Follow the steps [here](https://docs.pycord.dev/en/master/discord.html) to create your own bot. 
2. Grab your token from the discord application page and store it in a file called ```settings.py``` (mine is untracaked). For your own purposes, your file should look like this. 
  ```python
  MYTOKEN = ...
  ```
3. Clone this repo and setup with 
  ```bash
  git clone git@github.com:tyleryzhu/wordle-bot.git
  cd wordle-bot 
  conda env create -f env.yml 
  conda activate disc
  python run_bot.py
  ```

Note to use the following to install the correct version of pycord. 

```bash
pip install py-cord-2.0.0a4758+g1b17e831
```

## Future Features (currently on pause)
* Statistics and tracking. Keep track of how well you do on average, and how many games you've played.
* Hints. When stuck, the bot will remove some of the letters that aren't in the final word for you. 

## Version History

* **v0.4**:_(01/16/22)_ Finish fixing battle mode and other bugs, make it so private channels are shared afterwards with people. 
* **v0.3.1**:_(01/10/22)_ Added battle mode, multiplayer mode to play all at once with friends. 
* **v0.3**:_(01/08/22)_ Rewrite of the bot to use py-cord instead, replacing with slash commands. Also added custom game functionality to suggest your own word to play with.
* **v0.2**:_(01/07/22)_ Add commands for getting all past guesses, for tracking which letters are still left, and for restarting games. Add multi-server support.
* **v0.1**:_(01/06/22)_ Initial release. Basic functionality with text commands.

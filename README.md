# wordle-bot
Discord Bot for playing wordle and other word games.

I'm storing my bot token in an untracked file ```settings.py```, as well as a quick one-liner to get a list of words.

Use the following to install py-cord correctly. 

```bash
pip install py-cord-2.0.0a4758+g1b17e831
```

## Future Features
* Battle mode! Play with a bunch of friends and see who gets the best score. 
* Statistics and tracking. Keep track of how well you do on average, and how many games you've played.
* Hints. When stuck, the bot will remove some of the letters that aren't in the final word for you. 

## Version History

* **v0.3**:_(01/08/22)_ Rewrite of the bot to use py-cord instead, replacing with slash commands. Also added custom game functionality to suggest your own word to play with.
* **v0.2**:_(01/07/22)_ Add commands for getting all past guesses, for tracking which letters are still left, and for restarting games. Add multi-server support.
* **v0.1**:_(01/06/22)_ Initial release. Basic functionality with text commands.
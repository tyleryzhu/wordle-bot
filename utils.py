with open("words.txt", "r") as f:
    GAME_WORDS = [word.strip().upper() for word in f.readlines()]

with open("sgb-words.txt", "r") as f:
    WORDLEBANK = [word.strip().upper() for word in f.readlines()]

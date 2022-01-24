with open("wordle-answers-alphabetical.txt", "r") as f:
    GAME_WORDS = [word.strip().upper() for word in f.readlines()]

with open("sgb-words.txt", "r") as f:
    WORDLEBANK = list(set([word.strip().upper() for word in f.readlines()]))

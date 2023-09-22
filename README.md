# Tetris Game Assignment

## Overview

This is a simple Tetris game developed for educational purposes. Built with [Python](https://www.python.org/) and [Pygame](https://www.pygame.org/), it demonstrates basic game development techniques and design patterns. The game includes basic Tetris functionalities like line clearing, shape rotations, and more.


## Prerequisites

- python-i18n==0.3.9
- pygame==2.5.1
- pygame-ce==2.3.1
- pygame-gui==0.6.9

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/Nishko/tetrisGit.git
    ```

2. Navigate to the cloned directory:

    ```bash
    cd tetrisGit
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Game

Run `main.py` to start the game:

```bash
python main.py
```

## Code Description

### Naming Convention

The naming conventions of the code are; my_variable, myMethod, and MyClass.

### Line Counts

The line counts of the files are; main.py, 454 lines. gameScreen.py, 352 lines. tetrisObjects.py, 189 lines. theme.json, 58 lines. The total line count of all files are 1053 lines.

### Source Code Description

There are four code files of this project, theme.json, main.py, gameScreen.py, and tetrisObjects.py.

theme.json contains the colours, fonts, and sizes of the gui in the game project.

main.py runs the display and interactions of all the screens apart from the game screen and the pause screen. It also keeps track of high scores and game settings.

gameScreen.py runs the display and interactions of the game screen and runs the inputs and outputs behind the game of Tetris including both human playing mode and AI mode, the logic for deciding the AI's moves, and the display and interactions of the pause screen.

tetrisObjects.py runs the logic behind the Tetris game including the board, the active piece, and the line clearing.playing mode and AI mode. It also runs the display and interactions of the pause screen.

# Spades

A modern implementation of the trick-taking card game **Spades**, built with Python and Pygame. This version features smooth animations, AI opponents with names, and a "Green Felt" casino aesthetic.

## Features

* **Smooth Animations:** Fluid card movements using cubic easing and bounce effects.
* **Dynamic Visuals:** High-fidelity card rendering with shadows, hover scales, and "pop-up" playable card hints.
* **Intelligent AI:** Smart bidding and card-playing logic for three computer-controlled opponents.
* **Full Game Rules:** * Bidding phase (1-7 tricks).
* Spades as trump cards.
* Bagging system (10 bags = -100 points).
* Team-based scoring (First to 500 points wins).
* **Customizable Experience:** Randomize opponent names and enjoy an interactive menu system.

## Installation

### Prerequisites

Ensure you have **Python 3.7+** installed on your system. You will also need the `pygame` library.

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Igriscodes/spades.git
cd spades
```


2. **Install dependencies:**
```bash
pip install pygame
```


3. **Run the game:**
```bash
python app.py
```

## How to Play

### The Basics

* **Bidding:** At the start of each round, look at your hand and bid how many tricks you think you can win. Your team must reach the combined bid to earn positive points.
* **Playing:** You must follow the lead suit if possible. If you cannot, you may play any other suit, including Spades (the trump suit).
* **Winning a Trick:** The highest card of the lead suit wins, unless a Spade is played, in which case the highest Spade wins.

### Controls

* **Mouse Move:** Hover over cards in your hand to see them enlarge.
* **Left Click:** * Select your bid from the UI buttons.
* Click a "highlighted" card to play it during your turn.
* Click on AI names in the setup screen to randomize them.

## Game Mechanics

| Feature | Description |
| --- | --- |
| **Trump Suit** | Spades are always the highest suit. |
| **Breaking Spades** | You cannot lead with a Spade until a Spade has been played on a previous trick (unless you only have Spades). |
| **Bags** | Every trick won over your bid counts as a "bag." Accumulating 10 bags results in a 100-point penalty. |
| **Winning Score** | The first team to reach **500 points** is declared the winner. |

## Project Structure

```text
spades/
│
├── app.py              # Main game logic and Pygame loop
└── README.md           # Project documentation
```

## Credits

Developed by [Igriscodes](https://github.com/Igriscodes). Built using the Pygame framework.

## License
[GNU Lesser General Public License v2.1](LICENSE) - Feel free to use and modify

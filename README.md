# Cliffhanger

Cliffhanger is a party game designe around tracking your blood alcohol content (BAC) with your friends. You need a breathylizer to play. It should be run on a computer in your local network and that computer's IP address should be used by all the players.

## Setup

First, clone the repository:

```
git clone https://github.com/kevroy314/cliffhanger`
cd cliffhanger
```

Then create a conda environment (download conda [here](https://www.anaconda.com/)).

```
conda create -n cliffhanger python==3.9 --yes
conda activate cliffhanger
```

Install the dependencies:

```
pip install -r requirements.txt
```

Start the app server:

```
python index.py
```
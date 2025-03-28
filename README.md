# Vinted Scraper Bot

This bot scrapes Vinted listings and sends notifications to a specified Discord channel whenever new items that match the provided links are found.

## Features

- Scrapes Vinted for new items based on URLs.
- Sends an embed message to a specified Discord channel with item details such as price, name, and image.
- Allows users to add new Vinted URLs and channels through a command.
- Customizable to fit different search criteria for multiple URLs.

## Requirements

- Python 3.8+
- Libraries:
  - `discord.py`
  - `selenium`
  - `dotenv`
  - `json`
  - `chromedriver` (make sure it matches your Chrome version)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/SamSammm78/SMBOT-VINTED
   cd SMBOT-VINTED
   pip install -r requirements.txt

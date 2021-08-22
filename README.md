# Chia Tea 🌱🍵

Chia Tea is a tools and utility library for the Chia Cryptocurrency.
We are building tools in this library to serve our own needs and share our work openly with others.
Feel free to use them and make your life easier 💚

# Table of Contents

- [Intro and FAQ](docs/faq.md)
- [Quick-Start](docs/quick_start.md)
- [Architecture Summary](docs/architecture_summary.md)
- [Structure of this repository](#structure-of-this-repository)
- [Feature Overview](#feature-overview)
  - [Copy Tool](#copy-tool)
  - [Monitoring](#monitoring)
  - [Discord Bot](#discord-bot)
- [Contributions](#contributions)
- [About Us](#about-us)
- [✊ Support Us ✊](#support-us)

## Structure of this repository

![Chia-Tea Infrastructure](docs/Chia_Infrastructure.png?raw=true)

## Feature Overview

### Copy Tool

Copy is a tool to copy your chia files to a different location. It can be faster to plot to a temporary storage space and then move the plots to your harvester afterwards to not block the plotting queue. We manage this process through our copy cli tool. It incorporates the following features:

- Selects a drive with sufficient space from multiple disks specified
- Checks drive space regularly
- Takes plots which are being copied already into account
- Uses the drive with the fewest copy processes
- Logs transfer times

### Monitoring

The monitoring tracks everything relevant to a Chia farm, including harvesters, farmers, plotters, etc. It consists of a server and multiple clients. The server is run on only one machine. It stores all the monitoring data in a sqlite database. The clients are the data collectors and are typically run on plotters, harvesters, farmers, etc. Simply start them on the same machine and they will collect data automatically. You can run both server and client on the same machine if you have a single machine setup.

### Discord Bot

The discord module is a bot watching a farm and reports major incidents. Internally the bot keeps an eye on the sqlite database thus a running monitoring server is required. Besides notifications the bot also provides commands to interact with the chia farm.

<a name="about-us"></a>

## About Us

We are a small group of professional engineers and software developers doing Chia for fun. Join our discord server: https://discord.gg/azNjcVPYnY for questions, tips and tricks or just come over for a nice warm cup of your favourite tea.

<a name="security"></a>

## Contributions

Due to security concerns, we only accept small PR's with limited complexity to our codebase.

<a name="support-us"></a>

## ✊ Support Us ✊

The more you support us, the easier we can make your life as a Chia farmer. Every little bit helps and motivates us to do more.

| Currency | Address                                                                                                 |
| -------- | ------------------------------------------------------------------------------------------------------- |
| Chia     | xch13yrhjp0zleepsafjh8syh0jyakjgat9fzlut575lq0z5jywmydeqy05awj                                          |
| BTC      | bc1qwjyh0fu708zv0yqdmp098tq465qy64jpmqpj4y                                                              |
| ETH      | 0xeeaA95F8816208b4bb8D070ab571941843246029                                                              |
| ADA      | addr1qxc2amr663yfh9z4cdk8d6hkv9apvm35dm5lkgjdlu6ffkfggrvustlynuxzqmswee4mvd6cfeu66hq788rmgts2uggq7qtuqh |

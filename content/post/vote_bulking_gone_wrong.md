---
title: "One Man Army: How I Built a Bot to Dominate Ngoi Sao Xanh 2025"
author: clgp
date: "2025-12-12T01:06:11+07:00"
categories:
  - Tool
  - Automation
tags:
  - Python
  - PyAutoGUI
---

[**View THIS PROJECT ON GitHub**](https://github.com/iluvmOne-Y/Boosting_Lan_Song_Xanh2025)

![Status](https://img.shields.io/badge/Status-Not_Working-red)

## 🎯 The Mission

So, **Ngoi Sao Xanh 2025** is happening. For those who don't know, it's a major voting competition where fans vote for their favorite actors.

Here is the rule:

> **1 Verified Account = 1 Free Vote per Day (worth 5 points).**

Most people saw a voting form. I saw a challenge. And since I really wanted my favorite actor to take the top spot (don't judge my dedication), I needed more than just _my_ vote. I needed an army.

---

## ⚡ The Exploit: "The Infinite Email Glitch"

In the first three days of voting, I noticed something interesting: The website allowed registration with **any** email address, not just Gmail. You just needed to verify it.

My brain immediately went into **"Efficiency Mode."**

I briefly considered hosting my own private SMTP server, but then I realized... why reinvent the wheel? There are plenty of free temp-mail services online.

I discovered a sweet spot:

1.  One temp-mail domain (e.g., `@tempmail.com`) could be used to receive verification codes for about **10 different accounts** before it stopped working.
2.  I just needed to rinse and repeat.

### 🛠️ The Grind

For **2.5 days**, I went into manual overdrive. I managed to create **700 verified accounts**. Yes, 700. My fingers hurt, but the points were calling.

---

## 🤖 The Tool: "Why click when Python can click for you?"

Okay, creating accounts was manual pain, but _voting_ with them? No way was I logging in and out 700 times a day by hand.

**The Logic:**
`Login` ➡️ `Vote` ➡️ `Logout` ➡️ `Repeat`

I thought about the usual web scraping suspects: _Selenium_, _Puppeteer_, _Playwright_. But honestly? They were overkill. Dealing with complex DOM elements, hidden API tokens, and potential anti-bot detection on the backend seemed like a headache.

So I chose the lazy genius solution: **PyAutoGUI**.

Instead of bypassing the server, I just became a normal user with machine speed =)).
`PyAutoGUI` is a Python library that literally takes control of your mouse and keyboard. It doesn't care about HTML elements or APIs; it just clicks where I tell it to click.

I wrote a script to simulate _me_ sitting at the computer.

### 📍 Phase 1: Mapping

The first step was defining exactly where every button lived on my screen. The function `displayMousePosition()` was my best friend here. I used it to hunt down the `X` and `Y` coordinates for the **"Login"**, **"Vote"**, and **"Logout"** buttons.

Once mapped, I just needed some simple commands to spam the actions:

- `click()`: To smash the vote button.
- `press()` & `hotkey()`: To handle typing and tab navigation.

### 👁️ Phase 2: Giving the Bot "Eyes"

Clicking blindly at coordinates works... until it doesn't. What if an error pops up?

That is where the `locateOnScreen()` function comes in. It uses **OpenCV** (computer vision) to actually scan the screen for specific images.

**The Strategy:**
Sometimes, I would log into an account that I forgot to verify. A dumb bot would keep trying to vote and crash. My bot? It constantly scans for the **"Unverified Alert"** popup image.

- **If it sees the popup:** It detects it immediately, closes the alert, logs out, and skips to the next account.
- **If it doesn't:** It proceeds to vote.

It’s not just automation; it’s _smart_ automation.

---

## 📈 The Result: The Math of Success

- **Speed:** 13 seconds per vote cycle.
- **The Calculation:**
  700 accounts × 13 seconds) ÷ 3600 ≈ 2.5 hours
- **The Payload:** 700 × 5 = 3,500 **points per day.**

In just two days, I managed to pump **10,000 points** into the system. Not bad for a one-man army, right? =))

---

## 💀 The Tragedy (Bruh Moment)

It was too good to last.

After three days, the Dev Team at Lan Song Xanh apparently woke up. They dropped the ban hammer:

> **Registration and Login is now restricted to Gmail accounts only.**

Just like that, my factory of temp-mail accounts became useless.

## 🔮 What Next?

My 700 soldiers are all XXXXXX.

Am I giving up?
I don't know... but **WHERE THERE'S A WILL, THERE'S A WAY.**

_To be continued... or not._

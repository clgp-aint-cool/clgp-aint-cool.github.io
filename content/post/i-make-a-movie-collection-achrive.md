---
title: "I'm Hosting My Fav Actress's Movie Vault!"
author: clgp
date: '2025-11-15'
categories:
  - Projects
tags:
  - Web
---

## I Made a Movie Site for My Fave Actress (And I Was Lazy AF Doing It)

<img src = "/images/ltm.jpg" >

First off, why? Because I'm a fan. I love her films, I love her vibe, and I wanted a place to archive it all.

**You can see the live site here: https://lamthanhmymovies.vercel.app**

---

### How I Pulled It Off

So, how'd I build it? Months of intense coding? Nope.

My main strategy: **Prompting, prompting, and more prompting.**

This "vibe coding" style is honestly so much fun for a personal project. Did I write *some* TypeScript? Sure. But let's be real, it's basically JavaScript... and I prompted the AI for most of it anyway (hehe, lazy af ✌️).

The setup itself is a joke thanks to **Next.js**.

```bash
npx create-next-app@latest
```

Seriously, that's the command. If you're a non-tech person, you can still do this. Just follow a YouTube tutorial (or just prompt an AI!) and you can totally build a site for your hobby.

## The "How Do I Stream for $0?" Problem

My biggest headache was the streaming. I wanted you to click a poster and
navigate to the page to watch the movie, but I wanted a 100% free method.

The Solution: I just uploaded all the movie files to my Google Drive and
embedded the Drive player (youtube) right into the site.

After a bit of testing, it worked flawlessly.
(Okay, so the quality stops at 1080p, but for a free solution? I'll take it.)

## Going Live

When it was time to deploy, Vercel was the only answer. It's free and practically built for Next.js. A couple of YouTube tutorials helped me stick the landing.

And that's the blog. Go build something cool.

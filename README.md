## NOTE! MultiBot was written as there was no way to view subreddits in a custom user feed on some mobile apps (including the official iOS app). However, as the feature has since been implemented, MultiBot is obsolete as of February 2020 (and will likely be forever).

# MultiBot ![](https://img.shields.io/github/release/marcusmunch/multibot.svg)

`multibot` is a Reddit bot that interacts with [/r/MultiHub](https://reddit.com/r/multihub) in various ways (currently only one though).

MultiBot can:

- [x] Post comments to submissions
- [ ] Update comments if changes were made to the multireddit
- [ ] Remove its own comments if they get voted below a certain karma threshold (i.e. -1)


## Usage
Currently, `multibot` only contains two files: `multibot.py` and `poster.py`. `multibot.py` is most of the machinery in terms of parsing multireddits and generating text strings for the comments to post. It will not do anything if run directly. `poster.py`, on the other hand, posts comments. It can be run as follows:

```bash
python poster.py [-d] [-v 0]
```

The `-d` is for Debug mode, while `-v` specifies verbosity (default of 0)

### Debug mode
There are currently only a few differences between regular execution and debug mode. Currently, debug mode:

- Doesn't skip posts that are already commented on
- Doesn't sleep in between posts (non-debug mode sleeps for 10 minutes after posting a reply)
- Doesn't actually post any replies. Rather, it prints a line of text in lieu of replying to a post

### Verbosity
Currently, there are three levels of verbosity: 0, 1 and 2. Each increasing level (of course) includes messages from lower levels.

`-v 0`: This is the default level. Only feedback returned to stdout is successful authentication and posts in which MultiBot has posted replies.

`-v 1`: This is where things start happening. Some more information is given:

- stdout: Newly discovered subreddits and their title (the short description that you'll see in your tab/window name)
- stderr: Comment was skipped, either because the linked multireddit could not be found or it was already commented on by the bot's account.

`-v 2`: Additionally, this level prints the full comment that is about to be replied with.

import json
import sys
import re

import praw
import prawcore


VERSION = "0.1"

SUBSTRINGS_PATH = "substrings.txt"
VERBOSITY = 0


try:
    open(SUBSTRINGS_PATH, "r").close()
except FileNotFoundError:
    sys.stderr.write("{} not found. Creating...\n".format(SUBSTRINGS_PATH))
    with open(SUBSTRINGS_PATH, "w") as f:
        f.write("{}")


def authenticate(username):
    reddit = praw.Reddit(username, user_agent="python:multihubbot:v{}".format(VERSION))
    username = reddit.user.me()

    print("Authenticated as {}!".format(username))
    return reddit


def get_multisub_tuple(reddit_url):
    """Parses a reddit_url into a (user, multireddit) tuple to return.

    Note: Raises an AttributeError if URL doesn't fit the format given by sublink_pattern

    :param str reddit_url: The URL for a multireddit.
    """

    sublink_pattern = "[A-Za-z0-9\-\_]*\/m\/[A-Za-z0-9\-\_]*"
    return re.search(sublink_pattern, reddit_url).group(0).split("/m/")


def get_multisub_subreddits(reddit, multisub_tuple):
    try:
        return reddit.multireddit(multisub_tuple[0], multisub_tuple[1]).subreddits
    except prawcore.exceptions.NotFound:
        if VERBOSITY > 0:
            sys.stderr.write("MultiReddit {0} not found!\n".format(multisub_tuple))
        raise


def get_subreddit_string(subreddit):
    """Get the title string for a subreddit from substrings.txt rather than requesting it from the API for every post.
    This increases the speed of the bot (which can be useful when it gathers enough karma to comment freely).

    Returns a tuple consisting of the title and True/False for NSFW status.

    :param str subreddit: Name of the subreddit to get the title (and NSFW status) from.
    """

    with open("substrings.txt") as f:
        strings = json.load(f)
    if not subreddit.display_name in strings:  # Not yet discovered
        try:
            subreddit_desc = subreddit.title
            strings.update({subreddit.display_name: (subreddit_desc, subreddit.over18)})

            if VERBOSITY > 0:
                print("Found subreddit /r/{} - {}".format(subreddit.display_name, subreddit_desc))

            with open("substrings.txt", "w") as f:
                json.dump(strings, f, indent=2, sort_keys=True)

        except prawcore.exceptions.Forbidden:  # Subreddit is private
            strings.update({subreddit.display_name: ("Private", False)})
            with open("substrings.txt", "w") as f:
                json.dump(strings, f, indent=2, sort_keys=True)

        except prawcore.exceptions.NotFound:  # Subreddit is banned
            strings.update({subreddit.display_name: ("BANNED", False)})
            with open("substrings.txt", "w") as f:
                json.dump(strings, f, indent=2, sort_keys=True)

    return strings[subreddit.display_name]


def multireddit_string(subreddit_list, subreddit_name):
    fullstring = ""
    header = "The multireddit \"{}\" contains {} subs:\n\n".format(subreddit_name, len(subreddit_list))
    footer = "\n^^^Bleep ^^^bloop, ^^^I'm ^^^a ^^^bot ^^^and ^^^under ^^^development!"

    fullstring += header

    for i in subreddit_list:
        description, over18 = get_subreddit_string(i)

        if description == "BANNED":
            print("{} is banned!".format(i.display_name))
            continue

        if over18:
            substring = "- /r/{} (NSFW) - {}".format(i.display_name, description)
        else:
            substring = "- /r/{} - {}".format(i.display_name, description)
        fullstring += substring + "\n"

    fullstring += footer

    if VERBOSITY > 1:
        print(fullstring)
    return fullstring
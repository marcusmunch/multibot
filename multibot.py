import json
import sys
import re

import praw
import prawcore


SUBSTRINGS_PATH = "substrings.txt"
VERBOSITY = 0


try:
    open(SUBSTRINGS_PATH, "r").close()
except FileNotFoundError:
    sys.stderr.write("{} not found. Creating...\n".format(SUBSTRINGS_PATH))
    with open(SUBSTRINGS_PATH, "w") as f:
        f.write("{}")


def authenticate(username="mhb"):
    reddit = praw.Reddit(username)
    username = reddit.user.me()

    print("Authenticated as {}!".format(username))
    return reddit


def get_multisub_tuple(reddit_url):
    sublink_pattern = "[A-Za-z0-9\-\_]*\/m\/[A-Za-z0-9\-\_]*"
    try:
        sublink = re.search(sublink_pattern, reddit_url).group(0)
        return sublink.split("/m/")
    except AttributeError:  # Re.search returns no groups
        raise


def get_multisub_subreddits(reddit, multisub_tuple):
    try:
        return reddit.multireddit(multisub_tuple[0], multisub_tuple[1]).subreddits
    except prawcore.exceptions.NotFound:
        if VERBOSITY > 0:
            sys.stderr.write("MultiReddit {0} not found!\n".format(multisub_tuple))
        raise


def get_subreddit_string(subreddit):
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

    return strings[subreddit.display_name]


def multireddit_string(subreddit_list):
    fullstring = ""
    preface = "This multireddit contains {} subs:\n\n".format(len(subreddit_list))
    end = "\nBleep bloop, I'm a bot and under development!"

    fullstring += preface

    for i in subreddit_list:
        description, over18 = get_subreddit_string(i)

        if over18:
            substring = "- /r/{} (NSFW) - {}".format(i.display_name, description)
        else:
            substring = "- /r/{} - {}".format(i.display_name, description)
        fullstring += substring + "\n"

    fullstring += end

    if VERBOSITY >= 1:
        print(fullstring)
    return fullstring
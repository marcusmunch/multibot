# -*- coding: utf-8 -*-
"""MultiBot Poster

This file is poster.py - the script which scans for new posts in /r/multihub and comments with a list of subreddits
contained within a multireddit.

Be aware that running poster.py with no parameters starts scanning /r/multihub for posts. It is highly(!) recommended
that users test this script in debug mode (-d) and get familiar with it, since running it with no options will start
posting comments.

In the future, some things may (or may not) be added. These can be found in README.md, which you have hopefully also
read by now.

I know actually executing this script might not be relevant for many (it might even only be so if I fail to maintain the
bot). If you only use it to read through my code and learn what to (and what DEFINITELY not to) do, I'll have served my
purpose. By the end you'll hopefully find some ways to do things more efficiently than me and hopefully I will have
taught you something neat about Python.

Best regards and best of luck,
(/u/)MarcusMunch
Author
"""

import sys
from time import sleep
from argparse import ArgumentParser

import prawcore

import multibot


def argparser():
    """Quick parsing of system arguments. It needs to be done."""

    parser = ArgumentParser()
    parser.add_argument("-d", help="Debug mode", action="store_true")
    parser.add_argument("-v", help="Verbosity", type=int, default=0)
    args = parser.parse_args()

    return args


def do_the_thing(reddit, submission, debug=False):
    """Parse the linked submission and comment (unless debug mode is enabled). Returns False if post handling somehow
    failed underway, stderr should provide info needed for diagnostics."""

    if submission.is_self:  # Skip self posts
        return False
    if not submission.author:
        sys.stderr.write("Skipping deleted post\n")
        return False

    comment_authors = [c.author for c in submission.comments]

    if reddit.user.me() in comment_authors:
        if multibot.VERBOSITY > 0:
            sys.stderr.write("Already commented on: {} - skipping!\n".format(submission.title))
        if debug:
            pass  # Prevent wait for new posts when in debug mode
        else:
            return False

    try:
        multisub_tuple = multibot.get_multisub_tuple(submission.url)

        # Get the list of subreddits
        sub_list = multibot.get_multisub_subreddits(reddit, multisub_tuple)
    except AttributeError:  # Typically posts not being proper multireddits
        return False
    except prawcore.exceptions.NotFound:  # User deleted account (and/or sub?)
        return False

    # Compose the comment
    try:
        comment = multibot.multireddit_string(sub_list, multisub_tuple[1])
    except prawcore.exceptions.NotFound:
        print(submission.permalink)
        return False

    # Post the comment
    if not debug:
        submission.reply(comment)
        print("\n\nPosted reply to {}: {} - now sleeping...".format(submission.author, submission.title))
        try:
            sleep(600)
        except KeyboardInterrupt:
            sys.stderr.write("User interrupted!\n")
            exit(0)
    else:
        print("POST THE REPLY BLEEP BLOOP")


def main(praw_sect="mhb"):
    """
    Args:
        praw_sect: The section (specified in praw.ini) to authenticate with.
    """

    reddit = multibot.authenticate(praw_sect)
    subreddit = reddit.subreddit("multihub")
    args = argparser()

    multibot.VERBOSITY = args.v  # Set the verbosity
    if multibot.VERBOSITY > 0:
        print("Verbosity is set to {}!".format(multibot.VERBOSITY))

    for submission in subreddit.stream.submissions(skip_existing=False):
        do_the_thing(reddit, submission, debug=args.d)


if __name__ == "__main__":
    main()

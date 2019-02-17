# -*- coding: utf-8 -*-
"""MultiBot Poster

This file is poster.py - the script which scans for new posts in /r/multihub and comments with a list of subreddits
contained within a multireddit.

Currently the file works with only (mainly) one function, main(). I could have made do_the_thing(), but since main()
already did what I wanted it to do, I decided on sticking with the current model.

Example:
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


def main(praw_sect="mhb"):
    """

    Args:
        praw_sect: The section (specified in praw.ini) to authenticate with.
    """

    reddit = multibot.authenticate(praw_sect)
    my_name = reddit.user.me()
    subreddit = reddit.subreddit("multihub")
    args = argparser()

    multibot.VERBOSITY = args.v  # Set the verbosity
    if multibot.VERBOSITY > 0:
        print("Verbosity is set to {}!".format(multibot.VERBOSITY))

    for submission in subreddit.stream.submissions(skip_existing=False):
        if submission.is_self:  # Skip self posts
            continue

        # Look for self in users who commented in the thread
        comment_authors = [c.author for c in submission.comments]

        if my_name in comment_authors:  # Skip already commented posts
            if multibot.VERBOSITY > 0:
                sys.stderr.write("Already commented on: {} - skipping!\n".format(submission.title))
            if args.d:
                pass  # Prevent wait for new posts when in debug mode
            else:
                continue

        # Parse the multireddit link to a user-multi tuple
        try:
            multisub_tuple = multibot.get_multisub_tuple(submission.url)
        except AttributeError:  # Typically posts not being proper multireddits
            continue

        try:
            # Get the list of subs contained in the multireddit
            subs = multibot.get_multisub_subreddits(reddit, multisub_tuple)

            # Compose the comment
            reply_text = multibot.multireddit_string(subs, subreddit_name=multisub_tuple[1]) + "\n" + "-"*40

        except prawcore.exceptions.NotFound:
            continue

        # Post the comment
        if not args.d:
            submission.reply(reply_text)
            print("\n\nPosted reply to {}: {} - now sleeping...".format(submission.author, submission.title))
            sleep(600)
        else:
            print("POST THE REPLY BLEEP BLOOP")



if __name__ == "__main__":
    main()
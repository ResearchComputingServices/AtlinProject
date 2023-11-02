"""_summary_

Returns:
    _type_: _description_
"""
import argparse
import logging
import json

from colorama import Fore

from reddit_constants import RedditConstants as constants
from reddit_api_session import RedditAPISession

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def display_responses_dict(responses_dict : dict,
                           keys_of_interest : list) -> None:
    """displays responses from API calls in a visually appealing way

    Args:
        responses_dict (dict): contains the responses from the API get requests
        keys_of_interest (list): depending on the type of job the keys of interest will change
    """
    for key in responses_dict.keys():

        if key in keys_of_interest:

            value = str(responses_dict[key])

            print(Fore.RED + key, Fore.WHITE+':',value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def extract_replies_from_comment(comment : dict) -> dict:
    """checks to see if there are replies and if so returns them in a dict

    Args:
        comment (dict): comment from which to extract replies

    Returns:
        dict: continas all the replies to the comment. (empty if no replies)
    """

    replies = {}

    if 'replies' in comment.keys():
        replies = comment['replies']

    return replies

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_credentials_dict(file_path : str) -> dict:
    """ reads credentials from a json file

    Args:
        file_path (str): file path to json file containing reddit API credentials

    Returns:
        dict: dictionary containing API crediential fields
    """
    credentials_dict = {}

    with open(file_path, encoding='utf-8') as input_file:
        credentials_dict = json.load(input_file)

    return credentials_dict

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: Change --getPosts and --getComments so they dont require arguments (nrgs = 0?)
# TODO: Check if --post --getComments returns all comments
# TODO: add functionality for printing retrieved data to the screen
def extract_command_line_args() -> dict:
    """This code defines the command interface including the todo

    Returns:
        dict: dictionary representation of the command line arguements
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--'+constants.CL_ARG_CRED_FP_KEY,
                        help=constants.CL_ARG_CRED_FP_HELP,
                        default=constants.CL_ARG_CRED_FP_DEFAULT)

    # Return options
    parser.add_argument('--'+constants.CL_ARG_SORT_BY_KEY,
                        help=constants.CL_ARG_SORT_BY_HELP,
                        default=constants.CL_ARG_SORT_BY_DEFAULT)

    parser.add_argument('--'+constants.CL_ARG_TIME_FRAME_KEY,
                        help=constants.CL_ARG_TIME_FRAME_HELP,
                        default=constants.CL_ARG_TIME_FRAME_DEFAULT)

    parser.add_argument('--'+constants.CL_ARG_N_KEY,
                        help=constants.CL_ARG_N_HELP,
                        default=constants.MAX_NUM_RESPONSES_TOTAL,
                        type=int)

    # Items
    items = parser.add_mutually_exclusive_group(required=True)

    items.add_argument('--'+constants.CL_ARG_SUBREDDIT_KEY,
                       help=constants.CL_ARG_SUBREDDIT_HELP,
                       default=constants.CL_ARG_SUBREDDIT_DEFAULT)

    items.add_argument('--'+constants.CL_ARG_USER_KEY,
                       help=constants.CL_ARG_USER_HELP,
                       default=constants.CL_ARG_USER_DEFAULT)

    items.add_argument('--'+constants.CL_ARG_POST_KEY,
                       help=constants.CL_ARG_POST_HELP,
                       default=constants.CL_ARG_POST_DEFAULT,
                       nargs=2,)

    # Actions
    actions = parser.add_mutually_exclusive_group(required=True)

    actions.add_argument('--'+constants.CL_ARG_KEYWORD_KEY,
                         help=constants.CL_ARG_KEYWORD_HELP,
                         default=constants.CL_ARG_KEYWORD_DEFAULT)

    actions.add_argument('--'+constants.CL_ARG_GET_POSTS_KEY,
                         help=constants.CL_ARG_GET_POSTS_HELP,
                         default=constants.CL_ARG_GET_POSTS_DEFAULT,
                         type=int,
                         choices=[0,1])

    actions.add_argument('--'+constants.CL_ARG_GET_COMMENTS_KEY,
                         help=constants.CL_ARG_GET_COMMENTS_HELP,
                         default=constants.CL_ARG_GET_COMMENTS_DEFAULT,
                         type=int,
                         choices=[0,1])

    args = parser.parse_args()

    return vars(args)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#/r/canada/comments/176zyp4?sort=hot&limit=1&t=all&after=
#
def main():
    """  This code interacts with the RedditAPISession class using the command line interface
    Example command line calls:
        python reddit_api_cli.py --subreddit canada --getposts 1 --n 1 --sortBy new         -> <class 'dict'> dict_keys(['kind', 'data']) Listing
        python reddit_api_cli.py --subreddit canada --keyword maple --n 1 --sortBy top      -> <class 'dict'> dict_keys(['kind', 'data']) Listing 
        python reddit_api_cli.py --post canada 176zyp4 --getposts 1 --n 1                   -> <class 'list'> <class 'dict'> dict_keys(['kind', 'data']) [Listing]
        python reddit_api_cli.py --post canada 176zyp4 --getcomments 1 --n 1                -> <class 'list'> <class 'dict'> dict_keys(['kind', 'data']) [Listing]
        python reddit_api_cli.py --user Angry_Guppy --getcomments 1 --n 1                   -> <class 'dict'> dict_keys(['kind', 'data']) [Listing]
        python reddit_api_cli.py --user Angry_Guppy --getposts 1 --n 1                      -> <class 'dict'> dict_keys(['kind', 'data']) [Listing]
    """
    logging.basicConfig(level=logging.DEBUG,
                        format=constants.LOGGER_FORMAT_STR,
                        handlers=[logging.StreamHandler(),])

    # get command-line args in dict format
    job_dict = extract_command_line_args()

    credientals_dict = get_credentials_dict(job_dict[constants.CL_ARG_CRED_FP_KEY])

    session = RedditAPISession(credientals_dict)

    # collect all the responses generated by the RedditInterface named session
    if session.handle_job_dict(job_dict):
        # determine what type of data was scrape and how to display it       
        for response in session.list_of_responses:
            print(response)
    else:
        print(session.job_msg)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':

    main()

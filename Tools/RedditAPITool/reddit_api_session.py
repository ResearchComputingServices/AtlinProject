"""_summary_

Returns:
        _type_: _description_
"""

import logging
import requests

from Tools.RedditAPITool.reddit_constants import RedditConstants as constants
from Tools.RedditAPITool.reddit_data_classes import RedditComment, RedditPost, RedditScrapeResponse

# from reddit_constants import RedditConstants as constants
# from reddit_data_classes import RedditComment, RedditPost, RedditScrapeResponse

class RedditAPISession:
    """Add a short summary of the class here
    
    and a more detailed summary here.
    
    Attributes:
        atribute_1: description...
        atribute_2: description...
    """

    #########################################################################
    # Dunder Methods
    #########################################################################

    def __init__(   self,
                    credientals_dict : dict):

        # initialize logger
        username = credientals_dict['username']
        self.logger_ = logging.getLogger(f'RedditAPISession {username}' )
        self.logger_.info('Reddit API Session logger initialized.')

        # Initialize members

        self._credientals_dict = credientals_dict

        self._header = {}

        self._params = {}

        self._list_of_responses = []

        self._number_of_request = 0

        self._job_msg = ''

        self._oauth_successful = self._generate_authentified_header()

        if self._oauth_successful:
            self.logger_.info('Account successfully authenticated')
        else:
            self.logger_.error('Unable to authenticate account')

    #########################################################################
    # PRIVATE FUNCTIONS
    #########################################################################

    def _generate_authentified_header(  self,
                                        header_key = constants.DEFAULT_HEADER_KEY,
                                        header_value = constants.DEFAULT_HEADER_VALUE) -> bool:

        success_flag = False

        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        auth = requests.auth.HTTPBasicAuth( self._credientals_dict[constants.CRED_CLIENT_ID_KEY],
                                            self._credientals_dict[constants.CRED_SECRET_TOKEN_KEY])

        # setup our header info, which gives reddit a brief description of our app
        self._header[header_key] =  header_value

        # send our request for an OAuth token
        resp = requests.post(   constants.REDDIT_OAUTH_POST,
                                auth=auth,
                                data=self._credientals_dict,
                                headers=self._header,
                                timeout=constants.REQUEST_TIMEOUT)

        if resp.status_code == 200:
            success_flag = True

            # convert response to JSON and get access_token value
            token = resp.json()[constants.REDDIT_OAUTH_KEY]

            # add authorization to our headers dictionary
            self._header[constants.REDDUT_AUTHEN_KEY] = f"bearer {token}"
        else:
            self._job_msg = 'Authentication Failed'
            self.logger_.error(self._job_msg )

        return success_flag

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_comments_from_post(self,
                                job_dict: dict) -> bool:
        """This function scrape the comments for a post

        Args:
            job_dict (dict): contains the details required to fillin the url_string

        Returns:
            bool: returns true if the get request was successful
        """

        url_string = constants.API_BASE + 'r/'+job_dict['post'][0]+'/comments/'+job_dict['post'][1]

        self._params['limit'] = ''

        return self._request_get(url_string=url_string)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_user_comments( self,
                            job_dict: dict) -> bool:
        """This function returns all comments/replies from a given user

        Args:
            job_dict (dict): contains the details required to fillin the url_string

        Returns:
            bool: returns true if the get request was successful
        """

        # Construct the urlSring for the GET request
        url_string = constants.API_BASE + 'user/'+job_dict['user']+'/comments'

        # Submit Request
        return self._request_get(url_string=url_string)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_user_posts(self,
                        job_dict : bool) -> bool:
        """This function returns all comments/replies from a given user

        Args:
            job_dict (dict): contains the details required to fillin the url_string

        Returns:
            bool: returns true if the get request was successful
        """

        # Construct the urlSring for the GET request
        url_string = constants.API_BASE + 'user/' + job_dict['user'] + '/submitted'

        # Submit Request
        return self._request_get(url_string=url_string)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_subreddit_posts(   self,
                                job_dict : dict) -> bool:
        """This function returns the top (numResponses) posts in the subreddit (subRedditName)

        Args:
            job_dict (dict): contains the details required to fillin the url_string

        Returns:
            bool: returns true if the get request was successful
        """

        # Construct the urlSring for the GET request
        url_string = constants.API_BASE + 'r/'+job_dict['subreddit']+'/'+job_dict['sortBy']

        # Submit Request
        return self._request_get(url_string=url_string)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_subreddit_keyword_search(  self,
                                        job_dict : dict) -> bool:
        """This function does a keyword search of a subreddit

        Args:
            job_dict (dict): contains the details required to fillin the url_string

        Returns:
            bool: returns true if the get request was successful
        """

        # Construct the urlSring for the GET request
        url_string = constants.API_BASE + 'r/'+job_dict['subreddit'] + '/search/'

        # Construct the params for the GET request
        self._params['q'] = job_dict['keyword']
        self._params['restrict_sr'] = True

        # Submit Request
        return self._request_get(url_string= url_string)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_number_or_requests(self) -> int:

        perform_n_requests = 0

        if self._params['limit'] == '':
            perform_n_requests = 1
        else:
            perform_n_requests = self._params['limit'] // constants.MAX_NUM_RESPONSES_PER_REQUEST+1

        return perform_n_requests

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _request_get(   self,
                        url_string : str) -> bool:
        """ This function performs a GET call from requests as defined by it's arguments

        Args:
            url_string (str): _description_
            num_results_requested (int): _description_

        Returns:
            bool: _description_
        """

        self.logger_.info("Processing Get Request: %s \n %s", url_string, self._params)

        # Store thenumber of requests made so # of request per minute can be monitored
        self._number_of_request = self._get_number_or_requests()

        success_flag = False
        for _ in range(0, self._number_of_request):
            try:
                response = requests.get(url=url_string,
                                        headers = self._header,
                                        params = self._params,
                                        timeout= constants.REQUEST_TIMEOUT)

                self._params['after'] = self._process_response(self.get_json_list(response))
                success_flag = True

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                self._job_msg = f'A connection error or timeout occurred: {e}'
                self.logger_.error(self._job_msg)
            except requests.exceptions.HTTPError as e:
                self._job_msg = f'HTTP Error: {e}'
                self.logger_.error(self._job_msg)
            except requests.exceptions.RequestException as e:
                self._job_msg = f'An error occurred:{e}'
                self.logger_.error(self._job_msg)

        return success_flag

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_json_list(self,
                      response :requests.Response) -> list:
        """_summary_

        Args:
            response (requests.Response): _description_

        Returns:
            list: _description_
        """

        resp_json_list = response.json()

        if not isinstance(resp_json_list, list):
            resp_json_list = [response.json()]

        return resp_json_list
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _process_response(  self,
                            response_list : list) -> str:
        """ process the responds from the API Get Request

        Args:
            response (requests.Response):  json struct returned by API Get Request

        Returns:
            str: if further API calls are required this string is required
        """

        after_id = ''

        for resp_json in response_list:
            reddit_response = RedditScrapeResponse()

            for child in resp_json['data']['children']:
                if child['kind'] == 't1':
                    reddit_response.comments.append(self._extract_comments(child['data']))
                elif child['kind'] == 't3':
                    reddit_response.post_data = self._extract_post(child['data'])


            self._list_of_responses.append(reddit_response)

            # if multitple requests are need than update the after_id
            if len(resp_json['data']['children']) > 0:
                after_id = resp_json['data']['children'][-1]['data']['name']

        return after_id

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _extract_comments(self,
                          comments_json : dict) -> RedditComment:
        """_summary_

        Args:
            resp_json (_type_): _description_
        
        accepted_keys = ['author', 'author_fullname','body','parent_id', 'id', 'link_id','depth']
        """

        depth = 0
        if 'depth' in comments_json.keys():
            depth = int(comments_json['depth'])

        comment = RedditComment(author=comments_json['author'],
                                author_fullname=comments_json['author_fullname'],
                                id=comments_json['id'],
                                body=comments_json['body'],
                                depth=depth,
                                replies=[])

        if comments_json['replies'] != '':
            for child in comments_json['replies']['data']['children']:
                comment.replies.append(self._extract_comments(child['data']))

        return comment

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _extract_post(self, post_json) -> RedditPost:
        """_summary_

        Args:
            resp_json (_type_): _description_
        """

        return RedditPost(subreddit=post_json['subreddit'],
                          selftext=post_json['selftext'],
                          author_fullname=post_json['author_fullname'],
                          author=post_json['author'],
                          title=post_json['title'],
                          downs=int(post_json['downs']),
                          name=post_json['name'],
                          upvote_ratio=post_json['upvote_ratio'],
                          ups=int(post_json['ups']),
                          score=int(post_json['score']),
                          view_count=post_json['view_count'],
                          id=post_json['id'],
                          num_comments=post_json['num_comments'],
                          created_utc=post_json['created_utc'],)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _populate_params(   self,
                            job_dict : dict) -> None:
        """extracts the required params from the job dictionary

        Args:
            job_dict (dict): contains the data required to fill in the params dict
        """

        self._params['sort'] = job_dict['sortBy']
        self._params['limit'] = job_dict['n']
        self._params['t'] = job_dict['timeFrame']
        self._params['after'] = ''

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _handle_subreddit_job(self,
                              job_dict : dict) -> bool:
        """This function handles 'subreddit' type jobs

        Args:
            job_dict (dict): _description_

        Returns:
            bool: _description_
        """

        success_flag = False

        if len(job_dict['keyword']) > 0:
            success_flag = self._get_subreddit_keyword_search(job_dict)
        else:
            success_flag = self._get_subreddit_posts(job_dict)
            self._job_msg = 'defaulting to getpost'
            self.logger_.warning(self._job_msg)

        return success_flag

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _handle_user_job(self, job_dict) -> bool:
        """This function handles 'user' type jobs

        Args:
            job_dict (_type_): _description_

        Returns:
            bool: _description_
        """
        success_flag = False

        if job_dict['getposts'] == 1:
            success_flag = self._get_user_posts(job_dict)
        elif job_dict['getcomments'] == 1:
            success_flag = self._get_user_comments(job_dict)
        else:
            self._job_msg = 'No ACTION specified for user'
            self.logger_.erro(self._job_msg)

        return success_flag

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def handle_post_job(self,
                        job_dict : dict) -> bool:
        """This function handles 'post' type jobs. It is not as complex as the other 'handle job' 
        methods, but I included it for symmerty. 

        Args:
            job_dict (dict): _description_

        Returns:
            bool: _description_
        """
        return self._get_comments_from_post(job_dict)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def handle_job_dict(self,
                        job_dict : dict) -> bool:
        """This function performs the scraping job described in the job_dict dictionary.

        Args:
            job_dict (dict): 

        Returns:
            bool: _description_
        """

        self.logger_.info('Processing job: %s', job_dict)

        success_flag = False

        self._populate_params(job_dict)

        # This block of code calls the API command which is described in the job_dict
        if not self._oauth_successful:
            self._job_msg = 'Account was not authenticated.'
            self.logger_.error(self._job_msg)
        elif job_dict['subreddit'] != '':
            success_flag = self._handle_subreddit_job(job_dict)
        elif job_dict['user'] != '':
            success_flag = self._handle_user_job(job_dict)
        elif job_dict['post'][0] !=  '' and job_dict['post'][1] != '':
            success_flag = self.handle_post_job(job_dict)
        else:
            self._job_msg = 'No ITEM ID specified.'
            self.logger_.error(self._job_msg)

        if success_flag:
            self._job_msg = 'Successful'

        return success_flag

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @property
    def list_of_responses(self) -> list:
        """returns list_of_responses

        Returns:
            list: responses from the latest scrape job 
        """
        return self._list_of_responses

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @property
    def number_of_requests(self) -> int:
        """returns the number of requests sent to complete the latest job. This information
        is needed to keep track of quota.

        Returns:
            int: number of requests sent to complete latest job
        """
        return self._number_of_request

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @property
    def job_msg(self) -> str:
        """This function returns the job msg generated by job handling

        Returns:
            str: returns the job messages generated by the latest job
        """
        return self._job_msg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_keys_of_interest(self,
                             job_type : str) -> list:
        """Return the keys of interest depending on the job type

        Args:
            job_type (str): either get comments or get posts

        Returns:
            list: the list of keys in the response object we are interested in
        """

        keys_of_interest = []

        if job_type == constants.JOB_TYPE_KEYWORD or job_type == constants.JOB_TYPE_POSTS:
            keys_of_interest = constants.POST_KEYS_OF_INTEREST
        else:
            keys_of_interest = constants.COMMENT_KEYS_OF_INTEREST

        return keys_of_interest

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def End(self) -> None:
        """do any clean-up that needs to be done when ending the session
        """
        #do stuff here to end the session cleanly

        return
    
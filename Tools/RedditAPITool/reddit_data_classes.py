"""_summary_
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class RedditComment:
    """Add a short summary of the class here
    
    and a more detailed summary here.
    
    Attributes:
        atribute_1: description...
        atribute_2: description...
    """

    author : str
    author_fullname : str
    id: str
    body: str
    depth: int
    replies : List['RedditComment']

    def __str__(self):
        new_line = '\n'
        tab = '\t'
        arrow = r'\->'

        str_rep = f'{tab*self.depth}{arrow}{self.author} : {self.body}{new_line}'
        for reply in self.replies:
            str_rep = str_rep + reply.__str__()
            
        return str_rep

@dataclass
class RedditPost:
    """Add a short summary of the class here
    
    and a more detailed summary here.
    
    Attributes:
        atribute_1: description...
        atribute_2: description...
    """

    subreddit : str
    selftext : str
    author_fullname : str
    title : str
    name : str
    upvote_ratio : float
    ups : int
    downs : int
    score : int
    view_count : int
    id : str
    author : str
    num_comments : int
    created_utc : float

    def __str__(self):
        new_line = '\n'
        
        str_rep =   (f'subreddit : {self.subreddit}{new_line}'
                    f'selftext : {self.selftext}{new_line}'
                    f'author_fullname : {self.author_fullname}{new_line}'
                    f'title : {self.title}{new_line}'
                    f'name : {self.name}{new_line}'
                    f'upvote_ratio : {self.upvote_ratio}{new_line}'
                    f'ups : {self.ups}{new_line}'
                    f'downs : {self.downs}{new_line}'
                    f'score : {self.score}{new_line}'
                    f'view_count : {self.view_count}{new_line}'
                    f'id : {self.id}{new_line}'
                    f'author : {self.author}{new_line}'
                    f'num_comments : {self.num_comments}{new_line}'
                    f'created_utc : {self.created_utc}{new_line}')

        return str_rep


@dataclass
class RedditScrapeResponse:
    """Add a short summary of the class here
    
    and a more detailed summary here.
    
    Attributes:
        atribute_1: description...
        atribute_2: description...
    """
    comments : list = field(default_factory=list)
    post_data : RedditPost = None
    
    def __str__(self):
        new_line = '\n'
   
        str_rep = ''
        
        if(self.post_data is not None):
            str_rep = f'{self.post_data}{new_line}'

        
        if(self.comments is not None):
            for comment in self.comments:
                str_rep = str_rep + comment.__str__()

        return str_rep

def main():
    """_summary_
    """
    reply = RedditComment(  author='another_person',
                            author_fullname='t2_99xgav37',
                            id='99xgav37',
                            body='a civil responses',
                            replies=[],
                            depth=1)

    a_comment = RedditComment(author='some_person',
                            author_fullname='t2_5ovxy',
                            id='5ovxy',
                            body='some kinda statement',
                            replies=[reply],
                            depth=0)

    a_post = RedditPost(subreddit='canada',
                        selftext='',
                        author_fullname = 't2_5ovxy',
                        title = 'Classic Rockers the Guess Who Sue Ex-Members for False Advertising',
                        downs=0,
                        name='t3_17k1cn8',
                        upvote_ratio= 0.83,
                        ups=4,
                        score=4,
                        view_count=0,
                        id='17k1cn8',
                        author='MaplePoutineRyeBeer',
                        num_comments=0,
                        created_utc=1698693876.0)

    scrape_response = RedditScrapeResponse()
    
    scrape_response.post_data =a_post
    scrape_response.comments = [a_comment]

    print(scrape_response)

if __name__ == "__main__":
    main()

from cliffhanger.pages.newsession import page as newsession
from cliffhanger.pages.joinsession import page as joinsession
from cliffhanger.pages.play import page as play
from cliffhanger.pages.home import page as home

# First page is default page for bad url
# None is interpreted as a divider
pages = [home, None, newsession, joinsession, play]

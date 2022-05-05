"""The various pages of the document where None means a divider in the menu and the first page is default."""

from cliffhanger.pages.newsession import page as newsession
from cliffhanger.pages.joinsession import page as joinsession
from cliffhanger.pages.play import page as play
from cliffhanger.pages.home import page as home

pages = [home, joinsession, newsession, play]

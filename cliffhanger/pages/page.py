"""The page object template."""
import logging

logger = logging.getLogger(__name__)


class Page():
    """Page class which represents core properties of a page."""

    def __init__(self, url, display_name, layout_function, callbacks, show_in_navbar):
        """Initialize a page object.

        Args:
            url (str): the relative url beginning in /
            display_name (str): the name to display in menus which reference the page
            layout_function (function): the function which defines the layout
            callbacks (list): the list of callbacks for the page
            show_in_navbar (bool): if True, will appear in the navbar. Hidden of false
        """
        if url[0] != '/':
            logger.warn(f"Page {url} with display name {display_name} does not begin with /, will likely fail to load.")
        self.url = url
        self.display_name = display_name
        self.layout_function = layout_function
        self.callbacks = callbacks
        self.show_in_navbar = show_in_navbar

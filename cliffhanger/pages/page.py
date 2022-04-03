import logging

logger = logging.getLogger(__name__)

class Page():
    def __init__(self, url, display_name, layout, callbacks):
        if url[0] != '/':
            logger.warn(f"Page {url} with display name {display_name} does not begin with /, will likely fail to load.")
        self.url = url
        self.display_name = display_name
        self.layout = layout
        self.callbacks = callbacks
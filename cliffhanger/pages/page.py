class Page():
    def __init__(self, url, display_name, layout, callbacks):
        self.url = url
        self.display_name = display_name
        self.layout = layout
        self.callbacks = callbacks
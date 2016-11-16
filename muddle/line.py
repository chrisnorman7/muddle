"""A line class."""

class Line:
    def __init__(self, text):
        """Initialise the line."""
        try:
            text = str(text.decode(errors = 'ignore'))
        except AttributeError:
            pass # Not needed.
        self.text = text
        self._gag = False
        self._sub = None
    
    def gag(self):
        """Gag the received text."""
        self._gag = True
    
    def ungag(self):
        """Ungag the text."""
        self._gag = False
    
    def gagged(self):
        """Return whether the text is gagged."""
        return self._gag
    
    def substitute(self, text):
        """Substitute the actual text with the provided text."""
        self._sub = text
    
    def unsusbstitute(self):
        """Remove any substitution."""
        self._sub = None
    
    def substituted(self):
        """Return whether the text is substituted or not."""
        return self._sub is not None

    def get_text(self):
        """Get the text from the line."""
        if not self.gagged():
            if self.substituted():
                return self._sub
            else:
                return self.text

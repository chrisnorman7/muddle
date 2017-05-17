"""A line class."""

from attr import attrs, attrib, Factory


@attrs
class Line:
    """A generic line."""
    text = attrib()
    _gag = attrib(default=Factory(lambda: False), init=False)
    _sub = attrib(default=Factory(lambda: False), init=False)

    def __attrs_post_init__(self):
        try:
            self.text = str(self.text.decode(errors='ignore'))
        except AttributeError:
            pass  # Not needed.
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

    def unsubstitute(self):
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

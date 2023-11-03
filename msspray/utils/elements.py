class Element:
    def __init__(self, type: str, value: str):
        """Individual element object

        :param type: selenium object type
        :param value: type value for lookups
        """
        self.type = type
        self.value = value


class Elements:
    """Mapping of element objects

    Default: Microsoft Login via XPATH

    Each element can be adjusted according to the target
    In some cases, using a different type for each field can
    be more accurate than using a single type lookup for all
    elements

    Type Options:
        ID
        NAME
        XPATH
        LINK_TEXT
        PARTIAL_LINK_TEXT
        TAG_NAME
        CLASS_NAME
        CSS_SELECTOR
    """

    # Username field
    username = Element(
        type="XPATH",
        value='//*[@id="i0116"]',
    )

    # Password field
    password = Element(
        type="XPATH",
        value='//*[@id="i0118"]',
    )

    # Next button
    next = Element(
        type="XPATH",
        value='//*[@id="idSIButton9"]',
    )

    # Login button
    login = Element(
        type="XPATH",
        value='//*[@id="idSIButton9"]',
    )

    # Invalid user error
    usererror = Element(
        type="XPATH",
        value='//*[@id="usernameError"]',
    )

    # Invalid password error
    passerror = Element(
        type="XPATH",
        value='//*[@id="passwordError"]',
    )

    # Account locked error
    locked = Element(
        type="XPATH",
        value='//*[@id="idTD_Error"]',
    )

    # Work/Personal selection
    work = Element(
        type="XPATH",
        value='//*[@id="aadTile"]',
    )

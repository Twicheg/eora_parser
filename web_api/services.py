from functools import wraps
import re

class HtmlSupport:
    """class provides methods to help convert to html format"""

    @staticmethod
    def replace_n(disable=False):
        """Replace \n to <br>"""
        def wrapper(f):
            @wraps(f)
            async def wrapped(*args, **kwargs):
                if disable:
                    return await f(*args, **kwargs)
                return (await f(*args, **kwargs)).replace("\n", "<br> ")
            return wrapped
        return wrapper

    @staticmethod
    def set_links(disable=False):
        """Replace links to <a href=link>link</a>"""
        def wrapper(f):
            @wraps(f)
            async def wrapped(*args, **kwargs):
                if disable:
                    return await f(*args, **kwargs)
                result = await f(*args, **kwargs)
                for link in re.findall(r"https://\S+", result):
                    if link.endswith(")"):
                        link = link[:-1]
                    result = result.replace(link, f" <a href={link}>{link}</a> ")
                return result
            return wrapped
        return wrapper



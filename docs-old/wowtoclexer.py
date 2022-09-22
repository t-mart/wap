from pygments.lexer import RegexLexer, bygroups
from pygments.token import Comment, Literal, Name, Operator, Text


# mypy: allow-subclassing-any
class WoWTocLexer(RegexLexer):
    name = "wowtoc"
    filenames = ["*.toc"]

    tokens = {
        "root": [
            # (
            #     r"^(##)(\s+)([^:]+)(:)(\s+)(.+)$",
            #     bygroups(
            #         Comment.Preproc,
            #         Text,
            #         Name.Tag,
            #         Operator,
            #         Text,
            #         Literal.String,
            #     ),
            # ),
            (r"^#([^#\n].*)?$", Comment),
            # (r"^[^#\s].*$", Name),
        ]
    }

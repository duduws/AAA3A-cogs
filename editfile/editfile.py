from .AAA3A_utils import CogsUtils, Menu  # isort:skip
from redbot.core import commands  # isort:skip
from redbot.core.i18n import Translator, cog_i18n  # isort:skip
from redbot.core.bot import Red  # isort:skip
import discord  # isort:skip

import inspect
import io
import os
import re
import typing
from os import listdir
from pathlib import Path

from redbot.core import Config, data_manager
from redbot.core.utils.chat_formatting import box, pagify

if CogsUtils().is_dpy2:  # To remove
    setattr(commands, "Literal", typing.Literal)

# Credits:
# I made this cog to be able to update files on my bot's host machine easily and quickly, without having to update cogs from GitHub for all my tests.
# Thanks to @epic guy on Discord for the basic syntax (command groups, commands) and also commands (await ctx.send, await ctx.author.send, await ctx.message.delete())!
# Thanks to the developers of the cogs I added features to as it taught me how to make a cog! (Chessgame by WildStriker, Captcha by Kreusada, Speak by Epic guy and Rommer by Dav)
# Thanks to all the people who helped me with some commands in the #coding channel of the redbot support server!

_ = Translator("EditFile", __file__)

if CogsUtils().is_dpy2:
    from functools import partial

    hybrid_command = partial(commands.hybrid_command, with_app_command=False)
    hybrid_group = partial(commands.hybrid_group, with_app_command=False)
else:
    hybrid_command = commands.command
    hybrid_group = commands.group


@cog_i18n(_)
class EditFile(commands.Cog):
    """A cog to get a file and replace it from its path from Discord!"""

    def __init__(self, bot: Red):
        self.bot: Red = bot

        self.cogsutils = CogsUtils(cog=self)

    @commands.is_owner()
    @hybrid_group(aliases=["fileedit"])
    async def editfile(self, ctx: commands.Context):
        """Commands group to get a file and replace it from its path."""
        pass

    @editfile.command()
    async def get(
        self,
        ctx: commands.Context,
        menu: typing.Optional[bool] = False,
        show_line: typing.Optional[bool] = False,
        *,
        path: str,
    ):
        """Get a file on the bot's host machine from its path.
        `#L10` or `#L10-L30` is supported.
        """
        match = re.compile(r"(?:\.\/+)?(.+?)(?:#L?(\d+)(?:\-L?(\d+))?)?$").search(path)
        if match is None:
            raise commands.UserFeedbackCheckFailure(_("Couldn't parse this input."))
        path = match.group(1)
        line_span = None
        if match.group(2) is not None:
            start = int(match.group(2))
            line_span = (start, int(match.group(3) or start))
        path = self.cogsutils.replace_var_paths(path, reverse=True)
        path = Path(path)
        try:
            size = os.path.getsize(path)
            if size <= 0:
                raise commands.UserFeedbackCheckFailure(
                    _(
                        "Cowardly refusing to read a file with no size stat. (it may be empty, endless or inaccessible)."
                    )
                )
            if size > 128 * (1024**2):
                raise commands.UserFeedbackCheckFailure(
                    _("Cowardly refusing to read a file >128MB.")
                )
            with open(file=path, mode="rb") as file:
                content = file.read()
            if line_span is not None:
                lines = content.split(b"\n")[line_span[0] - 1 : line_span[1]]
            else:
                lines = content.split(b"\n")
            lines_without_count = lines
            if show_line:
                lines = []
                count = (line_span[0] - 1) if line_span is not None else 0
                for line in lines_without_count:
                    count += 1
                    lines.append(f"{count}: ".encode(encoding="utf-8") + line)
            file = discord.File(fp=io.BytesIO(b"\n".join(lines_without_count)), filename=path.name)
        except FileNotFoundError:
            raise commands.UserFeedbackCheckFailure(
                _("This file cannot be found on the host machine.")
            )
        except IsADirectoryError:
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a directory, not a file.")
            )
        path = Path(self.cogsutils.replace_var_paths(str(path)))
        if menu:
            len_lines = len(content.split(b"\n"))
            line = (
                f"#L1-L{len(lines)} (All)"
                if line_span is None
                else ("#L" + str(line_span[0]) + "-L" + str(line_span[1]) + f" / {len_lines}")
            )
            header = box(f"File {path}, line {line}.")
            pages = [
                {"content": (header + box(p, lang="py")), "file": file}
                for p in pagify(
                    (b"\n".join(lines)).decode(encoding="utf-8"), page_length=2000 - len(header)
                )
            ]
            if len(pages) == 0:
                len_lines = len(content.split(b"\n"))
                raise commands.UserFeedbackCheckFailure(
                    _("There are only {len_lines} lines in this file.").format(**locals())
                )
            await Menu(pages=pages, timeout=300, delete_after_timeout=None).start(ctx)
        else:
            await ctx.send(
                _("Here are the contents of the file `{path}`.").format(**locals()), file=file
            )

    @editfile.command()
    async def replace(
        self, ctx: commands.Context, path: str, *, content: typing.Optional[str] = None
    ):
        """Replace a file on the bot's host machine from its path.
        `#L10` or `#L10-L30` is supported.
        """
        line_span = None
        match = re.compile(r"(?:\.\/+)?(.+?)(?:#L?(\d+)(?:\-L?(\d+))?)?$").search(path)
        if match is None:
            raise commands.UserFeedbackCheckFailure(_("Couldn't parse this input."))
        path = match.group(1)
        if match.group(2):
            start = int(match.group(2))
            line_span = (start, int(match.group(3) or start))
        path = self.cogsutils.replace_var_paths(path, reverse=True)
        path = Path(path)
        try:
            with open(file=path, mode="rb") as file:
                old_file_content = file.read()
            try:
                if line_span is not None:
                    lines = old_file_content.split(b"\n")[line_span[0] - 1 : line_span[1]]
                else:
                    lines = old_file_content.split(b"\n")
            except IndexError:
                len_lines = len(old_file_content.split(b"\n"))
                raise commands.UserFeedbackCheckFailure(
                    _("There are only {len_lines} lines in this file.").format(**locals())
                )
            old_file = discord.File(fp=io.BytesIO(b"\n".join(lines)), filename=path.name)
        except FileNotFoundError:
            raise commands.UserFeedbackCheckFailure(
                _("This original file cannot be found on the host machine.")
            )
        except IsADirectoryError:
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a directory, not a file.")
            )
        if content is None and ctx.message.attachments == []:
            raise commands.UserFeedbackCheckFailure(
                _(
                    "You must send the command with an attachment that will be used to replace the original file."
                )
            )
        if content is not None:
            # remove ```py\n```
            if content.startswith("```") and content.endswith("```"):
                content = re.compile(r"^((```py(thon)?)(?=\s)|(```))").sub("", content)[:-3]
            # remove `foo`
            content = content.strip("` \n")
            new_file_content = content.encode(encoding="utf-8")
        else:
            new_file_content = await ctx.message.attachments[0].read()
        if line_span is not None:
            lines = (
                old_file_content.split(b"\n")[: line_span[0] - 1]
                + new_file_content.split(b"\n")
                + old_file_content.split(b"\n")[line_span[1] :]
            )
        else:
            lines = new_file_content.split(b"\n")
        with open(path, "wb") as file:
            file.write(b"\n".join(lines))
        path = Path(self.cogsutils.replace_var_paths(str(path)))
        await ctx.send(
            _(
                "This is the original/old file available at path `{path}`. Normally, this file has been replaced correctly."
            ).format(**locals()),
            file=old_file,
        )

    @editfile.command()
    async def findcog(self, ctx: commands.Context, cog: str):
        """Get a cog directory on the bot's host machine from its name."""
        cog_obj = ctx.bot.get_cog(cog)
        if cog_obj is None:
            await ctx.send(_("Could not find a cog with this name."))
            return
        cog_path = Path(inspect.getfile(cog_obj.__class__)).parent.resolve()
        cog_data_path = Path(data_manager.cog_data_path() / cog_obj.qualified_name).resolve()
        if not cog_data_path.exists():
            cog_data_path = None
            if not isinstance(getattr(cog_obj, "config", None), Config):
                reason = _("This cog does not store any data.")
            else:
                reason = _("This cog had its data directory removed.")
        list_files = "\n".join(
            [
                f"- {file}"
                for file in sorted(
                    cog_path.iterdir(), key=lambda file: file.is_dir(), reverse=True
                )
                if file.is_file() and file.suffix == ".py"
            ]
        )
        message = (
            f"Cog path: {cog_path}\nData path: {cog_data_path or reason}"
            + "\n\n"
            + f"Files `.py`:\n{list_files}"
        )
        message = self.cogsutils.replace_var_paths(message)
        await ctx.send(box(f"{message}"))

    @editfile.command()
    async def listdir(self, ctx: commands.Context, *, path: str):
        """List all files/directories of a directory from its path."""
        path = Path(self.cogsutils.replace_var_paths(path, reverse=True))
        if not path.exists():
            raise commands.UserFeedbackCheckFailure(
                _("This directory cannot be found on the host machine.")
            )
        if not path.is_dir():
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a file, not a directory.")
            )
        message = ""
        files = listdir(str(path))
        files = sorted(files, key=lambda file: (path / file).is_dir(), reverse=True)
        for file in files:
            path_file = path / file
            if path_file.is_file():
                message += "\n" + f"- [FILE] {file}"
            elif path_file.is_dir():
                message += "\n" + f"- [DIR] {file}"
        message = self.cogsutils.replace_var_paths(message)
        pages = [box(page, lang="ansi") for page in pagify(message, page_length=2000 - 12)]
        if len(pages) <= 3:
            for page in pages:
                await ctx.send(page)
        else:
            await ctx.send_interactive(pages)

    @editfile.command()
    async def rename(self, ctx: commands.Context, new_name: str, *, path: str):
        """Rename a file."""
        path = Path(self.cogsutils.replace_var_paths(path))
        if not path.exists():
            raise commands.UserFeedbackCheckFailure(
                _("This file cannot be found on the host machine.")
            )
        if not path.is_file() and path.is_dir():
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a directory, not a file.")
            )
        try:
            path.rename(target=Path(f"{path.parent}") + f"{new_name}")
        except FileNotFoundError:
            raise commands.UserFeedbackCheckFailure(
                _("This file cannot be found on the host machine.")
            )
        except IsADirectoryError:
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a directory, not a file.")
            )
        await ctx.send(_("The `{path}` file has been deleted.").format(**locals()))

    @editfile.command()
    async def delete(self, ctx: commands.Context, *, path: str):
        """Delete a file."""
        if not path.exists():
            raise commands.UserFeedbackCheckFailure(
                _("This file cannot be found on the host machine.")
            )
        if not path.is_file() and path.is_dir():
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a directory, not a file.")
            )
        path = Path(self.cogsutils.replace_var_paths(path))
        try:
            path.unlink()
        except FileNotFoundError:
            raise commands.UserFeedbackCheckFailure(
                _("This file cannot be found on the host machine.")
            )
        except IsADirectoryError:
            raise commands.UserFeedbackCheckFailure(
                _("The path you specified refers to a directory, not a file.")
            )
        await ctx.send(_("The `{path}` file has been deleted.").format(**locals()))

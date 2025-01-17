from redbot.core.bot import Red  # isort:skip
from redbot.core.utils import get_end_user_data_statement

from .reacttocommand import ReactToCommand

__red_end_user_data_statement__ = get_end_user_data_statement(file=__file__)


async def setup(bot: Red):
    cog = ReactToCommand(bot)
    await cog.cogsutils.add_cog(bot)

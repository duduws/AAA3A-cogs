from .AAA3A_utils import CogsUtils  # isort:skip
from redbot.core import commands  # isort:skip
from redbot.core.i18n import Translator, cog_i18n  # isort:skip
from redbot.core.bot import Red  # isort:skip
import discord  # isort:skip
import typing  # isort:skip

from redbot.core.utils.chat_formatting import box

if CogsUtils().is_dpy2:  # To remove
    setattr(commands, "Literal", typing.Literal)

_ = Translator("DiscordEdit", __file__)

if CogsUtils().is_dpy2:
    from functools import partial

    hybrid_command = partial(commands.hybrid_command, with_app_command=False)
    hybrid_group = partial(commands.hybrid_group, with_app_command=False)
else:
    hybrid_command = commands.command
    hybrid_group = commands.group

ERROR_MESSAGE = "I attempted to do something that Discord denied me permissions for. Your command failed to successfully complete.\n{error}"


@cog_i18n(_)
class EditVoiceChannel(commands.Cog):
    """A cog to edit voice channels!"""

    def __init__(self, bot: Red):  # Never executed except manually.
        self.bot: Red = bot

        self.cogsutils = CogsUtils(cog=self)

    async def check_voice_channel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if (
            not self.cogsutils.check_permissions_for(
                channel=channel, user=ctx.author, check=["manage_channel"]
            )
            and not ctx.author.id == ctx.guild.owner.id
            and ctx.author.id not in ctx.bot.owner_ids
        ):
            raise commands.UserFeedbackCheckFailure(
                _(
                    "I can not let you edit the voice channel {channel.mention} ({channel.id}) because I don't have the `manage_channel` permission."
                ).format(**locals())
            )
        if not self.cogsutils.check_permissions_for(
            channel=channel, user=ctx.guild.me, check=["manage_channel"]
        ):
            raise commands.UserFeedbackCheckFailure(
                _(
                    "I can not edit the voice channel {channel.mention} ({channel.id}) because you don't have the `manage_channel` permission."
                ).format(**locals())
            )
        return True

    @commands.guild_only()
    @commands.admin_or_permissions(manage_channels=True)
    @hybrid_group(aliases=["editvoiceroom"])
    async def editvoicechannel(self, ctx: commands.Context):
        """Commands for edit a voice channel."""
        pass

    @editvoicechannel.command(name="create")
    async def editvoicechannel_create(
        self,
        ctx: commands.Context,
        category: typing.Optional[discord.CategoryChannel] = None,
        *,
        name: str,
    ):
        """Create a voice channel."""
        try:
            await ctx.guild.create_voice_channel(
                name=name,
                category=category,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{name}.",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="clone")
    async def editvoicechannel_clone(
        self, ctx: commands.Context, channel: discord.VoiceChannel, *, name: str
    ):
        """Clone a voice channel."""
        await self.check_voice_channel(ctx, channel)
        try:
            await channel.clone(
                name=name,
                reason=f"{ctx.author} ({ctx.author.id}) has cloned the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="invite")
    async def editvoicechannel_invite(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        max_age: typing.Optional[float] = None,
        max_uses: typing.Optional[int] = None,
        temporary: typing.Optional[bool] = False,
        unique: typing.Optional[bool] = True,
    ):
        """Create an invite for a voice channel.

        `max_age`: How long the invite should last in days. If it's 0 then the invite doesn't expire.
        `max_uses`: How many uses the invite could be used for. If it's 0 then there are unlimited uses.
        `temporary`: Denotes that the invite grants temporary membership (i.e. they get kicked after they disconnect).
        `unique`: Indicates if a unique invite URL should be created. Defaults to True. If this is set to False then it will return a previously created invite.
        """
        await self.check_voice_channel(ctx, channel)
        try:
            invite = await channel.create_invite(
                max_age=(max_age or 0) * 86400,
                max_uses=max_uses,
                temporary=temporary,
                unique=unique,
                reason=f"{ctx.author} ({ctx.author.id}) has create an invite for the voice channel #{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )
        else:
            await ctx.send(invite.url)

    @editvoicechannel.command(name="name")
    async def editvoicechannel_name(
        self, ctx: commands.Context, channel: discord.VoiceChannel, name: str
    ):
        """Edit voice channel name."""
        await self.check_voice_channel(ctx, channel)
        try:
            await channel.edit(
                name=name,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="bitrate")
    async def editvoicechannel_bitrate(
        self, ctx: commands.Context, channel: discord.VoiceChannel, bitrate: int
    ):
        """Edit voice channel bitrate.

        It must be a number between 8000 and
        Level 1: 128000
        Level 2: 256000
        Level 3: 384000
        """
        await self.check_voice_channel(ctx, channel)
        if not bitrate >= 8000 or not bitrate <= ctx.guild.bitrate_limit:
            await ctx.send_help()
            return
        try:
            await channel.edit(
                bitrate=bitrate,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="nsfw")
    async def editvoicechannel_nsfw(
        self, ctx: commands.Context, channel: discord.VoiceChannel, nsfw: bool
    ):
        """Edit voice channel nsfw."""
        await self.check_voice_channel(ctx, channel)
        try:
            await channel.edit(
                nsfw=nsfw,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="userlimit")
    async def editvoicechannel_user_limit(
        self, ctx: commands.Context, channel: discord.VoiceChannel, user_limit: int
    ):
        """Edit voice channel user limit.

        It must be a number between 0 and 99.
        """
        await self.check_voice_channel(ctx, channel)
        if not user_limit >= 0 or not user_limit <= 99:
            await ctx.send_help()
            return
        try:
            await channel.edit(
                user_limit=user_limit,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    class PositionConverter(commands.Converter):
        async def convert(self, ctx: commands.Context, argument: str):
            try:
                position = int(argument)
            except ValueError:
                raise commands.BadArgument("The position must be an integer.")
            max_guild_text_channels_position = len(
                [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
            )
            if not position > 0 or not position < max_guild_text_channels_position + 1:
                raise commands.BadArgument(
                    f"The indicated position must be between 1 and {max_guild_text_channels_position}."
                )
            position = position - 1
            return position

    @editvoicechannel.command(name="position")
    async def editvoicechannel_position(
        self, ctx: commands.Context, channel: discord.VoiceChannel, *, position: PositionConverter
    ):
        """Edit voice channel position.

        Warning: Only voice channels are taken into account. Channel 1 is the highest positioned voice channel.
        Channels cannot be moved to a position that takes them out of their current category.
        """
        await self.check_voice_channel(ctx, channel)
        try:
            await channel.edit(
                position=position,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel !{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="syncpermissions")
    async def editvoicechannel_sync_permissions(
        self, ctx: commands.Context, channel: discord.VoiceChannel, sync_permissions: bool
    ):
        """Edit voice channel sync permissions."""
        await self.check_voice_channel(ctx, channel)
        try:
            await channel.edit(
                sync_permissions=sync_permissions,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="category")
    async def editvoicechannel_category(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        category: discord.CategoryChannel,
    ):
        """Edit voice channel category."""
        await self.check_voice_channel(ctx, channel)
        try:
            await channel.edit(
                category=category,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="videoqualitymode")
    async def editvoicechannel_video_quality_mode(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        video_quality_mode: commands.Literal["1", "2"],
    ):
        """Edit voice channel video quality mode.

        auto = 1
        full = 2
        """
        await self.check_voice_channel(ctx, channel)
        video_quality_mode = discord.VideoQualityMode(int(video_quality_mode))
        try:
            await channel.edit(
                video_quality_mode=video_quality_mode,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #!{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    class PermissionConverter(commands.Converter):
        async def convert(self, ctx: commands.Context, argument: str):
            permissions = [
                key for key, value in dict(discord.Permissions.all_channel()).items() if value
            ]
            if argument not in permissions:
                raise commands.BadArgument(_("This permission is invalid."))
            return argument

    @editvoicechannel.command(name="permissions", aliases=["overwrites", "perms"])
    async def editvoicechannel_permissions(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        permission: PermissionConverter,
        true_or_false: typing.Optional[bool],
        roles_or_users: commands.Greedy[typing.Union[discord.Member, discord.Role, str]],
    ):
        """Edit voice channel permissions/overwrites.

        create_instant_invite
        manage_channels
        add_reactions
        priority_speaker
        stream
        read_messages
        send_messages
        send_tts_messages
        manage_messages
        embed_links
        attach_files
        read_message_history
        mention_everyone
        external_emojis
        connect
        speak
        mute_members
        deafen_members
        move_members
        use_voice_activation
        manage_roles
        manage_webhooks
        use_application_commands
        request_to_speak
        manage_threads
        create_public_threads
        create_private_threads
        external_stickers
        send_messages_in_threads
        """
        await self.check_voice_channel(ctx, channel)
        targets = list(roles_or_users)
        for r in roles_or_users:
            if isinstance(r, str):
                if r == "everyone":
                    targets.remove(r)
                    targets.append(ctx.guild.default_role)
                else:
                    targets.remove(r)
        if not targets:
            return await ctx.send(
                _("You need to provide a role or user you want to edit permissions for.")
            )
        overwrites = channel.overwrites
        for target in targets:
            if target in overwrites:
                overwrites[target].update(**{permission: true_or_false})
            else:
                perm = discord.PermissionOverwrite(**{permission: true_or_false})
                overwrites[target] = perm
        try:
            await channel.edit(
                overwrites=overwrites,
                reason=f"{ctx.author} ({ctx.author.id}) has modified the voice channel #{channel.name} ({channel.id}).",
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

    @editvoicechannel.command(name="delete")
    async def editvoicechannel_delete(
        self,
        ctx: commands.Context,
        channel: discord.VoiceChannel,
        confirmation: typing.Optional[bool] = False,
    ):
        """Delete voice channel."""
        await self.check_voice_channel(ctx, channel)
        if not confirmation:
            embed: discord.Embed = discord.Embed()
            embed.title = _("⚠️ - Delete voice channel")
            embed.description = _(
                "Do you really want to delete the voice channel {channel.mention} ({channel.id})?"
            ).format(**locals())
            embed.color = 0xF00020
            if not await self.cogsutils.ConfirmationAsk(
                ctx, content=f"{ctx.author.mention}", embed=embed
            ):
                await self.cogsutils.delete_message(ctx.message)
                return
        try:
            await channel.delete(
                reason=f"{ctx.author} ({ctx.author.id}) has deleted the voice channel #!{channel.name} ({channel.id})."
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                _(ERROR_MESSAGE).format(error=box(e, lang="py"))
            )

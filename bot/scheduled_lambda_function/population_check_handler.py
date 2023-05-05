import traceback
from typing import Union

from bot.commons import gw2_guilds
from bot.commons import discord_interactions
from bot.commons import common_exceptions
from bot.commons import gw2_api_interactions
from bot.commons import template_utils
from bot.commons import discord_utils
from . import templates
from . import scheduled_lambda_utils


def handle_home_world_population_recheck(
    guilds_repo: gw2_guilds.Gw2GuildRepo,
    personality: discord_interactions.WebhookPersonality
) -> None:
    """
    An event where guilds home worlds must be re-checked in case their population has changed.
    Notification is sent if the population was changed.
    """
    worlds = gw2_api_interactions.get_home_worlds()

    for guild in guilds_repo.find_all_guilds([
        gw2_guilds.home_world_field_name,
        gw2_guilds.announcement_channels_field_name,
        gw2_guilds.wvw_roles_field_name,
        gw2_guilds.language_field_name
    ]):
        try:
            locale = scheduled_lambda_utils.get_guild_language_or_default(guild)
            home_world = scheduled_lambda_utils.get_guild_attribute_or_throw(guild, gw2_guilds.home_world_field_name)
            saved_population = home_world['population']
            current_population = extract_world_population(home_world['id'], worlds)

            notification_string = create_populations_update(home_world['name'], saved_population, current_population, locale)
            if notification_string is None:
                print(f'Guild with ID {guild[gw2_guilds.guild_id_field_name]} and home world {home_world["name"]} has no population change.')
                continue

            wvw_role_ids = scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.wvw_roles_field_name)
            if len(wvw_role_ids) > 0:
                notification_string += f'\n{discord_utils.mention_multiple_roles(wvw_role_ids)}'

            if notification_string is not None:
                scheduled_lambda_utils.post_to_announcement_channels(
                    guild_id=guild['id'],
                    personality=personality,
                    announcement_channels=scheduled_lambda_utils.get_guild_attribute_or_empty(guild, gw2_guilds.announcement_channels_field_name),
                    message=notification_string
                )
        except common_exceptions.NotFoundException:
            print(f"Guild with ID {guild['id']} has no home world set, so population recheck is skipped.")
        except gw2_api_interactions.ApiException:
            print(f"GW2 API exception while trying to recheck population of guild with ID {guild['id']}")
            traceback.print_exc()


def extract_world_population(world_id: int, worlds: list[dict]) -> str:
    for world in worlds:
        if world['id'] == world_id:
            return world['population']
    raise Exception(f'Internal error, the API did not respond with world with ID {world_id}')


def create_populations_update(world_name: str, saved: str, current: str, locale: str) -> Union[str, None]:
    """
    Create a string that displays the population update for the selected world. Return none if
    there is no update for the world.
    """
    if saved != current:
        if current == 'Full':
            transfer_summary = template_utils.get_localized_template(templates.transfer_summary_full, locale)
        else:
            transfer_summary = template_utils.get_localized_template(templates.transfer_summary_not_full, locale).format(
                gem_amount=template_utils.transfer_costs[current],
                emote_gem=discord_utils.custom_emote('gw2_gem', discord_utils.gem_emote_id)
            )
        return template_utils.get_localized_template(templates.population_changed, locale).format(
            emote_announce=discord_utils.default_emote('loud_sound'),
            world_name=world_name,
            previous=template_utils.get_localized_template(template_utils.populations, locale)[saved],
            current=template_utils.get_localized_template(template_utils.populations, locale)[current],
            transfer_summary=transfer_summary
        )
    else:
        return None


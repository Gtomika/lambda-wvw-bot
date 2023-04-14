import traceback

achievement_detail = {
    'hu': "- **{name}**: Jutalom {reward_amount}{reward_type}. Állapot: {progress}"
}

achievement_progress = {
    'hu': '{current}/{max} {emote_progress}'
}

achievement_progress_unknown = {
    'hu': '{emote_question}'
}


wvw_exotic_reward_chest_id = 78353
wvw_rare_reward_chest_id = 78485


def create_daily_achievement_detail_string(
        locale: str,
        template_utils,
        achievement,
        reward_type: str,
        progress: str,
):
    """
    Create nicely formatted string of an achievement. Progress string should be assembled with method below.
    """
    exotic_chest_reward_amount = __get_reward_amount_from_achievement(achievement, wvw_exotic_reward_chest_id)
    if exotic_chest_reward_amount > 0:
        potion_amount = 2
    else:
        potion_amount = 1

    return template_utils.get_localized_template(achievement_detail, locale).format(
        name=achievement['name'],
        reward_amount=potion_amount,
        reward_type=reward_type,
        progress=progress
    )


def create_achievement_progress_string(
        locale: str,
        discord_utils,
        template_utils,
        achievement,
        progress_array
):
    """
    Build progress string of an achievement.
    """
    unknown_progress_string = template_utils.get_localized_template(achievement_progress_unknown, locale).format(
        emote_question=discord_utils.default_emote('question')
    )
    try:
        if progress_array is None:
            return unknown_progress_string

        progress = __get_achievement_progress(achievement, progress_array)
        if 'current' in progress and 'max' in progress:
            current_amount: int = progress['current']
            max_amount: int = progress['max']
        else:  # should not happen with Wvw achievements
            current_amount = 0
            max_amount = 0
        done: bool = progress['done']
        progress_emote = discord_utils.default_emote('white_check_mark') if done else discord_utils.default_emote('x')

        return template_utils.get_localized_template(achievement_progress, locale).format(
            current=current_amount,
            max=max_amount,
            emote_progress=progress_emote
        )
    except BaseException as e:
        print('Exception while trying to compile achievement progress string')
        traceback.print_exc()
        return unknown_progress_string


def __get_achievement_progress(achievement, progress_array):
    for progress in progress_array:
        if achievement['id'] == progress['id']:
            return progress
    print('Error: progress of achievement not in array')


def __get_reward_amount_from_achievement(achievement, item_id: int) -> int:
    """
    Find how much of a certain item the achievement rewards. Item id is expected in GW2 API format.
    If there is no such reward, 0 is returned.
    """
    for reward in achievement['rewards']:
        if reward['type'] == 'Item' and reward['id'] == item_id:
            return reward['count']
    return 0

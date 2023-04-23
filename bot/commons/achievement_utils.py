achievement_detail = {
    'hu': "- **{name}**: Jutalom {reward_amount}{reward_type}. Állapot: {progress}",
    'en': "- **{name}** Reward {reward_amount}{reward_type}. Progress: {progress}"
}

achievement_progress = {
    'hu': '{current}/{max} {emote_progress}',
    'en': '{current}/{max} {emote_progress}'
}

achievement_progress_unknown = {
    'hu': '{emote_question}',
    'en': '{emote_question}'
}


wvw_exotic_reward_chest_id = 78353
wvw_rare_reward_chest_id = 78485


def get_reward_amount_from_achievement(achievement, item_id: int) -> int:
    """
    Find how much of a certain item the achievement rewards. Item id is expected in GW2 API format.
    If there is no such reward, 0 is returned.
    """
    for reward in achievement['rewards']:
        if reward['type'] == 'Item' and reward['id'] == item_id:
            return reward['count']
    return 0

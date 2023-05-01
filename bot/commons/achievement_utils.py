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

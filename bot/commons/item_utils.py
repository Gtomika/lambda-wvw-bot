
class Item:
    """
    Represents a GW2 item (or currency)
    """

    def __init__(self, item_id: int, item_name: str, emote_name: str, emote_id: int):
        self.item_id = item_id
        self.item_name = item_name
        self.emote_name = emote_name
        self.emote_id = emote_id


class ItemAmount:
    """
    A GW2 item (or currency) with the additional amount information.
    """

    def __init__(self, item: Item, amount: int):
        self.item = item
        self.amount = amount

    def increase_amount(self, additional: int):
        self.amount += additional


def __empty_amount(item: Item) -> ItemAmount:
    return ItemAmount(item, 0)


def empty_amounts(items):
    return [__empty_amount(item) for item in items]


def count_amounts_in_bags(amounts, bags):
    """
    Count the item amounts in a characters bags, bags array queried from the GW2 API.
    """
    for bag in bags:
        bag_contents = bag['inventory']
        __count_amounts(amounts, bag_contents, 'count')


def count_amounts_in_bank(amounts, bank):
    """
    Count the item amounts in the account bank, bank array queried from the GW2 API.
    """
    __count_amounts(amounts, bank, 'count')


def count_amounts_in_material_storage(amounts, storage):
    __count_amounts(amounts, storage, 'count')


def count_amounts_in_wallet(amounts, wallet):
    """
    Count the item amounts in the account wallet, wallet array queried from the GW2 API.
    """
    __count_amounts(amounts, wallet, 'value')


def count_amounts_in_shared_inventory(amounts, shared_inventory):
    """
    Count the item amounts in the account shared inventory, array queried from the GW2 API.
    """
    __count_amounts(amounts, shared_inventory, 'count')


def __count_amounts(amounts, resources, count_field_name: str):
    """
    Counts the amounts in the specified amounts array. Resources is an array of objects with item IDs and amounts,
    from the GW2 API. Each resource item must have 'id' field!
    Resources may have null elements which mean empty slots in GW2!
    """
    for resource in resources:
        if resource is None:
            continue
        __check_resource(amounts, resource, count_field_name)


def __check_resource(amounts, resource, count_field_name: str):
    for item_amount in amounts:
        if item_amount.item.item_id == resource['id']:
            item_amount.increase_amount(resource[count_field_name])


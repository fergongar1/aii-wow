from main.models import Item,UserItem,Keyword,User
from collections import Counter
import shelve

def load_similarities():
    shelf = shelve.open('dataRS.dat')
    item_keywords = get_item_keywords()
    user_keywords = top_users_keywords(item_keywords)
    shelf['item_keywords'] = item_keywords
    shelf['similarities'] = compute_similarities(item_keywords, user_keywords)
    shelf.close()

def recommend_items(user):
    shelf = shelve.open("dataRS.dat")
    
    liked_items = set()
    liked_items = set(ui.item.id for ui in UserItem.objects.filter(user=user))
    res = []
    if user not in shelf['similarities']:
        return res
    for item_id, score in shelf['similarities'][user]:
        if item_id not in liked_items:
            item = Item.objects.get(pk=item_id)
            res.append([item, 100 * score])
    shelf.close()
    return res

def compute_similarities(item_keywords, user_keywords):
    res = {}
    for user in user_keywords:
        top_items = {}
        for item in item_keywords:
            top_items[item] = dice_coefficient(user_keywords[user], item_keywords[item])
        res[user] = Counter(top_items).most_common(10)
        
    return res

def get_item_keywords():
    items = {}
    for item in Item.objects.all():
        item_id = item.id
        desc = item.descripcion
        tags = set(keyword.id for keyword in Keyword.objects.all() if keyword.keyword in desc)
        items[item_id] = tags

    return items

def top_users_keywords(item_keywords):
    users = {}
    # construye un diccionario {user_id: {tag_id: num_items}}
    for element in UserItem.objects.all():
        user_id = element.user.id
        item_id = element.item.id
        if item_id in item_keywords:
            users.setdefault(user_id, {})
            for keyword in item_keywords[item_id]:
                if(keyword in users[user_id]):
                    users[user_id][keyword] += 1
                else:
                    users[user_id][keyword] = 1
    # extrae las cinco palabras claves mas frecuentes de cada usuario
    for u in users:
        users[u] = set(keyword for keyword, num_items in Counter(users[u]).most_common(5))
    
    return users

def dice_coefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))
from main.models import Item,UserItem,Keyword,User
from bs4 import BeautifulSoup
import urllib.request

URL_BASE = "https://www.wowdb.com/"
KEYWORD_BASE_LIST = ["Back","Chest","Feet","Finger","Hands","Head","Legs","Neck","Shoulders","Trinket","Waist","Wrists",
                        "Main Hand", "Off Hand", "One Hand", "Ranged", "Two Hand", "Plate","Cloth","Leather","Mail",
                        "Strength","Mastery","Intellect","Haste","Critical Strike","Agility"]

def populate_database():    
    delete_tables()
    populate_items()
    populate_keywords()
    populate_users()
    print('Terminada la carga de la base de datos.')

def delete_tables():
    UserItem.objects.all().delete()
    Item.objects.all().delete()
    Keyword.objects.all().delete()

def extraer_items():
    lista=[]
    n_paginas = 3
    for i in range(n_paginas):
        url = URL_BASE + "items?filter-available=1&filter-bind=2&filter-slot=2359278&page=" + str(i+1)
        
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        table = s.find("table",class_=["listing-items"]).find("tbody")
        items = table.find_all("tr", recursive=False)
        
        lista.extend(items)
    return lista

def extraer_descripcion(item_url):
    f = urllib.request.urlopen(item_url)
    s = BeautifulSoup(f, "lxml")

    desc_dd = s.find("div",class_=['db-description']).find_all("dd")
    desc = ""
    for dd in desc_dd:
        desc+="".join(dd.stripped_strings)+" \n"

    return desc

def populate_keywords():
    print('Cargando palabras clave...')
    keywords = [Keyword.objects.create(keyword=kw) for kw in KEYWORD_BASE_LIST]
    
    print(str(len(keywords)) + ' palabras clave insertadas.')
    return keywords

def populate_items():
    print('Cargando objetos...')
    
    rows = extraer_items()
    items = []
    for row in rows:
        columns = row.find_all("td", recursive=False)
        col_name = columns[0]
        nom = "".join(col_name.stripped_strings)
        if (not any(itm.nombre==nom for itm in items)):
            item_url = col_name.find("a")['href']
            itemlvl = int(columns[1].string.strip())
            img_url = col_name.find("img")['src']
            slot = "".join(columns[3].stripped_strings)
            tipo = "".join(columns[5].stripped_strings)

            desc = extraer_descripcion(item_url)

            item = Item(nombre = nom,
                        descripcion = desc,
                        url_icono = img_url,
                        url = item_url,
                        ilvl = itemlvl,
                        slot = slot,
                        tipo = tipo)
            items.append(item)
    Item.objects.bulk_create(items)
    print(str(len(items)) + ' objetos insertados.')
    return items

def populate_users():
    print('Cargando usuarios...')
    items = Item.objects.all()
    users_keywords = {'usuario1': ['Plate','Strength'],
            'usuario2': ['Intellect','Cloth'],
            'usuario3': ['Agility','Mail']}
    for user in users_keywords:
        obj, _ = User.objects.get_or_create(username = user)
        obj.set_password("1234")
        obj.save()
        item_likes = []
        for item in items:
            if(all(keyword in item.descripcion for keyword in users_keywords[user])):
                item_likes.append(item)
            if(len(item_likes)>=5):
                break
        [UserItem.objects.create(item=item, user=obj) for item in item_likes]
    print(str(len(users_keywords)) + ' usuarios insertados.')
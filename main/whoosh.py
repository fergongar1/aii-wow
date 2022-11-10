from whoosh import qparser	
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, ID, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser,MultifieldParser

from main.models import Item, Keyword

DIR_INDEX = "index"

def get_schema():
    return Schema(nombre=TEXT(stored=True), ilvl=NUMERIC(int,stored=True), slot=TEXT(stored=True), tipo=TEXT(stored=True), url_icono=ID(stored=True),
                 id=NUMERIC(int,stored=True), keywords=KEYWORD(stored=True, commas=True, lowercase=True), descripcion=TEXT(stored=True),url=ID(stored=True))

def cargar_indexado():
    ix = create_in(DIR_INDEX, schema=get_schema())
    writer = ix.writer()
    items = Item.objects.all()
    i=0
    for item in items:
        desc = item.descripcion
        keywords = ",".join([kwd.keyword.replace(" ", "_") for kwd in Keyword.objects.all() if kwd.keyword in desc]) 
        writer.add_document(nombre=item.nombre, ilvl=item.ilvl, slot=item.slot,  tipo=item.tipo, keywords=keywords, 
                           descripcion=desc, id=item.id, url_icono=item.url_icono, url=item.url)
        i+=1
    writer.commit()
    print("Se han indexado "+str(i)+ " elementos.")

def busqueda_nombre(q):
    ix=open_dir(DIR_INDEX)      
    with ix.searcher() as searcher:
        query = QueryParser("nombre", ix.schema).parse(q)
        results = searcher.search(query, limit=10)
        items = []
        for r in results:
            item = {}
            item['id'] = r['id']
            item['nombre'] = r['nombre']
            item['ilvl'] = r['ilvl']
            item['url'] = r['url']
            item['url_icono'] = r['url_icono']
            item['keywords'] = r['keywords'].replace("_", " ")
            items.append(item)
    return items

def busqueda_slot_tipo(q):
    ix=open_dir(DIR_INDEX)      
    with ix.searcher() as searcher:
        query = MultifieldParser(["slot","tipo"], ix.schema,group=qparser.OrGroup).parse(q)
        results = searcher.search(query, limit=10)
        items = []
        for r in results:
            item = {}
            item['id'] = r['id']
            item['nombre'] = r['nombre']
            item['ilvl'] = r['ilvl']
            item['url'] = r['url']
            item['url_icono'] = r['url_icono']
            item['keywords'] = r['keywords'].replace("_", " ")
            items.append(item)
    return items

def busqueda_keyword(q):
    ix=open_dir(DIR_INDEX)      
    with ix.searcher() as searcher:
        lista_kwd = [i.decode('utf-8') for i in searcher.lexicon('keywords')]
        q = str(q.replace(' ','_').lower())  
        if q not in lista_kwd:
            raise ValueError("La palabra clave no se encuentra en la lista.")
            
        query = QueryParser("keywords", ix.schema).parse(q)
        results = searcher.search(query, limit=10)

        items = []
        for r in results:
            item = {}
            item['nombre'] = r['nombre']
            item['ilvl'] = r['ilvl']
            item['url'] = r['url']
            item['url_icono'] = r['url_icono']
            item['keywords'] = r['keywords'].replace("_", " ")
            items.append(item)
    return items

def busqueda_ilvl(lower_lim, upper_lim):
    ix=open_dir(DIR_INDEX)      
    with ix.searcher() as searcher:
        q = "[ " + str(lower_lim) + " TO " + str(upper_lim) + " ]"
        query = QueryParser("ilvl", ix.schema).parse(q)
        results = searcher.search(query, limit=10)
    
        items = []
        for r in results:
            item = {}
            item['nombre'] = r['nombre']
            item['ilvl'] = r['ilvl']
            item['url'] = r['url']
            item['url_icono'] = r['url_icono']
            item['keywords'] = r['keywords'].replace("_", " ")
            items.append(item)
    return items
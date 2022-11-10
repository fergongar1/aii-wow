import shelve
from collections import Counter

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth import login,authenticate
from django.db import IntegrityError

from main.recommendations import  load_similarities, recommend_items
from main.populate import populate_database
from main.forms import NameForm, LvlForm, KeywordForm, RegisterForm, SlotTypeForm
from main.models import Item, UserItem, Keyword, User
from main.whoosh import busqueda_slot_tipo, cargar_indexado, busqueda_nombre, busqueda_ilvl, busqueda_keyword

#  CONJUNTO DE VISTAS

def index(request): 
    all_items = Item.objects.all()
    items_popularity = {item: UserItem.objects.filter(item=item).count() for item in all_items}
    items = [item for item, popularity in Counter(items_popularity).most_common(10)]

    params = {'items':items, 'titulo':'Inicio'}
    if(request.user.is_authenticated):
        usuario = request.user
        user_items = [ui.item for ui in UserItem.objects.filter(user=usuario)]
        params['useritems'] = user_items
    return render(request,'items.html',params)

def populateDB(request):
    if request.user.is_superuser:
        populate_database() 
        return render(request,'populate.html')
    else:
        return HttpResponse('Debe ingresar como administrador',status=403)

def loadRS(request):
    if request.user.is_superuser:
        load_similarities()
        return render(request,'loadRS.html')
    else:
        return HttpResponse('Debe ingresar como administrador',status=403)
 
def whooshIndex(request):
    if request.user.is_superuser:
        cargar_indexado()
        return render(request,'whoosh_index.html')
    else:
        return HttpResponse('Debe ingresar como administrador',status=403)

def mis_items(request):
    if (not request.user.is_authenticated):
        return HttpResponse('Debe iniciar sesión',status=403)
    usuario = request.user
    items = [ui.item for ui in UserItem.objects.filter(user=usuario)]
    params = {'items':items, 'useritems':items,'titulo':'Mis objetos'}
    if 'add-success' in request.GET:
        params['message']="Objeto añadido a la lista con éxito."
    elif 'remove-success' in request.GET:
        params['message']="Objeto eliminado de la lista con éxito."
    return render(request,'items.html',params)

def recomendar_items(request):
    if (not request.user.is_authenticated):
        return HttpResponse('Debe iniciar sesión',status=403)
    usuario = request.user
    uid = usuario.id
    shelf = shelve.open("dataRS.dat")
    recommendations = recommend_items(uid)

    item_keywords = shelf['item_keywords']
    keywords = [", ".join([Keyword.objects.get(pk=kwd).keyword for kwd in item_keywords[item[0].id]]) 
                    if item[0].id in item_keywords else "-" for item in recommendations]

    items = zip(recommendations,keywords)
    params = {'items':items}
    shelf.close()
    return render(request, 'recommendations.html', params)

def login_view(request):
    if(request.user.is_authenticated):
        return HttpResponse('Debe ingresar como usuario anonimo',status=403)
    if request.method =='POST':
        form = AuthenticationForm(request.POST)
        usuario = request.POST['username']
        pwd = request.POST['password']
        acceso = authenticate(username=usuario,password=pwd)
        if acceso is None:
            params = {'form':form, 'message':'Usuario o contraseña incorrectas.'}
            return render(request,'login.html',params)
        if not acceso.is_active:
            params = {'form':form, 'message':'Usuario no activo.'}
            return render(request,'login.html',params)
        login(request,acceso)
        return render(request,'success_login.html')
    else:
        return render(request,'login.html', {'form': AuthenticationForm()})

def register_view(request):
    if(request.user.is_authenticated):
        return HttpResponse('Debe ingresar como usuario anonimo',status=403)
    if request.method =='POST':
        form = RegisterForm(request.POST)
        usuario = request.POST['username']
        pwd = request.POST['password']
        confirm_pwd = request.POST['confirm']
        acceso = authenticate(username=usuario,password=pwd)
        if pwd!=confirm_pwd:
            params = {'form':form, 'message':'Las contraseñas deben coincidir.'}
            return render(request,'register.html',params)
        try:
            user = User(username=usuario)
            user.set_password(pwd)
            user.save()
            login(request,user)
        except IntegrityError:
            params = {'form':form, 'message':'Usuario ya existente.'}
            return render(request,'register.html',params)
        return render(request,'success_login.html')
    else:
        return render(request,'register.html', {'form': RegisterForm()})

def add_item(request):
    if (not request.user.is_authenticated):
        return HttpResponse('Debe iniciar sesión',status=403)
    usuario = request.user
    item_id = request.GET.get('id',0)
    item = get_object_or_404(Item, pk=int(item_id))
    UserItem.objects.get_or_create(user=usuario,item=item)
    
    return redirect('/mis-items/?add-success')

def remove_item(request):
    if (not request.user.is_authenticated):
        return HttpResponse('Debe iniciar sesión',status=403)
    usuario = request.user
    item_id = request.GET.get('id',0)
    item = get_object_or_404(Item, pk=int(item_id))
    user_item = get_object_or_404(UserItem,user=usuario,item=item)
    user_item.delete()
    
    return redirect('/mis-items/?remove-success')

def buscar_por_nombre(request):
    if request.method =='POST':
        form = NameForm(request.POST)
        query = request.POST['query']
        items = busqueda_nombre(query)
        params = {'items':items, 'form':form, 'titulo': 'Búsqueda por nombre'}
        if(request.user.is_authenticated):
            usuario = request.user
            user_items = [ui.item.id for ui in UserItem.objects.filter(user=usuario)]
            params['useritems'] = user_items
        return render(request, 'search.html', params)
    else:
        return render(request,'search.html', {'form': NameForm(), 'titulo': 'Búsqueda por nombre'})

def buscar_por_slot_tipo(request):
    if request.method =='POST':
        form = SlotTypeForm(request.POST)
        query = request.POST['query']
        items = busqueda_slot_tipo(query)
        params = {'items':items, 'form':form, 'titulo': 'Búsqueda por slot o tipo'}
        if(request.user.is_authenticated):
            usuario = request.user
            user_items = [ui.item.id for ui in UserItem.objects.filter(user=usuario)]
            params['useritems'] = user_items
        return render(request, 'search.html', params)
    else:
        return render(request,'search.html', {'form': SlotTypeForm(), 'titulo': 'Búsqueda por slot o tipo'})


def buscar_por_nivel(request):
    if request.method =='POST':
        form = LvlForm(request.POST)
        low = request.POST['low_limit']
        upper = request.POST['upper_limit']
        items = busqueda_ilvl(low,upper)
        params = {'items':items, 'form':form, 'titulo': 'Búsqueda por nivel'}
        if(request.user.is_authenticated):
            usuario = request.user
            user_items = [ui.item.id for ui in UserItem.objects.filter(user=usuario)]
            params['useritems'] = user_items
        return render(request, 'search.html', params)
    else:
        return render(request,'search.html', {'form': LvlForm(), 'titulo': 'Búsqueda por nivel'})

def buscar_por_keyword(request):
    if request.method =='POST':
        form = KeywordForm(request.POST)
        keyword = request.POST['keyword']
        try:
            items = busqueda_keyword(keyword)
        except ValueError:
            return render(request,'search.html', {'form': form, 'titulo': 'Búsqueda por palabra clave', 'error_msg':'Palabra clave no existente'})
        params = {'items':items, 'form':form, 'titulo': 'Búsqueda por palabra clave'}
        if(request.user.is_authenticated):
            usuario = request.user
            user_items = [ui.item.id for ui in UserItem.objects.filter(user=usuario)]
            params['useritems'] = user_items
        return render(request, 'search.html', params)
    else:
        return render(request,'search.html', {'form': KeywordForm(), 'titulo': 'Búsqueda por palabra clave'})

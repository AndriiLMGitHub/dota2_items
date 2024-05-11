from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Dota2Item
import requests
import datetime
from django.utils.datastructures import MultiValueDictKeyError

TODAY = datetime.datetime.now().date()


def get_current_date():
    # Format the date as YYYY-MM-DD
    formatted_date = TODAY.strftime('%Y-%m-%d')
    return formatted_date


def get_date_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def date_to_timestamp(date):
    # Assuming date is in the format YYYY-MM-DD
    year, month, day = map(int, date.split('-'))
    dt = datetime.datetime(year, month, day)
    return dt.timestamp()


def get_resource():
    # Get API data from server
    r = requests.get(
        f'https://market.dota2.net/api/v2/history?key=n238hokFW7n38ZDTqxB32rT29YCWH24&date=1669852800&date_end={date_to_timestamp(get_current_date())}')

    resourse_data = r.json()['data']

    for item in resourse_data:
        if item['stage'] == '5':
            resourse_data.remove(item)
        else:
            continue

    return resourse_data


def get_all_unique_names():
    unique_names_list = Dota2Item.objects.values_list(
        'market_hash_name', flat=True).distinct()
    return unique_names_list


def get_all_unique_items():
    unique_names = get_all_unique_names()
    unique_items = []

    for name in unique_names:
        item = Dota2Item.objects.filter(
            market_hash_name=name).last()
        unique_items.append(item)

    return unique_items


def get_all_items_by_name(name):
    items = Dota2Item.objects.filter(
        market_hash_name=name).order_by('-time')
    return items


def create_db():
    # Get all items from API server
    data = get_resource()

    Dota2Item.objects.all().delete()

    # Save all items from API server into our database
    if data:
        for item in data:
            inst_item = Dota2Item.objects.create(
                market_hash_name=item['market_hash_name'],
                class_name=item['class'],
                instance=item['instance'],
                time=get_date_from_timestamp(int(item['time'])),
                event=item['event'],
                app=item['app'],
                stage=item['stage'],
                for_who=item['for'],
                amount=item['paid'] if 'paid' in item else item['received'],
                custom_id=item['custom_id'],
                currency=item['currency']
            )
            inst_item.save()


def get_all_id_from_items():
    id_list = Dota2Item.objects.values_list('item_id', flat=True)
    return list(id_list)


def index(request):
    data_items = get_resource()
    ids_from_db = get_all_id_from_items()

    if list(Dota2Item.objects.all()) == []:
        create_db()
        messages.success(request, 'Created new database')

    for i in range(len(data_items)):
        if data_items[i]['item_id'] == ids_from_db[i]:
            new_item = Dota2Item.objects.create(
                market_hash_name=data_items[i]['market_hash_name'],
                class_name=data_items[i]['class'],
                instance=data_items[i]['instance'],
                time=get_date_from_timestamp(int(data_items[i]['time'])),
                event=data_items[i]['event'],
                app=data_items[i]['app'],
                stage=data_items[i]['stage'],
                for_who=data_items[i]['for'],
                amount=data_items[i]['paid'] if 'paid' in data_items[i] else data_items[i]['received'],
                custom_id=data_items[i]['custom_id'],
                currency=data_items[i]['currency']
            )
            new_item.save()
            messages.success(request, 'Added new item')

    context = {
        'latest_items': Dota2Item.objects.all().order_by('-time')[:5]
    }

    return render(request, 'index.html', context)


def search_view(request):
    if request.method == 'GET':
        search_term = request.GET.get('q')
        search_results = Dota2Item.objects.filter(
            market_hash_name__icontains=search_term)[:1] if search_term else []
        if search_results:
            messages.success(
                request,
                f"Found success item {search_results.count()}"
            )
        else:
            messages.error(
                request,
                f"No results found"
            )
    return render(request, 'search.html', {'search_results': search_results})


def detail_item(request, item_id):
    single_item = get_object_or_404(Dota2Item, item_id=item_id)

    sells = []
    buys = []

    total_amount_buy = 0
    total_amount_sell = 0
    total_items = 0

    for item in get_all_items_by_name(single_item.market_hash_name):
        if item.event == "buy":
            buys.append(item)
            total_amount_buy += int(item.amount)
        else:
            sells.append(item)
            total_amount_sell += int(item.amount)
        total_items += 1

    context = {
        'single_item': single_item,
        'all_items': get_all_items_by_name(single_item.market_hash_name),
        'total_buy': int(total_amount_buy),
        'total_sell': int(total_amount_sell),
        'total_items': total_items,
        'sells': sells,
        'buys': buys,
    }

    return render(request, 'detail_item.html', context)

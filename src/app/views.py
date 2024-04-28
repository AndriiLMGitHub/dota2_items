from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Dota2Item
import requests


def get_resource():
    r = requests.get(
        'https://market.dota2.net/api/v2/history?key=n238hokFW7n38ZDTqxB32rT29YCWH24')

    return r.json()


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


def index(request):
    # Get all items from API server
    data = get_resource()

    # Save all items from API server into our database
    if data:
        for item in data['data']:
            inst_item = Dota2Item.objects.create(
                market_hash_name=item['market_hash_name'],
                class_name=item['class'],
                instance=item['instance'],
                time=item['time'],
                event=item['event'],
                app=item['app'],
                stage=item['stage'],
                for_who=item['for'],
                amount=item['paid'] if 'paid' in item else item['received'],
                custom_id=item['custom_id'],
                currency=item['currency']
            )
            inst_item.save()

    # Get all items from our database
    data = Dota2Item.objects.all()

    # Delete all items with stage = 5 (TRADE_STAGE_TIMED_OUT = 5)
    for item in data:
        if item.stage == '5':
            item.delete()

    context = {
        'unique_items': get_all_unique_items()
    }

    return render(request, 'index.html', context)


def search_view(request):
    if request.method == 'GET':
        # Get the search term from the query parameters
        search_term = request.GET['q']
        search_results = Dota2Item.objects.filter(
            market_hash_name__icontains=search_term) if search_term else []
        messages.success(
            request,
            f"Found success {search_results.count()} items"
        )
        return render(request, 'search.html',  {'search_results': search_results, 'search_term': search_term})


def detail_item(request, item_id):
    single_item = get_object_or_404(Dota2Item, item_id=item_id)

    total_amount_buy = 0
    total_amount_sell = 0
    total_items = 0

    for item in get_all_items_by_name(single_item.market_hash_name):
        total_amount_buy += int(item.amount) if item.event == 'buy' else 0
        total_amount_sell += int(item.amount) if item.event == 'sell' else 0
        total_items += 1

    context = {
        'single_item': single_item,
        'all_items': get_all_items_by_name(single_item.market_hash_name),
        'total_buy': int(total_amount_buy),
        'total_sell': int(total_amount_sell),
        'total_items': total_items,
    }

    return render(request, 'detail_item.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Dota2Item
import requests
import datetime
import time
import pytz

TODAY = datetime.datetime.now().date()
YESTERDAY = TODAY - datetime.timedelta(days=1)


def get_current_date():
    # Format the date as YYYY-MM-DD
    formatted_date = TODAY.strftime('%Y-%m-%d')
    return formatted_date


def get_date_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def get_kiyv_current_timestamp():
    # # Define the timezone for Kyiv
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    # # Get the current time in Kyiv
    kyiv_time = datetime.datetime.now(kyiv_tz)
    return kyiv_time.timestamp()


def date_to_timestamp(date):
    # Assuming date is in the format YYYY-MM-DD
    year, month, day = map(int, date.split('-'))
    dt = datetime.datetime(year, month, day)
    return dt.timestamp()


TIMESTAMP_NOW = round(date_to_timestamp(get_current_date()))
TIMESTAMP_KYIV_NOW = round(get_kiyv_current_timestamp())
TIMESTAMP_YESTERDAY = round(
    date_to_timestamp(YESTERDAY.strftime('%Y-%m-%d')))
# TIMESTAMP_YESTERDAY_KYIV = round(
#     date_to_timestamp(YESTERDAY.strftime('%Y-%m-%d')))


def get_resource():
    # Get API data from server
    r = requests.get(
        f'https://market.dota2.net/api/v2/history?key=n238hokFW7n38ZDTqxB32rT29YCWH24&date=1722076201&date_end={TIMESTAMP_NOW}')

    resourse_data = r.json()['data']

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
                item_id=item['item_id'],
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

    for item in Dota2Item.objects.all():
        if item.stage == "5":
            item.delete()


def get_all_id_from_items():
    id_list = Dota2Item.objects.values_list('item_id', flat=True)
    return list(id_list)


def get_interval_request():
    while True:
        try:
            response = requests.get(
                f"https://market.dota2.net/api/v2/history?key=n238hokFW7n38ZDTqxB32rT29YCWH24&date={TIMESTAMP_YESTERDAY}&date_end={TIMESTAMP_KYIV_NOW}")
            if response.status_code == 200:
                if response.json()['data'] != []:
                    for item in response.json()['data']:
                        new_item = Dota2Item.objects.create(
                            item_id=item['item_id'],
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
                        new_item.save()
                # print("Request successful:", response.json()['data'])
                return
            else:
                print(f"Request failed: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

        time.sleep(3600)  # Sleep for one hour (3600 seconds)


def index(request):

    if list(Dota2Item.objects.all()) == []:
        create_db()
        messages.success(request, 'Created new database')

    # get_interval_request()

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


def detail_item(request, pk):
    single_item = get_object_or_404(Dota2Item, pk=pk)

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

from django.shortcuts import render
import requests


def index(request):
    r = requests.get(
        'https://market.dota2.net/api/v2/history?key=n238hokFW7n38ZDTqxB32rT29YCWH24')

    data = r.json()
    return render(request, 'index.html', {'data': data})

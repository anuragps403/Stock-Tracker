from asgiref.sync import sync_to_async
from django.http.response import HttpResponse
from django.shortcuts import render
from yahoo_fin.stock_info import *
from threading import Thread
import queue
from asgiref.sync import sync_to_async

# Create your views here.
def stockPicker(request):
    try:
        stock_picker = tickers_nifty50()
    except:
        stock_picker = []
    print("Inside stockpicker")
    # print(stock_picker)
    return render(request, 'mainapp/stockpicker.html', {'stockpicker': stock_picker})


@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    else:
        return True


async def stockTracker(request):
    is_loginned = await checkAuthenticated(request)
    if not is_loginned:
        return HttpResponse("Login First")
    # print("Inside stocktracker")
    stockpicker = request.GET.getlist('stockpicker')
    data ={}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            return HttpResponse("Error")

    n_thread = len(stockpicker)
    thread_list = []
    que = queue.Queue()
    for i in range(n_thread):
        thread = Thread(target=lambda q, arg1: q.put({stockpicker[i] : get_quote_table(arg1)}), args = (que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)
    # try:
    #     for i in stockpicker:
    #         result = get_quote_table(i) 
    #         data.update({i : result})
    # except:
    #     pass
    
    # print("data",data)
    # print(get_quote_table(stockpicker[0]))
    return render(request, 'mainapp/stocktracker.html', {'data':data, 'room_name': 'track'})
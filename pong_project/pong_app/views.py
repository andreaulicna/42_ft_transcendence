from django.http import JsonResponse
from django.shortcuts import render

current_color = 'green'

def game(request):
	return render(request, 'game.html', {'initial_color': current_color})

def	toggle_color(request):
	global current_color
	if current_color == 'black':
		current_color = 'blue'
	else:
		current_color = 'black'
	return JsonResponse({'color': current_color})

from django.http import JsonResponse
from django.shortcuts import render

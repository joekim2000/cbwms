from django.shortcuts import render
import os
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.urls import reverse
from django.utils.translation import activate




def index(request):
	localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
	output = _("통합승인시스템")
	return HttpResponse(output)

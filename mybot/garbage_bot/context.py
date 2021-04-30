from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import os, json, re

import requests

import datetime
# Create your views here.

from garbage_bot.models import Remind, Area
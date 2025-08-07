from os import getenv
from google import genai
from google.genai import types

client = genai.Client(api_key=getenv("GOOGLE_API_KEY"))

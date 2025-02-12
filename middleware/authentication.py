from sanic import Sanic
from constants.AppConstants import AppConstants

app = Sanic.get_app(AppConstants.APP_NAME)

@app.on_request
async def example(request):
	print("I execute before the handler.")
	#TODO: readd authentication middleware for endpoints, 
	# use a list of allowed unauthenticated endpoint, such as /login
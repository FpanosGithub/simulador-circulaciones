import requests

url = 'https://mercave-backend.azurewebsites.net/material/ejes'

respuesta = requests.get(url, auth=('admintria', 'Mercave062023!'))
print (respuesta.status_code)
print (respuesta.text)
#
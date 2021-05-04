import mangopay
from mangopay.api import APIRequest

mangopay.client_id='myshinyplatttest'
mangopay.apikey='wFj7PpLVDHU9F6D4r9kL8fR65FhkNtWaQXiVYN0BSURGVSb6y7'

handler = APIRequest(sandbox=True, timeout=45.0)

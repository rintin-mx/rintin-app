import aiohttp
import json

async def make_post_request(url, data):
    '''
    Make an http request to AWS Lambda API
    
    Params:
    url: string
    data: dictionary
    
    Return:
    Endpoint response
    '''
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            try:
                response_data = await response.json()
                return response_data
            except aiohttp.ContentTypeError:
                return await response.text()


async def insert_product_to_db(data):
    '''
    Call async function for insertion in database
    
    Params:
    data: dictionary
    '''
    url = "https://nxmatrad06.execute-api.us-east-2.amazonaws.com/default/streamlit-product-creation"
    response = await make_post_request(url, data)
    print(response)
    return response
import requests
import pymongo

BASE_URL = 'http://neuromorpho.org/api/'

def get_neuromorpho_data_for_species(species, url=BASE_URL, sub='neuron/select/',  pagenum=0):
    """"""
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client.aibs
    coll = db.nmorpho

    furl = url+sub
    params = {
            "q":"species:"+species,
            "page":pagenum
             }
    page = requests.get(furl, params=params).json()
    number_of_pages = page['page']['totalPages']
    while (pagenum != number_of_pages):
        page = requests.get(furl, params=params).json()
        params['page'] += 1
        coll.insert_many(page['_embedded']['neuronResources'])
        print('inserted page {} of {} to database, count= {}'.format(params['page'], number_of_pages-1,coll.count()))




def get_neuron_ids(species, sub="neuron/select/", num_pages=None):
    furl = BASE_URL+sub

    params = {
            "q":"species:"+species,
            "page":0
             }
    page = requests.get(furl,params=params).json()
    page_num = page['page']['number']
    if not num_pages:
        num_pages = page['page']['totalPages']

    while(page_num != num_pages-1):
        params = {
                "q":"species:"+species,
                "page":page_num
                 }
        page = requests.get(furl,params=params).json()
        output = [(a['neuron_id'], a['neuron_name'], a['archive'],a['brain_region'],a['cell_type']) for a in page["_embedded"]["neuronResources"]]
        page_num += 1
        yield output

if __name__ == "__main__":
    a,b = get_neuron_ids(species="drosophila\ melanogaster", num_pages=2)
    print(a,b)

import requests
import time
import concurrent.futures
image_urls=[
    'https://unsplash.com/photos/woman-holding-a-smartphone-with-an-attached-sandisk-usb-drive-OVAomd4vZNs',
    'https://unsplash.com/photos/woman-in-pink-bow-headpiece-jAbeG4DMVCY',
    'https://unsplash.com/photos/hungarian-parliament-building-in-budapest-EyDPhY_idpQ',
    'https://unsplash.com/photos/people-on-cobblestone-street-at-golden-hour-ScBtoCFcuk8',
    'https://unsplash.com/photos/eroded-white-sandstone-formations-8jZmgPtDQaQ',
    'https://unsplash.com/photos/red-bromeliad-flower-in-foliage-BSkbVs7i-zA',
    'https://unsplash.com/photos/swing-ride-spinning-in-cloudy-sky--6_Y94Dk480',
    'https://unsplash.com/photos/glass-lily-with-orange-glass-leaves-EaJe7gb6LJw',
    'https://unsplash.com/photos/arched-window-with-rustic-brick-floor-VEPHVUxX0sE'
]
t1= time.perf_counter()
def download_image(url):
    img_bytes= requests.get(url).content
    img_name = url.split("/photos/")[1].rsplit("-", 1)[0]
    img_name = f'{img_name}.jpg'
    with open(img_name, 'wb') as img_file:
        img_file.write(img_bytes)
        print(f'{img_name} was downloaded')

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(download_image,image_urls)

t2= time.perf_counter()
print(f'Finished in {t2-t1} seconds')

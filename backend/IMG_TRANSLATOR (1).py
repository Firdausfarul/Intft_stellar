from PIL import Image
import base64
import requests
from io import BytesIO

rarity = [0.1, 0.2, 0.3, 0.4]
maxNum=0xffffffff
rarity_cum=[0, 0.1, 0.3, 0.6 , 1]

def imgTranslator(hex):
    gene_gender = int(hex[0:8], 16)/maxNum
    gene_hair = int(hex[56:64], 16) / maxNum
    gene_reserved = int(hex[8:16], 16)/maxNum
    gene_eyes = int(hex[16:24], 16)/maxNum
    gene_skin = int(hex[24:32], 16)/maxNum
    gene_shirt = int(hex[32:40], 16)/maxNum
    gene_flag = int(hex[40:48], 16)/maxNum
    gene_hat = int(hex[48:56], 16)/maxNum
    gender=0
    if(gene_gender>0.5):
        gender=1
    for i in range(len(rarity)):
        if(rarity_cum[i]<=gene_hair<=rarity_cum[i+1]):
            hair_name = str(gender) + str(i) +".png"
            break
    for i in range(len(rarity)):
        if (rarity_cum[i] <= gene_eyes <= rarity_cum[i + 1]):
            eyes_name = str(gender) + ".png"
            break
    for i in range(len(rarity)):
        if (rarity_cum[i] <= gene_skin <= rarity_cum[i + 1]):
            skin_name = str(gender) + str(i) + ".png"
            break
    for i in range(len(rarity)):
        if (rarity_cum[i] <= gene_shirt <= rarity_cum[i + 1]):
            shirt_name = str(i) + ".png"
            break
    for i in range(len(rarity)):
        if (rarity_cum[i] <= gene_flag <= rarity_cum[i + 1]):
            flag_name = str(i) + ".png"
            break
    for i in range(len(rarity)):
        if (rarity_cum[i] <= gene_hat <= rarity_cum[i + 1]):
            hat_name = str(i) + ".png"
    #tumpuk image dimulai
    print(hair_name, skin_name)
    url = 'https://github.com/Firdausfarul/Intft_stellar/raw/main/img/Hair/'+hair_name
    url2= "https://github.com/Firdausfarul/Intft_stellar/raw/main/img/Skin/"+skin_name
    url3 = "https://github.com/Firdausfarul/Intft_stellar/raw/main/img/Bg/"+flag_name
    url4 = "https://github.com/Firdausfarul/Intft_stellar/raw/main/img/Costume/0.png"
    url5 = "https://github.com/Firdausfarul/Intft_stellar/raw/main/img/Eye/"+eyes_name


    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((256,256), Image.ANTIALIAS)
    img = img.convert("RGBA")

    response2 = requests.get(url2)
    img2 = Image.open(BytesIO(response2.content))
    img2=img2.resize((256,256), Image.ANTIALIAS)
    img2=img2.convert("RGBA")

    response3 = requests.get(url3)
    img3 = Image.open(BytesIO(response3.content))
    img3 = img3.resize((256, 256), Image.ANTIALIAS)
    img3 = img3.convert("RGBA")

    response4 = requests.get(url4)
    img4 = Image.open(BytesIO(response4.content))
    img4 = img4.resize((256, 256), Image.ANTIALIAS)
    img4 = img4.convert("RGBA")

    response5 = requests.get(url5)
    img5 = Image.open(BytesIO(response5.content))
    img5 = img5.resize((256, 256), Image.ANTIALIAS)
    img5 = img5.convert("RGBA")


    final2 = Image.alpha_composite(img3, img)
    final2 = Image.alpha_composite(final2, img2)
    final2 = Image.alpha_composite(final2, img5)
    final2 = Image.alpha_composite(final2, img4)

    final2 = final2.resize((256,256), Image.ANTIALIAS)
    buffered = BytesIO()
    final2.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    final2.show()
    img_str = str(img_str)[2:]
    img_str = img_str[:-1]
    print(img_str)
    return img_str
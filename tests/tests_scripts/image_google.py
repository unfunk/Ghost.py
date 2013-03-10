import logging
import urllib
from ghost import Ghost, BlackPearl

BRAND = (
    ('ACURA', '1'),
    ('AEOLUS', '2'),
    ('ALEKO', '3'),
    ('ALFA ROMEO', '4'),
    ('ARO', '5'),
    ('ASIA', '6'),
    ('AUDI', '7'),
    ('AUSTIN', '8'),
    ('AUTOBIANCHI', '9'),
    ('BELAVTOMAZ', '10'),
    ('BERTONE', '11'),
    ('BLAC', '12'),
    ('BMW', '13'),
    ('CHERY', '14'),
    ('CHEVROLET', '15'),
    ('CHRYSLER', '16'),
    ('CITROEN', '17'),
    ('DACIA', '18'),
    ('DAEWOO', '19'),
    ('DAIHATSU', '20'),
    ('DEUTZ', '21'),
    ('DIMEX', '22'),
    ('ENIAK', '23'),
    ('F.E.R.E.S.A.', '24'),
    ('FERRARI', '25'),
    ('FIAT', '26'),
    ('FORD', '27'),
    ('G.A.Z.', '28'),
    ('GROSSPAL', '29'),
    ('HAM-JIANG', '30'),
    ('HEIBAO', '31'),
    ('HINO', '32'),
    ('HONDA', '33'),
    ('HUMMER', '34'),
    ('HYUNDAI', '35'),
    ('INTERNATIONAL', '36'),
    ('ISUZU', '37'),
    ('IVECO', '38'),
    ('IZH', '39'),
    ('JAC', '40'),
    ('JAGUAR', '41'),
    ('JINBEI', '42'),
    ('KAMAZ', '43'),
    ('KENWORTH', '44'),
    ('KIA', '45'),
    ('LADA', '46'),
    ('LANCIA', '47'),
    ('LIAZ', '48'),
    ('MAESTRO', '49'),
    ('MAHINDRA', '50'),
    ('MASERATI', '51'),
    ('MAZDA', '52'),
    ('MERCEDES BENZ', '53'),
    ('METRO', '54'),
    ('MINI COOPER', '55'),
    ('MITSUBISHI', '56'),
    ('NAKAI', '57'),
    ('NISSAN', '58'),
    ('OPEL', '59'),
    ('PEUGEOT', '60'),
    ('PIAGGIO', '61'),
    ('POLONEZ', '62'),
    ('PONTIAC', '63'),
    ('PORSCHE', '64'),
    ('PROTON', '65'),
    ('RANQUEL', '66'),
    ('RENAULT', '67'),
    ('ROLLS ROYCE', '68'),
    ('ROVER', '69'),
    ('SAAB', '70'),
    ('SANTANA', '71'),
    ('SANXING', '72'),
    ('SCANIA', '73'),
    ('SEAT', '74'),
    ('SKODA', '75'),
    ('SPACE', '76'),
    ('STAR', '77'),
    ('SUBARU', '78'),
    ('SUZUKI', '79'),
    ('TATA', '80'),
    ('TAVRIA', '81'),
    ('TOYOTA', '82'),
    ('UAZ', '83'),
    ('VOLKSWAGEN', '84'),
    ('VOLVO', '85'),
    ('WULING MOTORS', '86'),
    ('YANTAI', '87'),
    ('YUEJIN', '88'),
    ('SMART', '178'),
)

gh = Ghost(display=True,
            cache_size=10000,
            wait_timeout=30,
            download_images=True,
            individual_cookies=True)

for b in BRAND:
    try:
        name = "brand/%s" % b[1]
        page, resources = gh.create_page()
        page.open("https://www.google.com/search?hl=en&site=&tbm=isch&source=hp&q=wikipedia+logo+%s" % b[0])
        url = unicode(page.evaluate('document.querySelector(".rg_l").getAttribute("href")'))
        url = url.split("imgurl=")[1].split("&")[0]
        print url
        name += "." +  url.split(".")[-1]
        f = open(name,'wb')
        f.write(urllib.urlopen(url).read())
        f.close()
        print url
    except:
        print url

    
#page.evaluate('document.querySelector("#sbds input").click()')
#page.evaluate('document.querySelector("#lst-ib").value = "volkswagen gol foto2";')

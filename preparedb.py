import requests
from urllib.parse import quote
import time
from fake_useragent import UserAgent
import csv

file=open("hospitals","r")

hospitals=[]
corresponding_city=[]

data=file.read()
lines=data.split("\n")
cases=[l.split("\t") for l in lines]

for c in cases[:-1]:                                    #last line empty
        hospitals.append(c[2])
        corresponding_city.append(c[0])

bad_chars=["Ã¢","Ã©","Ã¯","Ã¨","Ã´"]
remplacents=["a","e","i","e","o"]

for i in range(len(hospitals)):                                                                 #clean data from no-assci characters that can cause problems
        for c in bad_chars:
                if c in hospitals[i]:
                        hospitals[i]=hospitals[i].replace(c,remplacents[bad_chars.index(c)])
                if c in corresponding_city[i]:
                        corresponding_city[i]=corresponding_city[i].replace(c,remplacents[bad_chars.index(c)])


search_name=[]

for i in range(len(hospitals)):
        h=hospitals[i]
        if "C." in h or "Centre" in h:
                s=h               
        elif "Hopital" in h:
                s=h
        else:
                h="Hopital "+h
                s=h
        if corresponding_city[i] in s:
                S=s
        else:
                S=s+" "+corresponding_city[i]
        search_name.append(S)


def find_coordinates(hospital):
        time.sleep(5)
        search_string="%2C"
        url="https://www.google.com/maps/search/"
        url+=quote(hospital)
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        r=requests.get(url,headers)
        pos1=r.text.index(search_string)
        start=pos1-1
        end=pos1+3
        while True:
                try:
                        int(r.text[start])
                        start-=1
                except:
                        if r.text[start]!="." and r.text[start]!="-":
                                break
                        else:
                                start-=1
        while True:
                try:
                        int(r.text[end])
                        end+=1
                except:
                        if r.text[end]!="." and r.text[end]!="-":
                                break
                        else:
                                end+=1
        return r.text[start+1:end]

def prepare_data():
        Locations=[]
        for s in search_name:
                coords=find_coordinates(s)
                coords=coords.split("%2C")
                for i in range(0,2):
                        coords[i]=float(coords[i])
                Locations.append(coords)
        db=zip(hospitals[:len(Locations)],corresponding_city[:len(Locations)],Locations)
        return db

hopitaux_db=prepare_data()


#db=[('Mohamed V', 'Al Hoceima', [35.23922315, -3.9389252]), ("C. d'oncologie d'Al Hoceima", 'Al Hoceima', [35.2374, -3.9281986]), ('Imzouren', 'Al Hoceima', [35.19148755, -3.92228785]), ('Targuist', 'Al Hoceima', [34.94016935, -4.31418375]), ('Mohamed V', 'Chefchaouen', [35.1687085, -5.27097515]), ('Ksar El Kebir', 'Larache', [34.992973, -5.9064296]), ('Lalla Meriem', 'Larache', [35.1855963, -6.156941]), ('Abou Kacem Zahraoui', 'Ouezzane', [34.7992138, -5.588535]), ('Assilah', 'Tanger Assilah', [35.46616005, -6.03072415]), ('Mohammed Vi', 'Tanger Assilah', [35.7511098, -5.8284885]), ('Arrazi', 'Tanger Assilah', [35.7579267, -5.8107983]), ('Mohamed V', 'Tanger Assilah', [35.7305941, -5.86921325]), ('Al Kortobi', 'Tanger Assilah', [35.7894825, -5.8184344]), ('Duc De Tovar', 'Tanger Assilah', [35.77884795, -5.8289123]), ("Centre d'oncologie", 'Tanger Assilah', [35.7345195, -5.839996]), ('Hopital mere enfant Mohamed VI', 'Tanger Assilah', [35.7511098, -5.8284885]), ('Hopital psychiatrique Mohamed VI', 'Tanger Assilah', [35.7404601, -5.85709725]), ('Hopital des specialite Mohamed VI', 'Tanger Assilah', [35.733773, -5.8746228]), ('Hopital.Civil', 'Tetouan', [35.573164, -5.355706]), ('Errazi', 'Tetouan', [35.5738426, -5.3588137]), ('Ben Karrich', 'Tetouan', [35.5102385, -5.4233944]), ('Hassan II', 'Mdiq-Fnideq', [35.8445194, -5.3659856]), ('Mohammed VI', 'Mdiq-Fnideq', [35.6805832, -5.3233213]), ('Edderak', 'Berkane', [34.9246983, -2.3261681]), ('Saidia', 'Berkane', [35.0880113, -2.239842]), ('Driouch', 'Driouch', [34.97788, -3.3886017]), ('Hassan II', 'Figuig', [32.10646675, -1.22265575]), ('Guercif', 'Guercif', [34.22610585, -3.35448675]), ('Jrada', 'Jerada', [34.31921015, -2.17669805]), ('Mohammed Vi', 'Nador', [35.00432, -3.0067742]), ('Hassani', 'Nador', [35.1759835, -2.9351665]), ('Zaio', 'Nador', [34.9424442, -2.7407221]), ('Al Farabi', 'Oujda Angad', [34.67558615, -1.91408055]), ('Hopital Psychiatrique', 'Oujda Angad', [34.6852989, -1.8760558]), ('Hopital des Specialitess', 'Oujda Angad', [34.66323455, -1.93927305]), ('Hopital Mere-Enfant', 'Oujda Angad', [34.6566352, -1.911876]), ("Centre d'oncoligie Hassan II", 'Oujda Angad', [34.62513005, -1.983456]), ('HPr Laayoune Sidi Mellouk', 'Taourirt', [34.58478225, -2.49841925]), ('Taourirt', 'Taourirt', [34.4074688, -2.902694]), ('Sidi Said', 'Meknes', [33.8926883, -5.5776681]), ('Mohamed V', 'Meknes', [33.90466875, -5.51026425]), ('Pagnon', 'Meknes', [33.9034792, -5.51456615]), ('Moulay Ismail', 'Meknes', [33.8906776, -5.5344986]), ("Centre d'oncologie", 'Meknes', [33.8933106, -5.5475131]), ('Marche Verte', 'Boulemane', [33.36386775, -4.73034375]), ('S. Ahmed B. Driss Missouri', 'Boulemane', [33.45411155, -5.65463835]), ('Prince My Hassan', 'El Hajeb', [33.6796249, -5.3768379]), ('Al Ghassani', 'Fes', [34.0181246, -5.0078451]), ('Ibn Al Baitar', 'Fes', [34.0430115, -4.9838275]), ("Hopital d'Oncologie", 'Fes', [34.0044999, -4.9607455]), ('Hopital des specialites', 'Fes', [34.01904295, -4.98204405]), ('Hopital Mere-Enfant', 'Fes', [34.0052106, -4.9631632]), ('Omar Drissi', 'Fes', [34.0579037, -4.9816889]), ('Ibn Al Khatib', 'Fes', [34.0629232, -4.9906229]), ('Ibn Al Hassan', 'Fes', [34.0613925, -5.00656845]), ('20 Aout (Azrou)', 'Ifrane', [33.43358805, -5.22880875]), ('Mohamed V', 'Sefrou', [33.8272193, -4.8357925]), ('Hassan II', 'Taounate', [34.57579735, -4.77761795]), ('Taounate', 'Taounate', [34.52890325, -4.6438429]), ('Ibn Baja', 'Taza', [34.21604525, -4.00449785]), ('Al Idrissi', 'Kenitra', [34.2481594, -6.5787587]), ('Zoubir Skirej', 'Kenitra', [34.46571575, -6.3030851]), ('Khemisset', 'Khemisset', [33.83057225, -6.0813761]), ('Roummani', 'Khemisset', [33.5298938, -6.6055375]), ('Tiflet', 'Khemisset', [33.89541515, -6.3266999]), ('Ibn Sina', 'Rabat', [33.9857772, -6.8530745]), ('Hopital Des Specialites', 'Rabat', [33.99180515, -6.8516728]), ('Maternite Souissi', 'Rabat', [33.9872248, -6.85538]), ("Hopital D'enfants", 'Rabat', [34.0037797, -6.83950705]), ('Maternite Orangers', 'Rabat', [34.0182139, -6.8387508]), ('Med Ben Abdellah', 'Rabat', [33.9976891, -6.81489555]), ('My Youssef', 'Rabat', [34.0102988, -6.8615694]), ('Moulay Youssef (Ancien hopital de Rabat)', 'Rabat', [34.0102988, -6.8615694]), ('El Ayachi', 'Sale', [34.0343765, -6.8260898]), ('Moulay Abdellah (Hop.prefectoral)', 'Sale', [34.0261709, -6.7533261]), ('Arrazi', 'Sale', [34.0361936, -6.8139535]), ('Jorf Elmelha', 'Sidi Kacem', [34.4929096, -5.497456]), ('Sidi Kacem', 'Sidi Kacem', [34.2209934, -5.69871505]), ('Sidi Slimane', 'Sidi Slimane', [34.2608477, -5.91924045]), ('Princesse Lalla Aicha (Ancien Sidi Lahcen)', 'Skhirate-Temara', [33.9179894, -6.9271501]), ('Haut Atlas Central', 'Azilal', [31.9634636, -6.5640298]), ('Demnate', 'Azilal', [31.7455517, -7.00489595]), ('Beni Mellal', 'Beni Mellal', [32.33345335, -6.36618465]), ('Moulay Ismail', 'Beni Mellal', [32.5884779, -6.2588566]), ('Beni Mellal', 'Beni Mellal', [32.33345335, -6.36618465]), ('Fquih Ben Salah', 'Fkih Ben Saleh', [32.50374565, -6.6905243]), ('Souk Sebt', 'Fkih Ben Saleh', [32.52261315, -6.63888295]), ('Khenifra', 'Khenifra', [32.9479924, -5.66962745]), ("M'Rirt", 'Khenifra', [33.1640223, -5.56321]), ('Mohamed VI', 'Khouribga', [33.1737863, -7.27452475]), ('Hassan II', 'Khouribga', [32.89261715, -6.90601495]), ('Oued.Zem', 'Khouribga', [32.86294615, -6.56960215]), ('Benslimane (Hassan II)', 'Benslimane', [33.630554, -7.1344901]), ('Berrchid', 'Berrechid', [33.26741585, -7.58131195]), ('Errazi', 'Berrechid', [33.2643354, -7.58414775]), ('Azemmour', 'El Jadida', [33.28762365, -8.3487689]), ('Mohamed V', 'El Jadida', [33.2433989, -8.49426425]), ('Mediouna', 'Mediouna', [33.4577594, -7.51910375]), ('Tit Mellil', 'Mediouna', [33.5407816, -7.4611798]), ('My Abdellah', 'Mohammedia', [33.6977869, -7.3855138]), ('Bouskoura', 'Nouaceur', [33.47204125, -7.62507165]), ('Prince My Hassan', 'Nouaceur', [33.44599015, -7.6871605]), ('Ben Ahmed', 'Settat', [33.0683435, -7.240907]), ('Hassan II', 'Settat', [32.9933691, -7.61188605]), ('Sidi Bennour', 'Sidi Bennour', [32.6509435, -8.41716065]), ('Zmamra', 'Sidi Bennour', [32.63017485, -8.5727868]), ('20 Aout 1953', 'Casablanca Anfa', [33.57503995, -7.61954055]), ('Ibn Rochd', 'Casablanca Anfa', [33.57950285, -7.62111175]), ("Hopital D'enfants", 'Casablanca Anfa', [33.56638875, -7.638743]), ('My Youssef', 'Casablanca Anfa', [33.6027446, -7.6322655]), ('Mohamed Baouafi', 'Al Fida-Mers Sultan', [33.55885715, -7.60934065]), ('Mohamed V', 'Ain Sebaa-Hay Mohammadi', [33.58928325, -7.55154225]), ('El Hassani', 'Hay Hassani', [33.5649762, -7.67752455]), ('Centre de Leprologie', 'Ain Chok', [33.55725145, -7.6083135]), ('Mohamed Sekkat', 'Ain Chok', [33.5463102, -7.5884098]), ('Al Mansour', 'Sidi Bernoussi', [33.6076083, -7.5033547]), ('HPr Sidi Moumen', 'Sidi Bernoussi', [33.5914245, -7.513835]), ('Ben Msick', 'Ben Msick', [33.5584053, -7.5730007]), ('Sidi Othmane', 'Moulay Rachid', [33.57140225, -7.5786586]), ('Mohammed VI', 'Al Haouz', [31.51224865, -8.35140105]), ('Mohamed Vi', 'Chichaoua', [31.5395889, -8.7684052]), ('Assalama', 'El Kelaa Des Sraghna', [32.048975, -7.4030825]), ('Hopital psychiatrique', 'El Kelaa Des Sraghna', [32.05142495, -7.39872135]), ('Princesse Lalla Khadija', 'El Kelaa Des Sraghna', [31.93447875, -7.45453275]), ('Sidi Med Ben Abdellah', 'Essaouira', [31.5110418, -9.763418]), ('Ibn Tofeil', 'Marrakech', [31.6419062, -8.0157537]), ('Ibn Nafis', 'Marrakech', [31.662246, -7.9963365]), ('Hopital Mere-Enfant', 'Marrakech', [31.664741, -7.9956104]), ("Centre d'Hematologie Oncologie", 'Marrakech', [31.664193, -7.9959249]), ('Arrazi', 'Marrakech', [31.6633669, -7.995191]), ('Ibn Zohr', 'Marrakech', [31.6183251, -7.9950524]), ('El Antaki', 'Marrakech', [31.6364423, -7.9851865]), ('Mhamid', 'Marrakech', [31.58937375, -8.0336454]), ('Charifa', 'Marrakech', [31.6065738, -7.9657827]), ('Saada', 'Marrakech', [31.6294118, -8.1116245]), ('Benguerir', 'Rehamena', [32.2276165, -7.9417713]), ('Mohamed V', 'Safi', [32.2880943, -9.2366444]), ('Aisha', 'Safi', [32.87854685, -8.43998755]), ('Lalla Hasna', 'Youssoufia', [32.2361156, -8.5109262]), ('Sghiri Houmman I Ben Maati', 'Errachidia', [31.9339099, -4.4233817]), ('My Ali Cherif', 'Errachidia', [31.9405972, -4.418251]), ('Hopital Amir Soultan Ibn Abdelaziz', 'Errachidia', [31.9405684, -4.41831035]), ('20 Aout (Goulmima)', 'Errachidia', [31.6842945, -4.960247]), ('Midelt', 'Midelt', [32.68583835, -4.743412]), ('HPr Rich', 'Midelt', [32.26802635, -4.4985373]), ('Sidi Hssain Bencer', 'Ouarzazate', [30.9253278, -6.9173163]), ('Bougafer', 'Ouarzazate', [30.9184325, -6.90440835]), ("HPr Kalaat M'gouna", 'Tinghir', [31.2498278, -6.11943575]), ('Tinghir', 'Tinghir', [31.5016467, -5.50419715]), ('Ed-Derrak', 'Zagora', [30.3532379, -5.8470933]), ('Hassan II', 'Agadir Ida Ou Tanane', [30.436159, -9.5903294]), ("C. d'Oncologie d'Agadir", 'Agadir Ida Ou Tanane', [30.4207931, -9.55859665]), ('Mokhtar Soussi', 'Chtouka Ait Baha', [30.412785, -9.572875]), ('Inezgane', 'Inezgane Ait Melloul', [30.3640009, -9.5431445]), ('Oulad Teima', 'Taroudant', [30.3944291, -9.22086515]), ('Mokhtar Es-Soussi', 'Taroudant', [30.473666, -8.875723]), ('Tata', 'Tata', [31.8622856, -7.4106387]), ('Hassan 1er', 'Tiznit', [29.705718, -9.7425218]), ('Houmman El Fatouaki', 'Tiznit', [29.6955676, -9.7293606]), ('Assa', 'Assa-zag', [28.60821245, -9.4358095]), ('Bouizakaren', 'Guelmim', [29.18069125, -9.71788185]), ('Guelmim', 'Guelmim', [28.98899575, -10.05897955]), ('Sidi Ifni', 'Sidi Ifni', [29.3790911, -10.1782047]), ('Hassan II', 'Tan Tan', [28.444443, -11.1110499]), ('Boujdour', 'Boujdour', [26.1159093, -14.47390505]), ('Es-Smara', 'Es Semara', [26.7438882, -11.6747184]), ('My Hassan Ben El Mehdi', 'Laayoune', [27.156723, -13.1892582]), ('Hassan II', 'Laayoune', [27.15089755, -13.1899828]), ('Laayoune', 'Laayoune', [27.14556255, -13.17055065]), ('Hassan II', 'Oued Ed-Dahab', [33.9990754, -6.8449787])]



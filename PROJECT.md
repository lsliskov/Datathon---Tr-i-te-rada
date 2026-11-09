# LabourPulse RH — projektna dokumentacija

## Sažetak

LabourPulse RH je interaktivni analitički pregled otvorenih podataka o potražnji
za radnicima u Hrvatskoj. Projekt povezuje HZZ oglase za posao, MUP-ove izdane
dozvole za boravak i rad te DZS podatke o stanovništvu i radnoj snazi.

Rezultat je namijenjen građanima, poslodavcima, lokalnoj upravi i donositeljima
odluka koji žele brzo vidjeti gdje je potražnja za radnicima najveća, koja su
zanimanja najtraženija i u kojim se djelatnostima koristi međunarodna radna snaga.

## Usklađenost s natjecanjem

Projekt odgovara kategoriji **Gospodarstvo i učinkovito upravljanje** jer:

- pretvara više javnih izvora u razumljiv regionalni pregled,
- podržava usporedbu županija i prepoznavanje regionalnih razlika,
- daje podatkovnu podlogu za planiranje obrazovanja, zapošljavanja i lokalnih mjera,
- prikazuje najtraženija zanimanja i djelatnosti,
- jasno razlikuje činjenice od interpretacije i prikazuje razdoblje svakog izvora,
- omogućuje izvoz tablica u XLSX za daljnju analizu i rad uprave.

### Mapiranje na kriterije ocjenjivanja

| Kriterij iz pravila | Kako ga projekt ispunjava |
|---|---|
| Korištenje otvorenih podataka | HZZ RSS, MUP javne statistike i DZS skupovi podataka; izvori, poveznice i datum preuzimanja su javno navedeni. |
| Relevantnost | Projekt odgovara na konkretno pitanje gdje su potrebe za radnicima najveće i koja su zanimanja tražena. |
| Uključivanje i korist za zajednicu | Javni dashboard je razumljiv građanima, poslodavcima i upravi; tablice se mogu preuzeti u XLSX-u za daljnju uporabu. |
| Inovativnost i primjena tehnologije | Više izvora objedinjeno je u interaktivnu analizu. Ova verzija ne koristi AI, IoT, blockchain ni drugu naprednu tehnologiju. |
| Izvedivost i integracijski potencijal | Projekt je reproducibilan iz lokalno spremljenih izvadaka, koristi jednostavan Streamlit/Pandas sloj i jasno odvaja učitavanje podataka od prikaza. |
| Prezentacija | Aplikacija vodi korisnika od sažetka preko regionalne usporedbe do zanimanja, djelatnosti i metodologije. |

### Otvorene stavke za predaju

- **Odabrati prije javne objave:** projektni kod nema licencu. Licence
  korištenih biblioteka ne određuju licencu ovog projekta.
- **Nije implementirano:** napredna tehnologija poput AI-ja/IoT-a; klasifikacija
  oglasa temelji se na determinističkim pravilima.
- **Nije implementirano:** aplikacija nema API ni izravno povezivanje s javnim
  sustavima; integracijski potencijal i potrebni preduvjeti opisani su u
  dokumentaciji.
- **Pripremiti za prijavu:** javni poziv traži video-prezentaciju u trajanju od
  tri minute.
- **Provjera izvora 09.11.2026.:** katalog otvorenih podataka MUP-a sadrži 41
  mjesečni izvještaj od travnja 2023. do kolovoza 2026.; kasniji izvještaji nisu
  navedeni u katalogu. Ponovno provjeriti MUP i katalog neposredno prije predaje.
- **DZS regionalna procjena:** identificirana je izravna PxWeb API tablica
  SP22_2; zadnja dostupna godina je 2024. Novija procjena nije pronađena u toj
  tablici.
- **HZZ i DZS svježina:** HZZ RSS provjeren 09.11.2026. ima najnoviji datum
  objave 06.11.2026. i isti sadržaj oglasa kao lokalni izvadak. DZS-ova
  nacionalna radna knjiga jednaka je aktualnoj datoteci na izvoru te završava
  rujnom 2026.

U snapshotu HZZ-a nalazi se 5.920 oglasa; 5.373 (90,8 %) imaju prepoznatu
kategoriju, dok 547 ostaje „Nerazvrstano”. Konzervativna pravila naslova
povećala su udio razvrstanih oglasa s 84,7 % na 90,8 %. Prikaz zadržava izvorni
naslov, izvornu kategoriju i izvor klasifikacije kako bi se rezultat mogao
provjeriti. Ovaj udio opisuje spremljeni izvadak i mijenjat će se s novim
HZZ podacima.

Regionalni prikazi odvajaju HZZ oglase od MUP-ovih dozvola. Zanimanja se
uspoređuju među regijama prema oglasima, a MUP-ove dozvole prikazuju se kao
zaseban kontekst; projekt ne izračunava kompozitni indeks pritiska ili manjka
radnika.

## Tehnička arhitektura i integracijski potencijal

- Višestranično sučelje izrađeno je u Streamlitu; Pandas obrađuje tablice,
  Plotly prikazuje grafikone, a XLSX izvoz izrađuje se pomoću openpyxl.
- Uvoz je lokalni i ponovljiv: HZZ XML/RSS, DZS CSV/XLSX i MUP XLSX datoteke
  čitaju se iz projektnih direktorija. Nema baze podataka ni automatskog
  dohvaćanja izvora tijekom rada aplikacije.
- Obrada čisti nazive regija, spaja Zagreb prema obuhvatu MUP-a, uklanja
  ponovljene HZZ oglase i izračunava pokazatelje po stanovniku. Rezultati se
  prikazuju u pregledniku i izvoze u XLSX.
- Za povezivanje s drugim sustavima potrebni su stabilni identifikatori
  prostornih jedinica, dokumentirani metapodaci i verzije skupova, dogovoreni
  formati razmjene (npr. CSV/JSON) te redovito ažuriranje i validacija izvora.
- U ovoj verziji nema AI-ja, IoT-a ni blockchaina; kategorije se obrađuju
  determinističkim pravilima, a ne modelom umjetne inteligencije. Korištene
  programske biblioteke su otvorenog koda, ali repozitorij još nema zasebnu
  licencu za sam projektni kod.

## Ključna pitanja

1. U kojim se regijama trenutno objavljuje najviše HZZ oglasa?
2. Koja se zanimanja oglašavaju u Hrvatskoj i kako se njihov broj razlikuje po regijama?
3. Koje djelatnosti imaju najviše izdanih MUP-ovih dozvola?
4. Kako se broj HZZ oglasa po zanimanju i regiji mijenja kada se prikaže na 1.000 stanovnika?
5. Kako se u dostupnoj DZS seriji kreću zaposlenost i nezaposlenost?

## Korišteni podaci

Podaci su preuzeti 09.11.2026. i spremljeni u `data/`, `dozvole/` i
`stanovništvo/`. Budući da su izvori podložni izmjenama, datum preuzimanja je
sastavni dio rezultata.

| Izvor | Uloga | Ponovno preuzimanje |
|---|---|---|
| HZZ RSS po županijama | oglasi po regionalnoj jedinici | [RSS katalog](http://burzarada.hzz.hr/rss/rsszup{broj}.xml) |
| HZZ RSS po zanimanju | skupine zanimanja | [Katalog HZZ-a](https://data.gov.hr/ckan/dataset/slobodna-radna-mjesta-po-zanimanju) |
| MUP | izdane dozvole i djelatnosti | [Skup podataka MUP-a na Portalu otvorenih podataka](https://data.gov.hr/ckan/dataset/statisticki-podaci-izdanih-dozvola-za-boravak-i-rad-u-travnju-2023-godine); 41 mjesečni izvještaj, travanj 2023. – kolovoz 2026. |
| DZS | stanovništvo po županijama | Lokalni CSV izvadak „Procjena stanovništva prema dobnim skupinama i spolu, po županijama, 31.12.”; [izravna PxWeb API tablica SP22_2](https://web.dzs.hr/PXWeb/api/v1/hr/Stanovni%C5%A1tvo/Procjene%20stanovni%C5%A1tva/SP22_2.px); zadnja godina 2024. |
| DZS | zaposlenost, nezaposlenost i aktivno stanovništvo | [Administrativni izvori, tablica 9.2.3.](https://podaci.dzs.hr/media/4snl4v1e/zaposlenost-administrativni-izvori.xlsx); privremeni podaci do rujna 2026. |

Detaljan popis poveznica nalazi se u [`data/SOURCES.txt`](data/SOURCES.txt).

### Kratki rječnik

- **RSS** je format u kojem HZZ objavljuje strojno čitljiv popis trenutno
  dostupnih oglasa.
- **Oglas** je objava na HZZ-u; ne mora značiti jedno slobodno radno mjesto
  jer može obuhvatiti više radnika ili biti ponovno objavljen.
- **Stopa na 1.000 stanovnika** omogućuje usporedbu regija različite veličine.
  Broj stanovnika je nazivnik, odnosno vrijednost prema kojoj se broj oglasa
  ili dozvola preračunava.
- **HZZ oglasi na 1.000 stanovnika** prikazuju broj oglasa u odnosu na broj
  stanovnika. To je omjer objava, ne broj slobodnih radnih mjesta po radniku.
- **Kumulativna vrijednost** zbraja dozvole evidentirane od početka godine do
  datuma MUP-ova izvještaja.
- **Snapshot** je lokalno spremljeni izvadak izvora u trenutku preuzimanja.

## Metodologija

### Regionalna usporedba

HZZ oglasi se grupiraju prema regiji i prepoznatoj skupini zanimanja. Aplikacija
prikazuje ili broj oglasa ili broj oglasa na 1.000 stanovnika. MUP-ove izdane
dozvole i njihova stopa po stanovniku ostaju zasebni pokazatelji i ne ulaze u
izračun HZZ vrijednosti. Nema kompozitnog indeksa koji miješa oglase i dozvole.

Za izračun indeksa ponude i potražnje potrebni su vremenski i prostorno
usporedivi podaci o slobodnim radnim mjestima i nezaposlenim osobama. Oglas
može obuhvatiti više radnika ili biti ponovno objavljen, a dostupna DZS serija
radne snage u ovom projektu nije regionalno usporediva s HZZ oglasima. Zato
aplikacija takav indeks ne izračunava.

### Usporedba zanimanja i djelatnosti

HZZ oglasi se prvo razvrstavaju prema kategoriji iz opisa oglasa, a kod
nedostajuće ili nepotpune kategorije koristi se povezani HZZ RSS po zanimanju.
Nepotpune oznake usklađuju se s potpunijim oznakama iz istog izvatka. Za
nedvosmislene nazive „doktor/doktorica medicine” (ne veterinarske medicine) i
„keramičar/keramičarka” primjenjuje se izričito pravilo normalizacije.
Ako kategorija i dalje nedostaje, mali skup pravila naslova povezuje jasne
nazive kuhar/konobar/čistač sa skupinom jednostavnih prodajnih i uslužnih
zanimanja, instalaterska i električarska zanimanja s građevinskom skupinom,
osobnog asistenta sa zdravstvom i socijalnom skrbi te izričita radna mjesta u
proizvodnji s proizvodnom skupinom. Ta pravila ne pokušavaju zaključiti
kvalifikaciju iz naziva; višeznačni ili općeniti nazivi ostaju nerazvrstani.
Pojedinačni oglas prikazuje i izvorni naziv/kategoriju i primijenjenu kategoriju
kako bi se ispravak mogao provjeriti. Oglasi bez pouzdane klasifikacije ostaju
„Nerazvrstano”.

MUP-ove dozvole prikazuju se prema MUP-ovim djelatnostima. HZZ zanimanja i MUP
djelatnosti ostaju odvojene klasifikacije jer nisu izravno usporedive.

### Interakcije

Korisnik može:

- odabrati regiju,
- usporediti dvije regije,
- pretražiti skupinu zanimanja ili pojedinačni naziv HZZ oglasa,
- provjeriti izvor i primijenjeno pravilo kategorije za pojedinačni oglas,
- odabrati skupine zanimanja i usporediti njihove HZZ oglase po regiji,
  kao apsolutni broj ili na 1.000 stanovnika,
- filtrirati MUP-ovu i nacionalnu DZS seriju po godini na sažetku,
- odabrati broj zanimanja na grafikonu,
- preuzeti prikazane tablice u XLSX formatu.

## Ograničenja

- HZZ RSS predstavlja trenutno dostupne oglase, a ne nužno broj stvarnih radnih mjesta.
- Jedan oglas može obuhvatiti više radnika, a isti oglas može biti objavljen više puta.
- HZZ kategorije mogu nedostajati ili biti skraćene; naziv oglasa i izvorna
  kategorija ostaju vidljivi uz normaliziranu kategoriju. Pravila iz naslova
  primjenjuju se samo na jasno prepoznate nazive, ne na sve nepoznate oglase.
- MUP-ove dozvole su izdane dozvole, a ne broj trenutačno zaposlenih stranih radnika.
- MUP-ovi mjesečni izvještaji sadrže kumulativne vrijednosti do datuma izvještaja.
- U priloženom izvatku ima 41 MUP izvještaj od travnja 2023. do kolovoza 2026.;
  kasniji izvještaji nisu uključeni u snapshot ove verzije; prije predaje
  provjeriti službeni izvor za novije objave.
- MUP ne daje istu regionalnu razinu za Grad Zagreb i Zagrebačku županiju, pa su spojeni.
- HZZ zanimanja i MUP djelatnosti nisu izravno usporedive klasifikacije.
- DZS procjena stanovništva za regionalne stope odnosi se na 2024. godinu.
- Regionalni nazivnik u ovoj verziji koristi procjenu stanovništva za 2024.;
  novija godina nije dostupna u DZS PxWeb tablici SP22_2 provjerenoj 09.11.2026.
- U spremljenom HZZ izvatku 547 od 5.920 oglasa (9,2 %) nema pouzdano
  prepoznatu kategoriju; njihova klasifikacija nije uključena u agregate
  zanimanja, ali se oglasi mogu pregledati u tablici pojedinačnih oglasa.
- DZS nacionalna serija aktivnog stanovništva je privremena; u izvatku obuhvaća
  listopad 2024. – rujan 2026. i nije regionalno usporediva s HZZ oglasima.
- Dostupni izvori imaju različite datume i vremenske obuhvate.
- Oglas nije nužno jedno slobodno radno mjesto, a MUP-ova dozvola nije dokaz
  trenutačnog zaposlenja. Dostupni regionalni podaci ne omogućuju izračun
  usporedivog omjera slobodnih radnih mjesta i nezaposlenih osoba.
- Aplikacija radi nad lokalnim snapshotima, nema automatsko osvježavanje niti
  jamči da su lokalne datoteke najnovije objave izvora.

Ograničenja su namjerno prikazana na stranici **Podaci i metodologija** kako bi
korisnik mogao pravilno tumačiti rezultate i razlikovati opisni pokazatelj od
službene statistike.

## Budući razvoj

- Automatizirati sigurno preuzimanje i verzioniranje izvora te ažurirati MUP-ove
  izvještaje nakon njihove objave.
- Nabaviti novije regionalne procjene stanovništva ili objasniti i ujednačiti
  vremenski obuhvat nazivnika u regionalnim stopama.
- Prije eventualnog indeksa ponude i potražnje pronaći vremenski i prostorno
  usporedive podatke o slobodnim radnim mjestima i nezaposlenima; MUP-ove
  dozvole ostaviti zasebnim pokazateljem.
- Proširiti nadzor kvalitete HZZ kategorija i provjeravati pravila normalizacije
  na uzorcima oglasa uz čuvanje izvornih podataka.
- Uvesti automatizirane provjere formata, potpunosti, duplikata i promjena izvora.
- Objaviti projekt pod odabranom otvorenom licencom te pripremiti dokumentirano
  strojno čitljivo sučelje za moguću integraciju.
- Pripremiti obaveznu video-prezentaciju u trajanju od tri minute o problemu,
  korisnicima, izvorima, funkcionalnosti, arhitekturi i koristi za zajednicu.

## Transparentnost i AI

AI je korišten kao pomoć pri analizi potreba projekta, oblikovanju metodologije,
izradi i provjeri programskog koda te pisanju dokumentacije. Izbor izvora,
tumačenje ograničenja i konačna odgovornost za projekt ostaju na autorici.

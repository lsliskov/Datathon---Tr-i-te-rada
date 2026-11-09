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
| Inovativnost i primjena tehnologije | Više heterogenih izvora pretvoreno je u jednu interaktivnu regionalnu analizu s pretragom i usporedbom regija. |
| Izvedivost i integracijski potencijal | Projekt je reproducibilan iz lokalno spremljenih izvadaka, koristi jednostavan Streamlit/Pandas sloj i jasno odvaja učitavanje podataka od prikaza. |
| Prezentacija | Aplikacija vodi korisnika od sažetka preko regionalne usporedbe do zanimanja, djelatnosti i metodologije. |

Projekt ne tvrdi da jedan kompozitni broj sam po sebi dokazuje manjak radnika.
Relativni regionalni pokazatelj služi kao početni alat za usporedbu, dok se
zaključci čitaju zajedno s izvornim brojevima, stopama i kontekstom.

## Ključna pitanja

1. U kojim se regijama trenutno objavljuje najviše HZZ oglasa?
2. Koja su zanimanja najtraženija u Hrvatskoj i u pojedinoj regiji?
3. Koje djelatnosti imaju najviše izdanih MUP-ovih dozvola?
4. Kako se regionalne vrijednosti razlikuju kada se prilagode broju stanovnika?
5. Kako se u dostupnoj DZS seriji kreću zaposlenost i nezaposlenost?

## Korišteni podaci

Podaci su preuzeti 09.11.2026. i spremljeni u `data/`, `dozvole/` i
`stanovništvo/`. Budući da su izvori podložni izmjenama, datum preuzimanja je
sastavni dio rezultata.

| Izvor | Uloga | Ponovno preuzimanje |
|---|---|---|
| HZZ RSS po županijama | oglasi po regionalnoj jedinici | [RSS katalog](http://burzarada.hzz.hr/rss/rsszup{broj}.xml) |
| HZZ RSS po zanimanju | skupine zanimanja | [Katalog HZZ-a](https://data.gov.hr/ckan/dataset/slobodna-radna-mjesta-po-zanimanju) |
| MUP | izdane dozvole i djelatnosti | [MUP statistika](https://mup.gov.hr/statistika/281716) |
| DZS | stanovništvo | [Procjene stanovništva](https://podaci.dzs.hr/media/vb1ae2vm/procjene-stanovnistva.xlsx) |
| DZS | zaposlenost, nezaposlenost i aktivno stanovništvo | [Administrativni izvori](https://podaci.dzs.hr/media/4snl4v1e/zaposlenost-administrativni-izvori.xlsx) |

Detaljan popis poveznica nalazi se u [`data/SOURCES.txt`](data/SOURCES.txt).

### Kratki rječnik

- **RSS** je format u kojem HZZ objavljuje strojno čitljiv popis trenutno
  dostupnih oglasa.
- **Oglas** je objava na HZZ-u; ne mora značiti jedno slobodno radno mjesto
  jer može obuhvatiti više radnika ili biti ponovno objavljen.
- **Stopa na 1.000 stanovnika** omogućuje usporedbu regija različite veličine.
  Broj stanovnika je nazivnik, odnosno vrijednost prema kojoj se broj oglasa
  ili dozvola preračunava.
- **Min–max normalizacija** pretvara vrijednosti u zajednički raspon 0–100.
- **Relativni pokazatelj** je prosjek normalizirane stope oglasa i normalizirane
  stope dozvola. On služi za usporedbu prikazanih regija, a nije službena
  stopa manjka radnika.
- **Kumulativna vrijednost** zbraja dozvole evidentirane od početka godine do
  datuma MUP-ova izvještaja.
- **Snapshot** je lokalno spremljeni izvadak izvora u trenutku preuzimanja.

## Metodologija

### Regionalni pokazatelj

Za svaku usporedivu regionalnu jedinicu računaju se:

- HZZ oglasi / stanovništvo × 1.000,
- MUP-ove izdane dozvole / stanovništvo × 1.000.

Obje stope se min–max normaliziraju na raspon 0–100 unutar prikazanih regija,
a njihov aritmetički prosjek daje relativni pokazatelj. Pokazatelj je deskriptivan
i ne predstavlja službenu stopu manjka radnika.

### Usporedba zanimanja i djelatnosti

HZZ oglasi grupiraju se prema HZZ-ovim skupinama zanimanja. MUP-ove dozvole
prikazuju se prema MUP-ovim djelatnostima. Klasifikacije se ne spajaju umjetno:
prikazuju se usporedno kako bi svaka zadržala izvorno značenje.

### Interakcije

Korisnik može:

- odabrati regiju,
- usporediti dvije regije,
- pretražiti skupinu zanimanja,
- odabrati broj zanimanja na grafikonu,
- preuzeti prikazane tablice u XLSX formatu.

## Ograničenja

- HZZ RSS predstavlja trenutno dostupne oglase, a ne nužno broj stvarnih radnih mjesta.
- Jedan oglas može obuhvatiti više radnika, a isti oglas može biti objavljen više puta.
- MUP-ove dozvole su izdane dozvole, a ne broj trenutačno zaposlenih stranih radnika.
- MUP-ovi mjesečni izvještaji sadrže kumulativne vrijednosti do datuma izvještaja.
- MUP ne daje istu regionalnu razinu za Grad Zagreb i Zagrebačku županiju, pa su spojeni.
- HZZ zanimanja i MUP djelatnosti nisu izravno usporedive klasifikacije.
- DZS radna snaga u ovoj verziji daje nacionalni vremenski kontekst; nije potpuno
  ujednačena regionalna mjesečna tablica s HZZ oglasima.
- Dostupni izvori imaju različite datume i vremenske obuhvate.
- Relativni pokazatelj ovisi o regijama uključenima u izračun i ekstremnim vrijednostima.

Ograničenja su namjerno prikazana na stranici **Podaci i metodologija** kako bi
korisnik mogao pravilno tumačiti rezultate i razlikovati opisni pokazatelj od
službene statistike.

## Transparentnost i AI

AI je korišten kao pomoć pri analizi potreba projekta, oblikovanju metodologije,
izradi i provjeri programskog koda te pisanju dokumentacije. Izbor izvora,
tumačenje ograničenja i konačna odgovornost za projekt ostaju na autorici.

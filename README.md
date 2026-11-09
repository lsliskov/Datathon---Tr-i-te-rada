# LabourPulse RH

Streamlit aplikacija za razumljiv pregled potražnje za radnicima, regionalnih
razlika i promjena u strukturi tržišta rada u Hrvatskoj.

## Pokretanje

Potrebni su Python 3.10 ili noviji.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Izvorne datoteke nalaze se u direktorijima `data/dzs`, `data/hzz_zupanije`,
`data/hzz_zanimanja`, `dozvole` i `stanovništvo`. Aplikacija koristi HZZ RSS XML,
MUP Excel izvještaje te DZS CSV i Excel podatke. Učitavanje je predmemorirano
Streamlitovim cacheom.

Početna stranica **Sažetak** nudi odvojene filtre za godine MUP izvještaja i
nacionalne DZS serije. HZZ RSS izvadak ne sadrži povijesnu arhivu za usporedbu
godina. Na stranici **Zanimanja i djelatnosti**
pretraga obuhvaća i naziv oglasa; pojedinačni naslov, izvornu HZZ kategoriju i
primijenjeno pravilo moguće je provjeriti u tablici oglasa.

## Pokazatelji i dokumentacija

Stranica **Zanimanja po regijama** uspoređuje HZZ oglase po skupinama zanimanja
među regijama, kao apsolutni broj ili na 1.000 stanovnika. MUP-ove izdane
dozvole prikazuju se odvojeno kao zaseban kontekst; ne spajaju se s oglasima u
zajednički indeks. Aplikacija također prikazuje djelatnosti iz MUP-ovih podataka
i nacionalni DZS kontekst radne snage.

MUP objavljuje podatke za Zagrebačku policijsku upravu bez odvojenog iznosa za
Grad Zagreb. Zbog toga se Grad Zagreb i Zagrebačka županija objedinjuju u
regionalnoj analizi. Karta koristi približne točke središta regija.

DZS tablica zaposlenosti i nezaposlenosti dodaje nacionalni vremenski kontekst.
Metodologija, izvori i kvaliteta podataka dostupni su na stranici **Podaci i
metodologija**. Tablice se mogu preuzeti u XLSX formatu.

Detaljna projektna dokumentacija, metodologija, ograničenja, izvori i
transparentna napomena o korištenju AI-ja nalaze se u
[PROJECT.md](PROJECT.md). Poveznice i datum preuzimanja nalaze se u
[data/SOURCES.txt](data/SOURCES.txt).

Projekt je strukturiran prema kriterijima javnog poziva: korištenje otvorenih
podataka, relevantnost za gospodarstvo i upravljanje, korist za zajednicu,
inovativna primjena tehnologije, izvedivost i integracijski potencijal te jasna
prezentacija. Mapiranje kriterija nalazi se u [PROJECT.md](PROJECT.md).

## Provjere

Pokrenite testove obrade podataka i prikaza svih stranica:

```powershell
python -m unittest discover -s tests -v
```

## Status za predaju

- Prototip pokriva izazov **Gospodarstvo i učinkovito upravljanje**.
- U spremljenom HZZ izvatku ima 5.920 oglasa; 5.373 (90,8 %) imaju prepoznatu
  kategoriju, a 547 ostaje nerazvrstano nakon konzervativnih pravila za jasne
  nazive zanimanja. Klasifikacija je dostupna za provjeru uz pojedinačne oglase.
- Provjera izvora 09.11.2026.: katalog otvorenih podataka MUP-a sadrži 41
  izvještaj od travnja 2023. do kolovoza 2026.; u katalogu nema kasnijih
  mjesečnih izvještaja. DZS API tablica regionalne procjene završava 2024.
  godinom. Ponovno provjeriti izvore neposredno prije predaje.
- HZZ RSS provjeren istog dana: najnoviji datum objave je 06.11.2026. i sadržaj
  oglasa odgovara lokalnom izvatku. DZS-ova nacionalna radna knjiga također je
  jednaka aktualnoj datoteci na izvoru, s podacima do rujna 2026.
- Javni poziv traži video-prezentaciju u trajanju od tri minute; video nije dio
  ovog projekta.
- Projektni kod nema odabranu licencu. Licence korištenih biblioteka ne
  određuju licencu ovog projekta.

Detaljni tehnički i metodološki status te ograničenja navedeni su u
[PROJECT.md](PROJECT.md).

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

Početna stranica **Zanimanja po regijama** stavlja usporedbu zanimanja u prvi
plan. HZZ RSS izvadak ne sadrži povijesnu arhivu za usporedbu godina. Na stranici
**Zanimanja i djelatnosti**
pretraga obuhvaća i naziv oglasa; pojedinačni naslov, izvornu HZZ kategoriju i
primijenjeno pravilo moguće je provjeriti u tablici oglasa.

## Pokazatelji i dokumentacija

Stranica **Zanimanja po regijama** uspoređuje HZZ oglase po skupinama zanimanja
među regijama, kao apsolutni broj, na 1.000 stanovnika ili na 1.000 stanovnika
u dobi 15–64. Prikazuje se i demografski pregled udjela stanovništva 15–64 i
65+ po regijama. MUP-ove izdane dozvole prikazuju se odvojeno kao dodatni
kontekst; ne spajaju se s oglasima u zajednički indeks.

Rezultati opisuju spremljene izvatke, ne nužno cijelo tržište rada. Oglasi nisu
isto što i slobodna radna mjesta, ponovne objave s drugim identifikatorom mogu
ostati zasebne, a pravila za razvrstavanje naslova nisu neovisno validirana.
Udio oglasa bez pouzdane kategorije i druga ograničenja navedeni su u
[PROJECT.md](PROJECT.md) i na stranici **Podaci i metodologija**.

MUP objavljuje podatke za Zagrebačku policijsku upravu bez odvojenog iznosa za
Grad Zagreb. Zbog toga se Grad Zagreb i Zagrebačka županija objedinjuju u
regionalnoj analizi. Karta koristi približne točke središta regija.

DZS tablica zaposlenosti i nezaposlenosti dodaje nacionalni vremenski kontekst.
Demografski nazivnik odnosi se na 2024., dok su oglasi noviji. Dobna skupina
15–64 nije isto što i aktivna radna snaga.
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

Detaljni opis projekta, metodologija, izvori i ograničenja navedeni su u
[PROJECT.md](PROJECT.md).

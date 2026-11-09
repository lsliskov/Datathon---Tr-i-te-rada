# LabourPulse RH

Streamlit aplikacija za razumljiv pregled potražnje za radnicima, regionalnih
razlika i promjena u strukturi tržišta rada u Hrvatskoj.

## Pokretanje

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Izvorne datoteke nalaze se u direktorijima `data/dzs`, `data/hzz_zupanije`,
`data/hzz_zanimanja`, `dozvole` i `stanovništvo`. Aplikacija koristi HZZ RSS XML,
MUP Excel izvještaje i DZS Excel podatke. Čitanje podataka predmemorirano je
tijekom sesije.

## Pokazatelji i dokumentacija

Regionalni pokazatelj potražnje računa HZZ oglase i MUP-ove izdane dozvole na
1.000 stanovnika te svaku stopu min–max normalizacijom pretvara u raspon 0–100.
Pokazatelj je prosjek dviju ocjena i služi za brzo uspoređivanje prikazanih regija.
Stranice aplikacije zasebno prikazuju oglase, zanimanja, djelatnosti, dozvole i
nacionalni DZS kontekst radne snage.

MUP objavljuje podatke za Zagrebačku policijsku upravu bez odvojenog iznosa za
Grad Zagreb. Zbog toga se Grad Zagreb i Zagrebačka županija objedinjuju u
regionalnoj analizi i pokazatelju. Karta koristi približne točke središta regija.

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

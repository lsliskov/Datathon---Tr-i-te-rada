# LabourPulse RH

Streamlit aplikacija za usporedni pregled HZZ oglasa, MUP-ovih dozvola i DZS-ova
stanovništva po regijama.

## Pokretanje

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Izvorne datoteke ostaju u direktorijima `poslovi po županijama`, `dozvole` i
`stanovništvo`. Aplikacija koristi HZZ RSS XML, MUP Excel izvještaje te CSV
procjene stanovništva. Čitanje podataka predmemorirano je tijekom sesije.

## Pokazatelj i ograničenja

Regionalni indeks pritiska jednak je prosjeku min–max normaliziranih stopa
HZZ oglasa i MUP-ovih izdanih dozvola na 1.000 stanovnika. Riječ je o
usporednom pokazatelju aplikacije, a ne službenoj statistici. HZZ broji oglase,
ne broj radnih mjesta; MUP-ove dozvole nisu broj trenutačno zaposlenih stranih
radnika. MUP-ova razrada po djelatnosti dostupna je samo za Hrvatsku ukupno.
Skupine zanimanja HZZ-a i djelatnosti MUP-a prikazuju se odvojeno jer nemaju
izravno usporedivu klasifikaciju.

MUP objavljuje podatke za Zagrebačku policijsku upravu bez odvojenog iznosa za
Grad Zagreb. Zbog toga se Grad Zagreb i Zagrebačka županija objedinjuju u
regionalnoj analizi i indeksu. Karta prikazuje približne točke središta regija,
ne službene granice županija.

Za indeks se koristi najnovija dostupna procjena ukupnog stanovništva iz DZS
datoteke, a ne radno sposobno stanovništvo. MUP-ovi mjesečni izvještaji
predstavljaju zbroj dozvola evidentiranih do datuma izvještaja; vrijednosti se
početkom godine ponovno akumuliraju od početka godine.

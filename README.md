# Order service

FastAPI servis: `POST /order` pretvara tekst narudžbe u JSON sa stavkama s jelovnika (`menu.json`) pomoću Gemini modela.

## Pokretanje

Potreban je besplatan API ključ iz [Google AI Studija](https://aistudio.google.com/apikey). Ključ se čita iz varijable okruženja, nije u kodu.

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY = "tvoj-kljuc"
python -m uvicorn main:app
```

```bash
# Linux / macOS
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="tvoj-kljuc"
python -m uvicorn main:app
```

Servis radi na `http://localhost:8000`. Za isprobavanje otvori `http://localhost:8000/docs`, klikni na "POST /order", zatim na "Try it out", upiši tekst narudžbe i klikni "Execute". Zadani model je `gemini-3.1-flash-lite`, a mijenja se varijablom okruženja `GEMINI_MODEL`.


Dok server radi, u drugom terminalu možete pokrenuti skriptu `test_order.py`:

```bash
python test_order.py
```

Skripta provjerava točnost zadanih primjera i nekoliko dodatnih.

Primjer: `{"text": "dva hamburgera, dvije margarite i jednu colu"}` vraća `items` (margarita × 2, coca_cola × 1), `unavailable` (hamburger × 2) i `prijedlog` (prazna lista).

**Proširenje formata:** polje `prijedlog` je lista `id`-eva s jelovnika kad gost ne naručuje nego pita (npr. „imate li nešto bez mesa?”). Narudžba tada ostaje prazna, a sustav ne sastavlja narudžbu umjesto gosta.

## Što bi se dalo poboljšati i kako provjeriti

Sustav bi se mogao poboljsati dodatnom sanitizacijom i blokiranjem odredenih input-a 
tako da netko ne bi mogao poslati bilo sto LLM-u i tako preopteretiti sustav,
kao recimo blokiranje pitanja koje nemaju veze s hranom i jelovnikom
ili poboljsano razlikovanje izmedu hrane i stvari.
Dodavanje mogucnosti da LLM postavi podpitanje kako bi rjesio nejasnoce,
time bi smanjili odgovore koji nisu smisleni, ali bi bio veci trosak resursa zbog dodatnih requestova modelu.

Sustav se moze provjeriti skriptama poput test_order.py ,
s time da bi trebalo prosiriti broj primjera za bolju pokrivenost.
Ako je moguce nabaviti stvarne primjere narudzbi u restoranu,
a ne samo izmisljenje. U prirodnom govoru ljudi znaju grijesiti, krivo izgovarati i koristiti
krive rijeci te bi mogli testirati modelovu sposobnost hvatanja konteksta.
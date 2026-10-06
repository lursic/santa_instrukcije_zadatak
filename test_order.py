"""Pokretanje (server mora već raditi: python -m uvicorn main:app):
    python test_order.py                          (testira http://localhost:8000)
    python test_order.py http://localhost:9000    (drugi URL)

Šalje niz rečenica servisu i uspoređuje rezultat s očekivanim.
Pozivi idu pravom Gemini modelu, pa rezultati mogu povremeno varirati.
"""
import json
import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
PAUZA = 4  # sekundi između poziva, zbog ograničenja besplatne kvote

# "items": {id: količina} | "unavailable": {tekst: količina} | "prijedlog": {id, ...}
# Ključ koji nije naveden se ne provjerava.
TESTOVI = [
    # --- primjeri iz zadatka ---
    ("dvije margarite i jednu colu",
     {"items": {"margarita": 2, "coca_cola": 1}, "unavailable": {}, "prijedlog": set()}),
    ("jednu kapričozu i dva piva molim",
     {"items": {"capricciosa": 1, "pivo": 2}, "unavailable": {}}),
    ("dva hamburgera i jednu margaritu",
     {"items": {"margarita": 1}, "unavailable": {"hamburger": 2}}),
    ("imate li nešto bez mesa za nas dvoje?",
     {"items": {}, "unavailable": {},
      "prijedlog": {"margarita", "vegetariana", "quattro_formaggi", "mijesana_salata"}}),
    ("tri margarite i colu, ma ne, ipak dvije margarite",
     {"items": {"margarita": 2, "coca_cola": 1}}),
    # --- dodatni slučajevi ---
    ("jednu colu, dvije margarite i još jednu colu",
     {"items": {"coca_cola": 2, "margarita": 2}}),
    ("tri margarite i colu, ma ne, ipak dvije margarite. Ipak još dvije cole mi dajte",
     {"items": {"margarita": 2, "coca_cola": 3}}),
    ("jednu pizzu",
     {"items": {}, "unavailable": {"pizza": 1}}),
    ("dva hamburgera",
     {"items": {}, "unavailable": {"hamburger": 2}}),
    ("koja pića imate?",
     {"items": {}, "prijedlog": {"coca_cola", "mineralna_voda", "pivo"}}),
    ("dvije margarite i koja su pića?",
     {"items": {"margarita": 2}, "prijedlog": {"coca_cola", "mineralna_voda", "pivo"}}),
        ("asdf qwer",
     {"items": {}, "unavailable": {}, "prijedlog": set()}),
    ("   ",
     {"items": {}, "unavailable": {}, "prijedlog": set()}),
]


def provjeri(odgovor: dict, ocekivano: dict) -> list[str]:
    greske = []
    if "items" in ocekivano:
        dobiveno = {i["id"]: i["quantity"] for i in odgovor["items"]}
        if dobiveno != ocekivano["items"]:
            greske.append(f"items: očekivano {ocekivano['items']}, dobiveno {dobiveno}")
    if "unavailable" in ocekivano:
        # tekst se uspoređuje labavo (npr. "hamburger" unutar "hamburgeri")
        dobiveno = {u["text"].lower(): u["quantity"] for u in odgovor["unavailable"]}
        for tekst, kol in ocekivano["unavailable"].items():
            if not any(tekst in k and q == kol for k, q in dobiveno.items()):
                greske.append(f"unavailable: nedostaje '{tekst}' x{kol}, dobiveno {dobiveno}")
        if not ocekivano["unavailable"] and dobiveno:
            greske.append(f"unavailable: očekivano prazno, dobiveno {dobiveno}")
    if "prijedlog" in ocekivano:
        dobiveno = {p["id"] for p in odgovor["prijedlog"]}
        if dobiveno != ocekivano["prijedlog"]:
            greske.append(f"prijedlog: očekivano {sorted(ocekivano['prijedlog'])}, dobiveno {sorted(dobiveno)}")
    return greske


def main_test() -> int:
    client = httpx.Client(base_url=URL, timeout=60)
    try:
        client.get("/docs")
    except httpx.ConnectError:
        print(f"Ne mogu se spojiti na {URL}. Pokreni prvo server: python -m uvicorn main:app")
        return 1
    print(f"Testiram servis na {URL}\n")
    palo = 0
    for n, (tekst, ocekivano) in enumerate(TESTOVI):
        if n:
            time.sleep(PAUZA)
        print("=" * 70)
        print(f"POSLANO:  {json.dumps({'text': tekst}, ensure_ascii=False)}")
        r = client.post("/order", json={"text": tekst})
        if r.status_code != 200:
            print(f"DOBIVENO: HTTP {r.status_code}: {r.text}")
            print("REZULTAT: [PAO]")
            palo += 1
            continue
        odgovor = r.json()
        print(f"DOBIVENO: {json.dumps(odgovor, ensure_ascii=False, indent=2)}")
        greske = provjeri(odgovor, ocekivano)
        if greske:
            palo += 1
            print("REZULTAT: [PAO]")
            for g in greske:
                print(f"          {g}")
        else:
            print("REZULTAT: [OK]")
    print("=" * 70)
    print(f"Prošlo {len(TESTOVI) - palo}/{len(TESTOVI)}")
    return 1 if palo else 0


if __name__ == "__main__":
    sys.exit(main_test())
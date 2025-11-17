# Password Service Technical Design

## 1. Overzicht

Deze architectuur beschrijft een schaalbare wachtwoordmodule gebouwd met **Python 3.12**, **FastAPI**, **Pydantic**, **SQLModel/SQLite** (optioneel), en volledig asynchrone request-afhandeling. Het doel is het leveren van validatie, generatie, sterkte-analyse en een REST-interface, met uitbreidbaarheid richting logging, analytics en security policies.

## 2. Architecturale doelen
- **Modulariteit:** iedere domeinfunctie in eigen module (validator, generator, scoring).
- **Security-first:** cryptografisch sterke randomisatie, centrale policy-configuratie.
- **Async performance:** FastAPI routers en services werken async, geen blocking I/O.
- **Testbaarheid:** pure functies voor logica, services orchestreren afhankelijkheden.
- **Extensibiliteit:** duidelijke uitbreidingspunten (rate limiting, API keys, auditlog).

## 3. Directory-structuur
```
app/
├── main.py                # FastAPI-initialisatie en CLI entrypoint
├── core/
│   ├── config.py          # Settings, policy-constanten, lazy env-config
│   ├── security.py        # Character sets, entropy utilities, secrets wrappers
│   ├── generator.py       # Pure password generatie helpers
│   ├── validator.py       # Validatieregels + orchestrator
│   └── scoring.py         # Entropie en score berekeningen
├── routers/
│   └── password.py        # Alle REST-routes voor validate/generate/strength/full
├── models/
│   ├── request_schemas.py # Pydantic-modellen voor inkomende payloads
│   └── response_schemas.py# Pydantic-modellen voor API-outputs
├── services/
│   └── password_service.py# Business flows die core-modules aanroepen
├── db/ (optioneel)
│   └── session.py         # SQLModel engine/session + logging tabeldefinities
└── utils/ (optioneel)
    └── logging.py         # Async logging helper voor toekomstige auditlogs
```

## 4. Core modules

### 4.1 config.py
- Gebruikt `pydantic_settings.BaseSettings` voor runtime-config (min/max lengtes, standaard generatie-lengte, symbolensets).
- Voorbeeldvelden:
  - `MIN_LENGTH: ClassVar[int] = 8`
  - `MAX_LENGTH: ClassVar[int] = 128`
  - `DEFAULT_GENERATE_LENGTH: int = 16`
  - `SYMBOLS: str = "!@#$%^&*()-_=+[]{};:,.?/"`
- Functie `get_settings()` retourneert singleton-config via lru_cache.

### 4.2 security.py
- Definieert karaktersets: `UPPERS`, `LOWERS`, `DIGITS`, `SYMBOLS`.
- Combineert tot `FULLSET`.
- Bevat helper `secure_choice(seq)` en `secure_shuffle(chars: list[str])` met `secrets.SystemRandom`.
- Eventuele hashing of toekomstige bcrypt logica hier centraliseren.

### 4.3 generator.py
- Functie `generate_password(length: int, settings: Settings) -> str`:
  1. Valideert lengte binnen MIN/MAX.
  2. Zorgt voor minimaal één char per categorie.
  3. Gebruikt `secrets.choice` voor resterende karakters uit FULLSET.
  4. Shuffle met `secure_shuffle`.
- Optionele helper `generate_batch(count, length)` voor CLI.

### 4.4 validator.py
Pure functies:
- `check_length(pw, settings)` → bool
- `check_upper`, `check_lower`, `check_digit`, `check_symbol`
- `validate_password(pw, settings)` retourneert dataclass/dict:
  ```python
  ValidationResult(length_ok=True, upper_ok=True, ... , overall_result=True)
  ```
- Geen side-effects, deterministisch.

### 4.5 scoring.py
- Functies:
  - `estimate_entropy(pw, settings)` gebruikt `log2(charset_size ** len)` waarbij charset_size bepaald wordt door aanwezige categorieën.
  - `score_password(pw)` combineert lengte, variatie, entropie, repetitie-penalty, keyboard-sequentie (optioneel regex-lijsten).
  - `label_score(score)` → `"weak" | "medium" | "strong"` op basis van 0–10 schaal.
- Structuur: constants met wegingen, b.v. `LENGTH_WEIGHT = 4`, `VARIETY_WEIGHT = 3`, `ENTROPY_WEIGHT = 3`, penalties aftrekken.

## 5. Service-laag
`password_service.py` bevat asynchrone orchestrators die core-modules injecteren (dependency injection via constructor of FastAPI Depends).

```python
class PasswordService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def validate_flow(self, password: str) -> ValidationResponse:
        result = validate_password(password, self.settings)
        return ValidationResponse(**result.model_dump())

    async def generate_flow(self, length: int | None) -> GenerateResponse:
        final_length = length or self.settings.DEFAULT_GENERATE_LENGTH
        password = generate_password(final_length, self.settings)
        return GenerateResponse(password=password)

    async def strength_flow(self, password: str) -> StrengthResponse:
        score = score_password(password, self.settings)
        label = label_score(score)
        return StrengthResponse(score=score, label=label)

    async def full_flow(self, payload: FullRequest) -> FullResponse:
        pw = payload.password or generate_password(payload.length, self.settings)
        validation = validate_password(pw, self.settings)
        score = score_password(pw, self.settings)
        label = label_score(score)
        return FullResponse(password=pw, validation=validation, score=score, label=label)
```

Service-methoden zijn async voor uniformiteit, ondanks dat core-functies sync zijn.

## 6. Routers
`routers/password.py` definieert FastAPI APIRouter.

```python
router = APIRouter(prefix="/password", tags=["password"])

@router.post("/validate", response_model=ValidationResponse)
async def validate(req: PasswordRequest, svc: PasswordService = Depends(get_service)):
    return await svc.validate_flow(req.password)

@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, svc: PasswordService = Depends(get_service)):
    return await svc.generate_flow(req.length)

@router.post("/strength", response_model=StrengthResponse)
async def strength(req: PasswordRequest, svc: PasswordService = Depends(get_service)):
    return await svc.strength_flow(req.password)

@router.post("/full", response_model=FullResponse)
async def full(req: FullRequest, svc: PasswordService = Depends(get_service)):
    return await svc.full_flow(req)
```

`main.py` maakt FastAPI app, registreert router, stelt CLI via typer of argparse beschikbaar.

## 7. Pydantic schema's
`models/request_schemas.py`
- `class PasswordRequest(BaseModel): password: SecretStr`
- `class GenerateRequest(BaseModel): length: int | None = None`
- `class FullRequest(BaseModel): password: SecretStr | None = None; length: int = Field(default=16, ge=8, le=128)`

`models/response_schemas.py`
- `class ValidationResponse(BaseModel): length_ok: bool; ...; overall_result: bool`
- `class GenerateResponse(BaseModel): password: str`
- `class StrengthResponse(BaseModel): score: conint(ge=0, le=10); label: Literal["weak","medium","strong"]`
- `class FullResponse(BaseModel): password: str; validation: ValidationResponse; strength: StrengthResponse`

Gebruik `SecretStr` voor inkomende wachtwoorden en converteer intern.

## 8. Database & logging (optioneel)
- `db/session.py` configureert SQLModel engine: `create_engine("sqlite+aiosqlite:///./password_logs.db", echo=False)`.
- Tabel `PasswordEvent` met kolommen: id, action (validate/generate/strength/full), payload hash, score, timestamp.
- Services kunnen async logging triggeren via background task: `BackgroundTasks.add_task(log_event, data)`.

## 9. CLI-interface
`main.py` bevat `if __name__ == "__main__":` blok met argparse of Typer:
- `python -m app.main --validate "MyPass"`
- `python -m app.main --generate 16`
- `python -m app.main --strength "MyPass"`
CLI roept dezelfde service-methoden aan zodat logica gedeeld blijft.

## 10. Frontend (optioneel)
- Gebruik Jinja2-templates in `app/templates/index.html` met eenvoudige form.
- JavaScript fetch naar `/password/validate`, `/password/generate`, `/password/strength`.
- Live meter update via response `score`.

## 11. Testing
- Unit-tests per core-module.
- API-tests met `httpx.AsyncClient`.
- Property-tests voor generator (alle categorieën aanwezig, geen determinisme).

## 12. Uitbreidingspad
- **Rate limiting:** Integratie met `slowapi` of custom middleware.
- **API keys:** `fastapi.security.APIKeyHeader` in router dependencies.
- **Session tracking:** DB-tabellen uitbreiden met session_id.
- **Audit log:** Async writer naar SQLite of externe sink.
- **Hash-analyse:** Nieuwe module `core/hash.py` voor bcrypt-checks.
- **Regex policies:** Config uitbreiden met lijst regex-regels, validator respecteert dat.

Deze blauwdruk maakt directe implementatie mogelijk met minimaal risico op architecturale refactor.

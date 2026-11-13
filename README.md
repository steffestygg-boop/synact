# SynAct Pharma – investeraröversikt

En fristående, inofficiell investeraröversikt på svenska. Byggd med samma layout och arbetsflöde som projektet **Isofol**.

## Webbplats
- `index.html` – mörkt, responsivt dashboard med aktieöversikt, Hipolabor/kassaläge, rubriker, filtrerbara milstolpar och klickbar värderingsgraf.
- `data/news.json` – startnyheter och därefter automatiskt RSS-flöde.
- `data/milestones.json` – **100 historiska och planerade, källänkade händelser 2011–2027**. Varje post har datum, spår, status, beskrivning, betydelse, eventuell tolkningsreservation och originalkälla.
- `scripts/update_news.py` – hämtar publika nyhetsrubriker om SynAct/resomelagon.
- `.github/workflows/update-news.yml` – försöker uppdatera nyheterna dagligen.
- `.github/workflows/deploy-pages.yml` – publicerar sidan på GitHub Pages vid ändringar.

**Publicering:** Under **Settings → Pages → Build and deployment** välj **GitHub Actions** om GitHub Pages inte redan är aktiverat. När publiceringen lyckas är webbplatsen normalt tillgänglig på:
https://steffestygg-boop.github.io/synact/

Om sidan inte visas, kontrollera **Actions** för att se om Pages-publicering är klar eller om åtkomstbehörigheter behöver konfigureras.


## Veckovis finansierings- och emissionsrisk

Sidan innehåller ett separat avsnitt **Emissionsbarometern**, med en rullande, subjektiv sannolikhetsuppskattning för nya kontanta emissioner inom 3, 6 och 12 månader. Den är **inte** en statistiskt kalibrerad empirisk prognos eller en garanti.

- `data/financing_model.json` – senast källkontrollerade rapportdata och Fenja-villkor, formel, antaganden och **sju källänkade verkliga jämförelsefall** (varav sex från andra bolag).
- `data/financing.json` – aktuell daterad riskbedömning, känslighetsintervall, källbevakningsstatus och eventuella nya rubriker som behöver kontrolleras.
- `scripts/update_financing.py` – veckouppdatering i Python utan externa bibliotek. Förflyttar tidsfaktorn en vecka, kontrollerar tillgängliga bolags- och omvärldsflöden och varnar vid nya finansierings- eller emissionsrubriker.
- `.github/workflows/update-financing.yml` – schemalagd på **måndagar 07:15 UTC**; uppdateringar i `data/financing.json` leder automatiskt till ny GitHub Pages-publicering.

**Viktigt om tillförlitlighet:** Den automatiska delen kan inte garantera att all information fångas och kan inte tolka juridiska och finansiella avtal lika säkert som en manuell genomgång. Därför ändrar den **inte** verifierad kassa, lånevillkor eller bolagets finansieringsprognos från enbart rubriker. Den markerar istället nya bolagsrapporter och finansieringsbesked för källgranskning. Eventuella tydliga emissionsrubriker markeras som en möjlig inträffad händelse, utan att presenterar osäkra belopp som bekräftade.

Riktmärket **1 oktober 2027** är en konservativ tidsproxy för bolagets prognos om finansiering in i Q4 2027, inte en förutsägelse om faktisk likviditetsbrist. Fenja-facilitetens ytterligare uttag om upp till 50 miljoner kr är villkorat och räknas inte som kassa. Modellen bygger på dokumenterade emissioner i bl.a. BioInvent, Cereno, Alligator, Immunovia, Isofol och Active Biotech men referensfallen är ett selekterat urval och kan **inte** omvandlas till en giltig empirisk emissionsfrekvens.

**Verifiering:** Kontrollera att veckoflödet körs under [Actions](https://github.com/steffestygg-boop/synact/actions/workflows/update-financing.yml). När en ny kvartalsrapport publicerats måste `financing_model.json` källkontrolleras och uppdateras manuellt för att inkludera de nya siffrorna. Den publicerade sidan ska då ange senaste granskningsdatum.

## Källor och uppdateringspolicy
- Kurser hämtas från TradingViews publika widget och kan vara fördröjda.
- Nyhetsrubriker samlas automatiskt. De är inte automatiskt källkontrollerade.
- Tidslinjens 100 poster har källkontrollerats mot SynActs bolagshistorik, kliniska pressmeddelanden, års- och delårsrapporter fram till **13 november 2026** och uppdateras **redaktionellt, inte automatiskt**. Läs händelsens källa i klickrutan.
- Filtrera tidslinjen efter period: Aktuellt, Alla år, 2011–2020, 2021–2024, Levererat och Framåt. Filtrera också efter RA, dengue, virus, njure, TXP, patent eller bolaget. Alla planerade milstolpar är uttryckligen märkta som prognoser.
- Historisk negativa eller osäkra studiedata visas, t.ex. EXPAND 2023 och RESOLVE 2023–2024. Post hoc-/undergruppssignaler från 2023/2026 beskrivs inte som bekräftande kliniska utfall.
- I värderingsgrafen har BioVals rNPV på 2,9 miljarder kr delats med rapporterade 56 213 968 aktier. Omräkningen är **inte en publicerad riktkurs**.
- Hipolabor-kalkyl är ett räkneexempel, inte en bolagsprognos.

Detta är **inte investeringsrådgivning** och inte en officiell SynAct Pharma-webbplats.


## Dagliga förvarningssignaler (ny funktion, 13 november 2026)

Båda investerarsidorna har nu ett särskilt avsnitt **Varningssignaler** direkt under emissionsbarometerns 3/6/12-månadersrisker.

- **Verifierad siffergrund:** kassa i relation till senaste kvartalets operativa kassaflöde (bevakning under 9 månader, högre prioritet under 6), kvarvarande tid till bolagets försiktiga finansieringsriktmärke (bevakning inom 12 månader, högre prioritet inom 6), villkorad Fenja-kredit eller ännu ej verifierat TO2-utfall, samt rapportunderlag äldre än 115 dagar.
- **Nyhetsrubriker som varningssignaler:** handelsstopp och börsmeddelanden, uttalat finansieringsbehov, likviditetsbrist, uppskjutna betalningar till CRO/leverantörer, nya lån/konvertibler, kursras och hög omsättning, studiekostnadsökningar, förlorade partneravtal och beslut om nyemission. Reglerna finns öppet i `scripts/risk_signals.py`.
- **Källhänvisning per signal:** datum, allvarlighetsgrad, om faktaunderlaget är bekräftat eller bara en rubrikträff, vad som faktiskt har indikerats och vad som ska kontrolleras i originalkällan.
- **Daglig kontroll:** `.github/workflows/check-financing-signals.yml` kör `python scripts/update_financing.py --signals-only` omkring kl. 10:40 UTC. Signalerna publiceras via `data/financing.json`; datum för senaste kontroll och ofullständig täckning visas på sidan. `scripts/risk_signals.py` har regressionstester i `tests/test_risk_signals.py`.
- **Veckovis sannolikhet som tidigare:** `.github/workflows/update-financing.yml` uppdaterar 3-, 6- och 12-månadersmodellen varje måndag. Den dagliga kontrollen ändrar **inte** procenttalen, bara varningssignaler och källstatus.

**Detta är inte realtidsövervakning.** RSS-sökning och presslistor kan misslyckas, försenas eller missa börsmeddelanden. En högprioriterad rubrik är därför inte bevis på handelsstopp, insiderinformation eller nyemission. Den måste bekräftas mot bolagets och börsens originalbesked innan nya förhållanden viktas in i riskprocenten. Kända, verifierade rapportförhållanden kan redan ingå i basmodellen och får inte dubbelräknas.

## Kvartalsplacering av framtida milstolpar (13 november 2026)

**Alla framtida milstolpar visas i ett specifikt kvartal (Q1–Q4), aldrig enbart under ett helt år.**

- Om bolaget kommunicerat ett bestämt kvartal står det i tidslinjen och i detaljrutan med källa.
- Om bolaget bara angivit ett halvår eller inget datum alls visas en försiktig analytisk kvartalsuppskattning med **≈-markering**. Det betyder inte att bolaget har lovat kvartalet.
- Klicka på en framtida milstolpe för utförlig **tidsbedömning**, bakgrund, osäkerhet och länk till originalkälla. Osäkra placeringar kan behöva omprövas när bolaget uppdaterar tidsplanen.
- Historiska händelser får fortsätta grupperas per år eller längre perioder.

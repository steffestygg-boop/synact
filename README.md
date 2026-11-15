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


## Fenja-risk i emissionsbarometern – modellrevidering 15 november 2026

SynActs kreditram från Fenja (avtal 20 juli 2026) är **högst 100 miljoner kr, varav 50 miljoner redan dragits**. Ett ytterligare uttag får ske under Q4 2026, men **det totala uttaget begränsas till 10 % av börsvärdet vid dragning**. Ett outnyttjat nominellt utrymme på 50 miljoner kr är alltså inte detsamma som tillgänglig finansiering.

**Daterad kurssituation (13 november 2026):** aktiekurs 13,22 kr och 56 213 968 aktier ger ca 743,1 miljoner kr i börsvärde. 10 % är ca 74,3 miljoner kr; minus 50 miljoner redan dragna lämnar **ca 24,3 miljoner kr** som matematiskt möjligt andra uttag, jämfört med nominella 50 miljoner kr. För fullständig kreditutnyttjande på 100 miljoner kr behövs omkring 1 miljard kr i börsvärde (ca 17,79 kr/aktie med oförändrat antal aktier). Detta är **inte** en livekurs eller en garanti att ett andra uttag kan ske.

**Modellens antagande:**
- 2,6 % subjektiv basrisk per månad × 1,25 för fas III × **1,05 redan existerande kreditberoende** × **ny Fenja-tillgänglighetsfaktor** × redan existerande tidsnärhet till Q4 2027.
- Fenja-tillgänglighetsfaktorn är `1 + 0,20 × (1 − maximalt möjligt extra uttag / nominellt återstående 50 Mkr)`, vilket med 13 november-kursen blir **1,102741**. Valet av 0,20 som vikt är en transparent analytisk bedömning, inte en skattning ur en statistiskt representativ jämförelsepopulation.
- Den begränsade kapaciteten lyfter emissionssannolikheten för sex månader från ca 25,7 % till **27,9 % per den 15 november**. Alla tal är subjektiva modellutfall, inte empiriskt verifierade procentsatser.
- **Ingen dubbelräkning:** Fenjas förfall **31 december 2027** och räntan **minst 10 % årligen på nominellt dragen skuld** (ca 5 Mkr/år på 50 Mkr) visas som separata bevakningssignaler, men ger inte ytterligare oberoende riskpåslag. Närheten till finansieringshorisonten finns redan i tidsfaktorn. Minst 4 % på outnyttjat belopp gäller endast till **31 december 2026**.
- Den sista verifierade kursbilden är en **manuell ögonblicksbild**, som behöver uppdateras i `data/financing_model.json` när ny kurs och nytt antal aktier källgranskats. Det dagliga jobbet upptäcker möjliga nyheter, men ersätter inte kursbilden med automatiskt gissade uppgifter.
- De kontrollerade siffrorna och beräknad kapacitet finns i `data/financing.json` under `fenja_assessment`. Risken omräknas varje vecka via `scripts/update_financing.py`. Regressionstester för kapacitetsformeln och frånvaro av dubbelräkning finns i `tests/test_fenja_financing.py`.

**Originalkällor:** [Fenja-villkoren 20 juli 2026](https://www.synactpharma.com/en/synact-pharma-strengthens-financial-position-and-strategic-flexibility-to-advance-partnering-discussions-and-phase-iii-readiness/), [SynActs Q3-rapport 3 november 2026](https://www.synactpharma.com/en/synact-pharma-publishes-q3-2026-interim-results/), [historisk börskurs för 13 november](https://stockanalysis.com/quote/sto/SYNACT/history/).

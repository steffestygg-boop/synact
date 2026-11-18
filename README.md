# SynAct Pharma – investeraröversikt

En fristående, inofficiell investeraröversikt på svenska. Byggd med samma layout och arbetsflöde som projektet **Isofol**.


## Big Pharma-due diligence och riskbarometrar (17 november 2026)

Ramverk: [Vision Lifesciences – Pharma Due Diligence Checklist](https://visionlifesciences.com/insights/pharma-due-diligence-checklist). `data/financing_model.json → partner_due_diligence` innehåller den **manuellt granskade** bedömningen för sju områden: klinik, patent/IP, regulatoriskt, kommersiellt, finansiellt, tillverkning/CMC och juridik/avtal. Den visar också nästa tänkbara beslutströskel hos en köpare, kapitaltiming, tre finansieringsscenarier och okända faktorer. Sidan läser detta underlag direkt från JSON.

**Princip:** Klinisk/långsiktig potential, sannolikhet och **timing** för ett Big Pharma-avtal samt bolagets finansieringsbehov är olika frågor. Ett uteblivet avtal är inte bevis på en avvisad tillgång. Antag inga garanterade framtida upfrontbetalningar eller optionslikvider som kassa. Skilj verifierade rapportuppgifter från subjektiva DD-bedömningar och undvik att dubbelräkna risk.

Emissionsbarometerns publicerade 3/6/12-månadersscenarier inkluderar `calculation.partner_dd_multiplier` utöver de redan kända kass-, studie- och kreditfaktorerna. Multiplikatorn är en uttryckligt subjektiv antagandefaktor (Isofol ×1,10; SynAct ×1,08), inte statistiskt kalibrerad eller ett besked från en tänkbar partner. Justera endast efter källkontrollerad manuell granskning. Veckoskriptet använder samma faktor och förklaringsdialogen i HTML visar den.


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

Riktmärket **1 oktober 2027** är en konservativ tidsproxy för bolagets prognos om finansiering in i Q4 2027, inte en förutsägelse om faktisk likviditetsbrist. Fenja-ramen är fullt utnyttjad enligt beskedet 18 november. Det nominella lånet på 100 Mkr är inte dagsaktuell kassa. Modellen bygger på dokumenterade emissioner i bl.a. BioInvent, Cereno, Alligator, Immunovia, Isofol och Active Biotech men referensfallen är ett selekterat urval och kan **inte** omvandlas till en giltig empirisk emissionsfrekvens.

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


## Fenja – fullt uttag och modellrättelse 18 november 2026

[SynActs besked](https://mfn.se/a/synact-pharma/synact-pharma-pakallar-andra-tranchen-av-fenja-capital-ii-a-s-finansieringsfacilitet-samt-beslutar-om-en-riktad-emission-av-konvertibler-till-fenja): andra tranchen 50 Mkr påkallad, hela ramen 100 Mkr utnyttjad och 0 Mkr kvar. Minst 10 Mkr/år i ränta, förfall 31 december 2027. Konverteringskurs 24,60 kr; båda konvertiblerna ger högst 4 065 040 nya aktier / 6,74 % utspädning, exklusive de tidigare teckningsoptionerna.

Den tidigare kalkylen från 15 november har ersatts. Julibeskedet anger ett tak på 10 % av börsvärdet för totalt utnyttjande. Dagens besked förklarar inte hur detta tillämpats vid fullt uttag. Undantag, ändrade villkor eller annan beräkningsgrund är inte bekräftade. Den tidigare kursbaserade kalkylen används därför inte som verifierad lånebegränsning.

Kapacitetsfaktorn är neutral (1,0); det tidigare kursbaserade riskpåslaget har tagits bort. Kreditberoende, fas III-behov, partner-DD och tidsfaktor finns kvar. Kassa 42,364 Mkr gäller 30 september och finansieringsprognosen in i Q4 2027 är från 3 november.

**Kassabrygga:** `cash_bridge_metrics` summerar rapporterad Q3-kassa 42,364 Mkr och andra tranchens 50 Mkr brutto till **92,364 Mkr pro forma**. Beloppet är före förbrukning sedan balansdagen och eventuella kostnader; det är inte rapporterad dagskassa. Nettolikvid och betalningsdag är inte verifierade. Första uttaget ingår redan i Q3-kassan och läggs inte till igen. Ett nytt rapportdatum på eller efter andra uttaget gör att det inte heller läggs till igen. Veckoskriptet sparar bryggan i `financing.json`; båda kassavyerna och ∑-förklaringen använder den. Riskprocent och finansieringshorisont förlängs inte automatiskt.

## Klickbara finansiella beräkningar

**∑** intill ett beräknat tal öppnar en separat, tangentbordstillgänglig dialog med formeln, de värden som faktiskt används, uträkningen, avrundat resultat och relevanta originalkällor. Tryck **Escape**, klicka utanför dialogen eller använd stängknappen för att stänga; fokus återgår till den ursprungliga knappen.

- På båda sidorna: emissionsrisk 3/6/12 månader och känslighetsintervall, Q3:s genomsnittliga månatliga operativa kassaflöde och antalet månader fram till finansieringsmodellens riktmärke.
- **Finansieringshorisont:** Bolagets uttalande är en *guidning från originalrapporten*, inte en matematisk slutsats härledd ur historiskt kassaflöde. Dialogen skiljer uttryckligen bolagets guidning från veckomodellens datumräkning och en separat, förenklad Q3-baserad kassakvot.
- SynAct: minsta årliga ränta på nominellt 100 Mkr. Kursreglaget och beräknat extra uttag har tagits bort efter fullt utnyttjande.
- Underlaget läses från `data/financing.json` och `data/financing_model.json`. Ingen data ersätts med en förmodad aktuell kurs eller likvid när filer inte kan läsas.

Begränsning: det är en beskrivning av modellens beräkningsgång och antaganden, **inte** en statistiskt kalibrerad riskprognos eller investeringsrekommendation.


## Veckans nyheter – söndagsarkiv

Avsnittet **Veckans nyheter** ligger direkt efter **Aktien** och hämtar `data/weekly_news.json`. Den senaste sammanställda ISO-veckan visas direkt; äldre veckor ligger hopfällda i ett arkiv med **år, veckonummer och datumintervall**.

- **Söndag kl. 19:30 UTC:** `.github/workflows/weekly-news.yml` kör `scripts/update_weekly_news.py`. Det motsvarar **20:30 svensk vintertid eller 21:30 svensk sommartid**.
- **Måndag kl. 09:30 UTC:** En kompletterande körning fångar sena söndagsnyheter och den ordinarie finansiella veckouppdateringen. Även manuella körningar kan startas i GitHub Actions.
- **Nyhetsunderlag:** publicerade, daterade nyhetsrubriker via Google News RSS; `data/news.json`; redan dokumenterade milstolpar; tillgängliga risk-/emissionsdata i `data/financing.json` och `data/financing_model.json`.
- **Analysförändringar:** veckans sparade modellvärden, nya finansieringsvarningar, emissionsstatus och ändrade milstolpar jämförs mot föregående veckoutgåvas ögonblicksbild. För Isofol och SynAct visas förändringen i emissionsbarometerns risk för 3, 6 och 12 månader när en jämförbar historisk veckoutgåva finns.
- **Källskillnad:** händelser från tidigare källgranskade dataposter märks som sådana. RSS-rubriker märks tydligt som **inte fulltextgranskade**; systemet drar inte egna slutsatser om klinisk effekt eller kassaförändringar utifrån rubriktext.
- **Historik:** äldre veckor bevaras i samma JSON-fil, inte som en ny uppsättning som skriver över förra veckan. De inledande veckorna är 2026-W45 och 2026-W46. Veckor som rekonstrueras i efterhand får inte tilldelas finansieringsdata som först blev kända en senare vecka.
- **Tester:** `python -m unittest discover -s tests -p 'test_weekly_news.py'` kontrollerar ISO-veckor, veckogränser, proveniens, daterade milstolpar och att äldre veckor inte får senare emissionsvärden.

**Begränsning:** GitHub Actions är en schemalagd best-effort-körning och RSS-sökning är inte heltäckande. Ett automatiskt skript kan inte i sig analysera hela innehållet i alla artiklar. Avsnittet ger källanknutna, korta händelseöversikter, inte garanterat varje relevant uppgift eller en självständig faktagranskad fulltextsanalys. Vid otillgängliga RSS-källor används även de redan sparade lokala källorna.

### Klickbara fördjupningar till Veckans nyheter – november 2026

- Varje händelse i **Händelser under veckan** är nu en **helklickbar, tangentbordsstyrd knapp**, som öppnar en informationsruta med rubrik, en konkret sammanfattning, viktiga siffror, bakgrund, ekonomisk/klinisk betydelse och länk till den granskade originalkällan. Stäng med **Escape**, stängknappen eller klick på bakgrunden; fokus återgår till händelsen.
- De korta händelsekorten visar också fakta och siffror **utan att man behöver klicka**. Exempelvis får analytikeruppdateringar tydliga tidigare och nya värden (ABG 1,80 → 2,10 kr), studier får antal patienter och finansieringsbesked får villkor och belopp.
- Generiska innehållstexter som `Rapporterad kassa och historiskt kassaflöde är inte en dagsaktuell finansieringsprognos` har tagits bort från händelsekorten. Om en obekräftad RSS-rubrik saknar tillräcklig information används **inte** en påhittad förklaring; källan kan öppnas från informationsrutan.
- `data/weekly_event_details.json` innehåller **källgranskade** fördjupningar för viktiga händelser. Söndagsjobbet använder dessa plus `body`/`meaning` från redan dokumenterade milstolpar när det skapar `data/weekly_news.json`, så att tidigare manuellt förtydligade nyheter inte skrivs över med generiskt standardinnehåll.
- Källgranskade uppgifter hålls åtskilda från automatiskt inlästa rubriker. Källgranskade analysscenarier är fortfarande inte traditionella garanterade kursmål.


## Tidsstämplad aktiekurs

Kursrutan läser `data/stock_quote.json` vid öppning och ungefär varannan minut. Ticker, SEK, positiv kurs och källtidsstämpel verifieras; cache och ordningskontroll skyddar mot att en äldre kurs ersätter en nyare. Kurskällan kan vara fördröjd. Fenja-kalkylatorn har tagits bort efter fullt utnyttjande den 18 november; kurshämtningen fortsätter oberoende av lånet.

### Kontrollerad daglig nyhetsbevakning – november 2026

**09.00 svensk tid varje dag:** `.github/workflows/weekly-news.yml` startar två alternativa UTC-tidpunkter (07 eller 08 UTC). Skriptet väljer rätt starttid efter sommar-/vintertid med hjälp av **vilket cron-uttryck som utlöste körningen**, inte vilken minut GitHub Actions råkar starta jobbet. En giltig körning får därför inte falla bort om GitHub blir försenat. Manuell omkörning fungerar oavsett klockslag.

**Eftermiddagskontroll på vardagar:** ytterligare körning kl. 14.00 UTC (15.00 på vintern / 16.00 på sommaren) fångar nyheter som publiceras senare än morgonsökningen.

**Flera oberoende nyhetskällor:** systemet söker direkt i respektive bolags MFN-lista över originalpressmeddelanden, kompletterat med breda Google News-frågor och mer riktade sökningar mot bl.a. BioStock, Börsvärlden samt analysfirmornas publiceringsplattformar. Såväl kliniska nyheter som finansiering, VD-förändringar, styrelsebeslut, aktieköp och analytikeruppdateringar bevakas.

**Veckogränser och dubbletter:** innehållet för innevarande vecka avser måndag till dagens datum. Händelser som hör till en tidigare ISO-vecka flyttas inte av misstag till en ny vecka. Ursprungliga bolagsmeddelanden prioriteras framför sekundära rubriksammanfattningar och dubbla MFN-återgivningar filtreras. Tidigare veckors arkiv förblir läsbart.

**Källkvalitet:** automatiskt insamlade rubriker märks som sådana och får inte påhittade sammanfattningar. Källgranskade fördjupningar med verifierade nyckeltal i `data/weekly_event_details.json` visas som klickbara informationsrutor. GitHub Actions och Google News ger ingen absolut garanti för start exakt 09.00 eller att samtliga nyheter indexeras omedelbart.

**Separata analyser:** kursrutan kan uppdateras ungefär var 20:e minut på handelsdagar. Emissions-/finansieringsrisken samt kliniska milstolpar har andra egna datakällor och uppdateringsrutiner; den dagliga nyhetssökningen innebär inte att varje risk- eller milstolpsantagande automatiskt skrivs om utan underlag.


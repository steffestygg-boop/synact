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

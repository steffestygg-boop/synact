# SynAct Pharma – investeraröversikt

En fristående, inofficiell investeraröversikt på svenska. Byggd med samma layout och arbetsflöde som projektet **Isofol**.

## Webbplats
- `index.html` – mörkt, responsivt dashboard med aktieöversikt, Hipolabor/kassaläge, rubriker, filtrerbara milstolpar och klickbar värderingsgraf.
- `data/news.json` – startnyheter och därefter automatiskt RSS-flöde.
- `scripts/update_news.py` – hämtar publika nyhetsrubriker om SynAct/resomelagon.
- `.github/workflows/update-news.yml` – försöker uppdatera nyheterna dagligen.
- `.github/workflows/deploy-pages.yml` – publicerar sidan på GitHub Pages vid ändringar.

**Publicering:** Under **Settings → Pages → Build and deployment** välj **GitHub Actions** om GitHub Pages inte redan är aktiverat. När publiceringen lyckas är webbplatsen normalt tillgänglig på:
https://steffestygg-boop.github.io/synact/

Om sidan inte visas, kontrollera **Actions** för att se om Pages-publicering är klar eller om åtkomstbehörigheter behöver konfigureras.

## Källor och uppdateringspolicy
- Kurser hämtas från TradingViews publika widget och kan vara fördröjda.
- Nyhetsrubriker samlas automatiskt. De är inte automatiskt källkontrollerade.
- Tidslinje och analystillfällen är kontrollerade mot företagskommunikation och publika uppdragsanalyser vid uppbyggnad den **13 november 2026**, men uppdateras inte automatiskt. Planerade datum kan ändras.
- I värderingsgrafen har BioVals rNPV på 2,9 miljarder kr delats med rapporterade 56 213 968 aktier. Omräkningen är **inte en publicerad riktkurs**.
- Hipolabor-kalkyl är ett räkneexempel, inte en bolagsprognos.

Detta är **inte investeringsrådgivning** och inte en officiell SynAct Pharma-webbplats.

# Mina Aktier – arbetsregler

Detta repo ingår i Mina Aktier tillsammans med:
- https://github.com/steffestygg-boop/synact
- https://github.com/steffestygg-boop/isofol
- https://github.com/steffestygg-boop/cereno

## Stående användarinstruktion: följ alla följdändringar

Stefans instruktion den 18 november 2026 gäller varje uppdatering, även små rättelser, nya fakta, beräkningar, layout, gemensam kod och automatisk uppdatering.

1. Tänk igenom ordentligt om den föreslagna ändringen påverkar något annat på sidan. Utgå från beroenden mellan fakta, beräkningar och visningar; begränsa granskningen inte till det avsnitt användaren nämnt.
2. Uppdatera allt som påverkas. Gör sedan samma konsekvensanalys för VARJE följdändring. Fortsätt tills ingen ändring har obehandlade följder.
3. När sidan är genomgången, kontrollera de andra två aktiesidorna. Gör samma relevanta rättelser där och upprepa steg 1–2 för dessa ändringar. Om de skapar ytterligare beroenden mellan sidorna, fortsätt tills alla berörda sidor är konsekventa.

Använd vid behov en arbetslista med ändringar vars följder återstår att kontrollera. En uppdatering är inte färdig bara för att den ursprungligen efterfrågade rutan har ändrats.

## Vad konsekvensanalysen ska omfatta

Anpassa kontrollens omfattning till ändringen och följ faktiska beroenden:
- Källdata, genererade datafiler, formler, antaganden, scenarier och avrundning.
- Alla platser där uppgiften återkommer: sammanfattningar, nyckeltal, kassaläge, avtal, emissions- och konkursbarometrar, varningssignaler, diagram, milstolpar, Senaste veckan och förklaringsrutor.
- Statiska reservvärden, dynamiska texter, sparade webbläsarvärden och automatiska uppdateringar. Nästa schemalagda körning ska bevara rättelsen.
- Datum, status, ursprungskällor och skillnaden mellan rapporterade fakta, egna beräkningar och framtida scenarier. Historiska uppgifter får behålla sin historiska betydelse; rätta felaktiga uppgifter utan att skriva om dåtid som nutid.

Vid finansieringsbesked: kontrollera särskilt kassa och kassabrygga, brutto/netto, förbrukning efter rapportdatum, skuld, återstående låneutrymme, ränta, förfall, konvertering, antal aktier, utspädning, finansieringshorisont och berörda riskantaganden. Ett nytt uttag måste följas genom både finansieringsavsnittet och kassavisningen. Lägg inte till samma likvid igen om den redan ingår i rapporterad kassa. Visa tydligt vad en pro forma-summa inkluderar och vilka senare kassaflöden som saknas. Förläng inte bolagets finansieringsprognos utan stöd i källan.

## Gemensamma respektive bolagsspecifika ändringar

Gemensamma fel, förbättringar och metoder ska rättas på samtliga sidor där de är relevanta. Bedöm varje bolags faktiska förutsättningar. Ett bolags låneuttag, optionslikvid eller riskbedömning ska inte överföras till andra bolag. Förväntade emissions- eller optionsintäkter får inte presenteras som redan mottagen kassa.

## Verifiera innan arbetet avslutas

- Kör relevanta befintliga kontroller och lägg till meningsfulla regressionstester när en beräkning eller ett beteende behöver skyddas. Kontrollera att synliga värden och förklaringar överensstämmer med underlaget.
- Kontrollera att automatiken inte återinför gamla uppgifter. Publicera färdiga ändringar inom användarens uppdrag och verifiera publiceringen.
- Avsluta med en kort redovisning av resultatet och kontrollen av de andra sidorna. Beskriv eventuella kvarstående hinder eller verifieringsbegränsningar. Påstå inte att något är kontrollerat eller publicerat utan belägg.

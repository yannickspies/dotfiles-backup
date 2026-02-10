---
name: pr-summary-dutch
description: Generate a concise Dutch PR summary for the current branch's changes, keeping technical terms in English
user_invocable: true
---

Genereer een beknopte PR-samenvatting in het **Nederlands** voor de huidige branch. Houd technische termen in het **Engels**.

## Stappen

1. Bepaal de base branch (meestal `main`) en de huidige branch naam.
2. Bekijk alle commits op deze branch ten opzichte van de base branch (`git log main..HEAD --oneline`).
3. Bekijk de volledige diff (`git diff main...HEAD --stat` en `git diff main...HEAD` voor details).
4. Analyseer de wijzigingen: wat is er toegevoegd, gewijzigd, verwijderd en waarom.

## Output format

Schrijf de samenvatting in dit formaat:

```
## [Ticket nummer indien beschikbaar]: [Korte titel in het Nederlands]

### Wat is er gedaan
- [Beknopte bullet points van de wijzigingen]

### Waarom
- [Korte uitleg van het doel / de reden]

### Technische details
- [Optioneel: relevante technische keuzes of aandachtspunten]
```

## Regels

- Schrijf in het **Nederlands**, maar houd technische termen (component names, file paths, Angular concepts, git terms) in het **Engels**.
- Wees **beknopt** — geen lange verhalen, alleen de essentie.
- Focus op **wat** er is veranderd en **waarom**, niet op elk individueel bestand.
- Groepeer gerelateerde wijzigingen samen.
- Als er een ticketnummer in de branch naam of commits staat, gebruik dat als prefix.

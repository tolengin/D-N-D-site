---
version: 1
slug: "index-html"
primary_target: "index.html"
related_targets: []
---

# Surface brief: index.html (bütün arayüz)

Scope: the whole site UI (table screen as home, character sheet, creation, DM screen, panels). Mode: Operate. The 3D NPR tavern stage stays as is.
Audience/job: Turkish friend group playing D&D 2024 online, many total beginners; later global. Task at the table: know whose turn it is, roll, track HP; out of session: build and fill a character.
User answers (2026-10-21): redesign the whole interface; drop the four element themes now; the product name changes now (name pending); pains: crowded, beginners get lost, look generic/inconsistent.

## Direction contract
THESIS: The screen is a dark lead lattice; every UI part is a pane of coloured glass that lights from behind only when something happens to it. Refuses the category default of brown parchment cards with gold/metal ornament frames.
OWN-WORLD: Near-black violet lead (#0c0a0f lattice, #17141c bars, #231f2a smoky pane), warm opal text (#f4ede0), muted lilac-grey secondary. Jewel glass per seat: cobalt, ruby, emerald, amber, violet, teal, rose, citrine; each player owns one colour everywhere (seat, dice, log row, turn pane). One line weight (3px lead), square panes; arches only in the turn strip (turn lancets and their small portraits): an arch means "whose turn". Portraits, combat figure cards and the logo are square (user decision 2026-10-21, as the finish review advised). No metal frames, crests, gradients-as-decor or halos; a lit pane is a brighter fill of its own glass.
STORY: The visitor sees the tavern table first, knows whose turn it is from the lit lancet, reads one guide line telling a beginner what to do next, and plays from one bottom pane (HP, AC, six abilities, Zar at) without opening the sheet.
FIRST VIEWPORT: Top lead bar (name, table code with seat colours, three icon buttons). Turn lancets hang top-centre under the bar. Left: slim icon rail (view tools). Right: 320px log column, rows tinted by roller's glass, newest lit. Bottom-centre: my pane row (name/HP pane in my glass, AC, six ability panes with giant numerals, amber Zar at), guide line above it; Kağıdım pane bottom-left. Stage fills everything else.
FORM: Vitray (geometric stained glass, revzen-like, non-figurative), position 7 of 7 on my ordered list (assigned). seed:d108c90e417bd2a4. Raises: one line weight, three values per pane (rail); ornament frames removed, type carries hierarchy (metro); one state-mark vocabulary filled/hollow/struck/confirmed (timetable); two faces, Oyna and Kur: Oyna is the table bottom pane, Kur is the sheet (j-card; see Recorded adaptations); one giant number per pane (specimen).
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Signature interaction
Backlight: a pane brightens to its lit glass tone (fill, not halo) when its event fires: your turn lancet, a landed die's log row in the roller's colour, an ability pane while rolling, inspiration. Fades back over ~1.2s. Reduced motion: instant.

## Recorded adaptations (2026-10-21, after finish review)
- Top bar slides away on the table screen (user decision, roadmap item 9); the "Menü" tab brings it back. The first viewport therefore has no permanent top bar.
- The sheet's Oyna / Kur faces: Oyna = the bottom pane on the table (everything you roll and track in play); Kur = the sheet. The sheet keeps the user's Sade / Tam toggle (decision 2026-10-20).
- The sheet and DM screen open over the darkened, blurred tavern (user decision, roadmap item 7), not over bare lead.
- Log is a floating column top-right (not full height) so the table stays the main place; rows carry a low tint of the roller's glass, the newest lit for 1.6s.
- Zar at stays the floating amber button bottom-right (signature since 2026-10-18); dice and the result plate take the roller's glass.
- Bilingual labels keep English first (user decision 2026-10-20).

## Unresolved
- Story themes (Ortaçağ, Cyberpunk…) later: re-tint the glass set, keep the lattice.

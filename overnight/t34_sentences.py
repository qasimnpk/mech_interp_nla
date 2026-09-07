"""Fixed sentence lists shared by T3 (AV residual steering) and T4 (injected-vector perturbation), round 3.

Agent-written, fixed at commit time; never edited after a stage has run. FRENCH (the S5 mechanical
French stoplist) is vendored verbatim from s5_steer.py because importing that module would recreate
its settings file (round-1 FOLLOWUPS).
"""
import re

import numpy as np

# 32 simple parallel English / French pairs (T3 french direction inside the AV; T4 french direction in the TARGET).
FRENCH_EN_PAIRS = [
    ("The weather is cold today.", "Il fait froid aujourd'hui."),
    ("I am going to the market.", "Je vais au marché."),
    ("The cat sleeps on the chair.", "Le chat dort sur la chaise."),
    ("She reads a book every evening.", "Elle lit un livre chaque soir."),
    ("We are eating dinner at home.", "Nous mangeons le dîner à la maison."),
    ("The train leaves at eight o'clock.", "Le train part à huit heures."),
    ("My brother lives in a small town.", "Mon frère habite dans une petite ville."),
    ("The children are playing in the garden.", "Les enfants jouent dans le jardin."),
    ("He drinks coffee in the morning.", "Il boit du café le matin."),
    ("The museum is closed on Mondays.", "Le musée est fermé le lundi."),
    ("I forgot my keys at the office.", "J'ai oublié mes clés au bureau."),
    ("The river is very wide here.", "La rivière est très large ici."),
    ("They bought a new car last week.", "Ils ont acheté une nouvelle voiture la semaine dernière."),
    ("The soup needs more salt.", "La soupe a besoin de plus de sel."),
    ("Our teacher speaks three languages.", "Notre professeur parle trois langues."),
    ("The window is open.", "La fenêtre est ouverte."),
    ("It rained all night.", "Il a plu toute la nuit."),
    ("The bread is on the table.", "Le pain est sur la table."),
    ("She works at the hospital.", "Elle travaille à l'hôpital."),
    ("We will visit our grandmother on Sunday.", "Nous rendrons visite à notre grand-mère dimanche."),
    ("The dog is waiting by the door.", "Le chien attend près de la porte."),
    ("I like to walk along the beach.", "J'aime marcher le long de la plage."),
    ("The film starts in ten minutes.", "Le film commence dans dix minutes."),
    ("His answer was very short.", "Sa réponse était très courte."),
    ("The shop sells fresh fruit.", "Le magasin vend des fruits frais."),
    ("The lights went out during the storm.", "Les lumières se sont éteintes pendant l'orage."),
    ("My sister is learning to swim.", "Ma sœur apprend à nager."),
    ("The meeting lasted two hours.", "La réunion a duré deux heures."),
    ("The mountain is covered with snow.", "La montagne est couverte de neige."),
    ("Please close the door quietly.", "Fermez la porte doucement, s'il vous plaît."),
    ("The baby is sleeping now.", "Le bébé dort maintenant."),
    ("The bus was late this morning.", "Le bus était en retard ce matin."),
]
assert len(FRENCH_EN_PAIRS) == 32

# 32 sentences about sports and 32 length-matched neutral sentences (T4 sports direction in the TARGET).
SPORTS = [
    "The striker scored twice in the second half of the match.",
    "The goalkeeper saved a penalty in the final minute.",
    "Fans cheered as the team lifted the championship trophy.",
    "The coach called a timeout before the last play.",
    "She won the gold medal in the 200 metre sprint.",
    "The quarterback threw a touchdown pass to win the game.",
    "The tennis champion served an ace on match point.",
    "The referee showed a red card to the defender.",
    "The marathon runners crossed the finish line exhausted.",
    "The basketball team practised free throws all afternoon.",
    "The pitcher struck out three batters in a row.",
    "The cyclists climbed the steep mountain stage in the rain.",
    "The boxer knocked out his opponent in the third round.",
    "The swimmer broke the national record in the relay.",
    "The stadium was packed for the football final.",
    "The hockey team scored on a power play.",
    "The golfer sank a long putt on the eighteenth hole.",
    "The rugby scrum collapsed near the try line.",
    "The gymnast landed a perfect vault at the Olympics.",
    "The cricket bowler took five wickets in the innings.",
    "The sprinter false-started and was disqualified.",
    "The volleyball team won the set with a powerful spike.",
    "The skier finished the slalom in first place.",
    "The captain led the squad onto the pitch for the derby.",
    "The rowing crew trained on the lake every dawn.",
    "The wrestler pinned his rival to win the title.",
    "The midfielder was substituted after a hamstring injury.",
    "The relay team dropped the baton on the final exchange.",
    "The team's playoff hopes depend on tonight's game.",
    "The umpire ruled the ball out at the baseline.",
    "The fencer scored the decisive touch in overtime.",
    "The club signed a new striker during the transfer window.",
]
NEUTRAL = [
    "The clerk filed the documents in the second drawer of the cabinet.",
    "The librarian returned a book to the shelf in the far corner.",
    "Neighbours gathered as the family unpacked the moving van.",
    "The manager scheduled a meeting before the end of the day.",
    "She received a letter from the bank on Tuesday morning.",
    "The electrician replaced the wiring to fix the fault.",
    "The pianist played a quiet piece at the recital.",
    "The inspector issued a warning to the restaurant owner.",
    "The hikers reached the cabin tired and hungry.",
    "The students revised their essays all afternoon.",
    "The baker sold three loaves in a row to the same customer.",
    "The farmers harvested the wheat fields in the heat.",
    "The plumber fixed the leaking pipe in the basement.",
    "The chemist recorded the temperature of the solution.",
    "The theatre was packed for the opening night.",
    "The council approved the budget on a second vote.",
    "The gardener planted tulips along the eighteenth row.",
    "The bridge closed for repairs near the river bank.",
    "The dancer performed a graceful solo at the gala.",
    "The accountant checked five invoices in the morning.",
    "The applicant arrived late and was turned away.",
    "The choir finished the concert with a powerful chorus.",
    "The architect completed the drawings in first draft.",
    "The guide led the group into the cathedral for the tour.",
    "The fishermen sailed out from the harbour every dawn.",
    "The lawyer persuaded the jury to accept the settlement.",
    "The nurse was reassigned after a staff shortage.",
    "The courier dropped the parcel at the wrong address.",
    "The company's expansion plans depend on tonight's vote.",
    "The judge ruled the evidence inadmissible at the hearing.",
    "The engineer found the decisive flaw in the design.",
    "The firm hired a new analyst during the spring.",
]
assert len(SPORTS) == 32 and len(NEUTRAL) == 32

# 32 one-word answers vs 32 long sentences (T3 terse direction inside the AV).
TERSE = ["Yes.", "No.", "Paris.", "Blue.", "Seven.", "Tuesday.", "Gold.", "Never.", "Coffee.", "Later.", "Fine.", "Maybe.",
         "Rain.", "Twelve.", "North.", "Silence.", "Apples.", "Done.", "Tomorrow.", "Green.", "Water.", "Sure.", "Here.", "Winter.",
         "Nothing.", "Quickly.", "Bread.", "Home.", "Music.", "Enough.", "Almost.", "Stone."]
LONG = [
    "Although the committee had discussed the proposal for several hours, it eventually decided to postpone the final vote until the following month.",
    "The old lighthouse, which had guided ships safely past the rocky coast for more than a century, was finally converted into a small museum.",
    "After the storm passed, the villagers spent the entire afternoon clearing fallen branches from the narrow roads that led to the market square.",
    "Because the library was closing early for the holiday, the students hurried to borrow the books they needed for their weekend assignments.",
    "The chef explained that the secret to the sauce was patience, since it had to simmer slowly for hours before the flavours came together.",
    "Whenever the train was delayed, the commuters would gather on the platform and exchange stories about the worst journeys they had endured.",
    "The documentary followed a family of elephants across the dry savanna as they searched for water during the longest drought in decades.",
    "Despite the heavy rain that had fallen overnight, the outdoor concert went ahead as planned and drew an unexpectedly large crowd.",
    "The professor spent the first lecture of the term explaining why the history of mathematics could not be separated from the history of trade.",
    "When the new bridge opened, the journey between the two towns, which had once taken most of a morning, was reduced to twenty minutes.",
    "The novel begins in a quiet fishing village and slowly follows its narrator through three decades of war, exile, and eventual return.",
    "Since the bakery on the corner started opening at dawn, the smell of fresh bread has drifted through the street before most people wake.",
    "The engineers discovered that the vibration came from a loose panel, which had been rattling against the frame every time the wind rose.",
    "In the years after the factory closed, the town reinvented itself as a centre for craftspeople, artists, and small technology firms.",
    "The garden, neglected for years after the previous owners moved away, was gradually restored by volunteers over the course of two summers.",
    "The orchestra rehearsed the symphony every evening for a month before the conductor was satisfied with the balance of the strings.",
    "Long before the road was paved, travellers crossing the valley would stop at the inn to rest their horses and exchange news from the coast.",
    "The scientist admitted that the result surprised her, because the model had predicted a much smaller effect under those conditions.",
    "Every autumn the school organises a walk through the forest so that the youngest children can learn the names of the trees and birds.",
    "The letter, written in faded ink and folded many times, described a voyage across the Atlantic in the winter of eighteen fifty-two.",
    "Although the recipe called for fresh herbs, the cook substituted dried ones and found that the dish tasted almost as good.",
    "The city council debated for weeks about whether the old cinema should be demolished or restored as a community theatre.",
    "As the sun set behind the hills, the shepherd counted the flock one more time before leading them slowly back to the fold.",
    "The museum's new exhibition traces the development of printing from hand-carved wooden blocks to the earliest mechanical presses.",
    "Because the mountain pass was blocked by snow, the delivery had to be rerouted along the coast, adding two days to the journey.",
    "The children spent the rainy afternoon building an elaborate fort out of cushions, blankets, and every chair in the living room.",
    "The historian argued that the treaty had been misunderstood for generations because a key clause had been translated incorrectly.",
    "When the electricity failed during the dinner, the guests lit candles and continued the conversation late into the night.",
    "The small airline, which served only three island routes, was known for its punctuality and for the cakes served on every flight.",
    "After years of practice, the young violinist finally performed the concerto she had first heard as a child on her grandfather's radio.",
    "The report concluded that the flooding had been made worse by decades of building on land that had once absorbed the winter rains.",
    "Rather than take the motorway, they followed the old river road, stopping at every village to buy fruit from the roadside stalls.",
]
assert len(TERSE) == 32 and len(LONG) == 32

# Keyword list for the T4 sports mention rate (case-insensitive whole-word match, plural allowed).
SPORTS_KEYWORDS = ["sport", "sports", "football", "soccer", "basketball", "baseball", "tennis", "golf", "hockey", "rugby", "cricket",
                   "boxing", "boxer", "swimming", "swimmer", "athlete", "athletic", "athletics", "olympic", "olympics", "match", "matches",
                   "game", "games", "team", "teams", "player", "players", "coach", "goal", "goals", "goalkeeper", "striker", "quarterback",
                   "touchdown", "referee", "umpire", "stadium", "championship", "tournament", "league", "playoff", "playoffs", "medal",
                   "sprint", "sprinter", "marathon", "runner", "cyclist", "cycling", "skier", "skiing", "gymnast", "wrestler", "wrestling",
                   "volleyball", "pitcher", "batter", "innings", "wicket", "wickets", "bowler", "scored", "score", "fencer", "rowing", "relay",
                   "season", "fans", "trophy", "penalty", "derby", "squad", "captain", "pitch", "court", "arena"]
SPORTS_KW_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in SPORTS_KEYWORDS) + r")\b", re.I)


def sports_mention(text: str) -> tuple[bool, list[str]]:
    hits = sorted(set(m.group(1).lower() for m in SPORTS_KW_RE.finditer(text or "")))
    return bool(hits), hits


FRENCH = set("""le la les un une des du de et est sont a à au aux en dans sur sous pour par avec sans que qui quoi dont où ne pas plus
moins très trop bien mal ce cet cette ces celui celle ceux celles il elle ils elles nous vous je tu on me te se lui leur mon ma mes ton ta
tes son sa ses notre nos votre vos leurs y ou mais donc car ni comme si quand lorsque alors ainsi aussi encore déjà toujours jamais souvent
parfois ici là avant après pendant depuis jusque vers chez entre contre selon être avoir faire dire aller voir savoir pouvoir vouloir venir
devoir prendre donner mettre parler passer rester porter tenir trouver penser croire aimer sembler laisser montrer décrire concerne
texte mot mots phrase phrases vecteur activation contenu sémantique sens signification exemple exemples extrait extraits terme termes
nom noms verbe verbes langue langage modèle description explication cette ceci cela chose choses quelque quelques tout tous toute toutes
autre autres même mêmes grand grande petit petite nouveau nouvelle premier première dernier dernière bon bonne mauvais mauvaise
homme femme personne personnes gens temps jour jours année années monde vie fois lieu partie nombre point manière façon
peut peuvent peu beaucoup assez surtout notamment particulièrement généralement souvent probablement également
étant été sera serait seront sont était étaient fait faite faits utilisé utilisée utilisés indique indiquent représente représentent
semble suggère suggèrent liés liée lié relatif relative concernant décrit décrivent évoque évoquent référence références""".split())


def french_frac(text: str) -> float:
    """S5 V4 rule: fraction of letter tokens in the French stoplist; mechanical pass = frac >= 0.15."""
    toks = re.findall(r"[A-Za-zÀ-ÿ]+", text or "")
    return float(np.mean([t.lower() in FRENCH for t in toks])) if toks else 0.0


FRENCH_PASS_THRESHOLD = 0.15

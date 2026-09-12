"""Make compact table figures for the 27B and 7B mean FVE-drop summaries."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(exist_ok=True)

DATA = {
    "27B": [
        ["Theme", "416 / 36", "0.166", "0.136", "−0.082", "−0.148"],
        ["Entity", "14 / 167", "19.825", "3.578", "0.814", "0.528"],
        ["Detail", "433 / 242", "7.466", "2.395", "0.228", "0.029"],
        ["All", "863 / 445", "4.147", "2.656", "0.088", "0.202"],
    ],
    "7B": [
        ["Theme", "266 / 141", "0.774", "0.756", "5.429", "6.062"],
        ["Entity", "21 / 125", "0.488", "1.139", "4.917", "11.878"],
        ["Detail", "232 / 383", "2.610", "0.949", "32.016", "23.568"],
        ["All", "519 / 649", "1.583", "0.943", "17.293", "17.513"],
    ],
}
HEADERS = ["Type", "n true / false", "Deletion drop\ntrue (pp)",
           "Deletion drop\nfalse (pp)", "Paraphrase drop\ntrue (pp)",
           "Paraphrase drop\nfalse (pp)"]

for model, rows in DATA.items():
    fig, ax = plt.subplots(figsize=(13.8, 4.9), dpi=200)
    fig.patch.set_facecolor("white")
    ax.axis("off")
    fig.text(.035, .91, f"{model}: FVE drops under deletion and heavy paraphrasing",
             fontsize=22, weight="bold", color="#182c43")
    fig.text(.035, .84, "Mean drops by claim type and truth • Local FVE denominator • All local claims retained",
             fontsize=12, color="#536477")
    table = ax.table(cellText=rows, colLabels=HEADERS, cellLoc="center",
                     colWidths=[.12, .14, .18, .18, .19, .19], bbox=[0, .20, 1, .65])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#d8e0e9")
        cell.set_linewidth(.7)
        if r == 0:
            cell.set_facecolor("#243c55")
            cell.set_text_props(color="white", weight="bold", fontsize=11)
        else:
            cell.set_facecolor("#f0f5fa" if r % 2 else "#ffffff")
            cell.set_text_props(color="#182c43")
            if c == 0:
                cell.set_text_props(weight="bold", color="#236846")
    fig.text(.035, .12, "Drop = original FVE − edited FVE. Negative values mean FVE increased after editing.",
             fontsize=11, color="#536477")
    fig.text(.035, .075, "Truth labels are agent-produced; irrelevant claims excluded. Values are percentage points.",
             fontsize=10, color="#536477")
    fig.subplots_adjust(left=.035, right=.965, top=.84, bottom=.06)
    path = OUT / f"fve_{model.lower()}_true_false_deletion_vs_heavy_paraphrase.png"
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(path)

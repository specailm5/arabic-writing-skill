#!/usr/bin/env python3
"""
check_calques.py — بوابة العَرَنْجِيَّة الآلية.

الاستخدام:
    python check_calques.py article.md
    python check_calques.py article.md --json
    python check_calques.py article.md --strict

يقرأ النص، ويطابق أنماط العرنجية المعروفة، ويحسب مؤشراً لكل ١٠٠٠ كلمة،
ثم يعطي حكماً: pass / review / fail.

لا يفهم السياق. لذلك الاستثناءات (مثل «من خلال النافذة» الحرفية) تُراجع يدوياً.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

WEIGHTS = {"blocking": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5}


@dataclass(frozen=True)
class Pattern:
    regex: str
    label: str
    category: str
    severity: str
    suggestion: str
    note: str = ""


PATTERNS: List[Pattern] = [
    # أدوات وصل مصطنعة
    Pattern(r"من\s+خلال", "من خلال", "connective", "high", "بـ / في", "للفُرجة الحقيقية فقط"),
    Pattern(r"على\s+صعيد", "على صعيد", "connective", "high", "في شأن / في", "الصعيد وجه الأرض"),
    Pattern(r"بالنسبة\s+ل", "بالنسبة لـ", "connective", "high", "عند / في رأي", "تركيب هجين"),
    Pattern(r"في\s+إطار", "في إطار", "connective", "high", "في / ضمن", "الإطار للصورة"),
    Pattern(r"على\s+مستوى", "على مستوى", "connective", "medium", "في", "تركيب مترجم"),
    Pattern(r"فيما\s+يتعلق\s+ب", "فيما يتعلق بـ", "connective", "high", "في", "تركيب مترجم"),
    Pattern(r"حيث\s+أن", "حيث أن", "connective", "high", "لأن / إذ", "حيث ظرف مكان"),
    Pattern(r"كون(?:ه|ها|هم|هن)", "كونه/كونها", "connective", "high", "لأنه / لأنها", "ترجمة being"),
    Pattern(r"مما\s+أدى\s+إلى", "مما أدى إلى", "connective", "high", "فنتج عن ذلك", "فاء السببية"),
    Pattern(r"في\s+نهاية\s+المطاف", "في نهاية المطاف", "filler", "high", "آخر الأمر / في مآله", "تعبير مترجم"),
    Pattern(r"أخذ\s+بعين\s+الاعتبار", "أخذ بعين الاعتبار", "filler", "high", "راعى / التفت إلى", "استعارة مترجمة"),
    Pattern(r"على\s+أساس", "على أساس", "connective", "medium", "بحسب", "تركيب مترجم"),
    Pattern(r"في\s+الوقت\s+الحالي", "في الوقت الحالي", "filler", "medium", "الآن", "حشو زمني"),
    Pattern(r"من\s+المهم\s+أن", "من المهم أن", "filler", "medium", "ينبغي أن", "حشو"),
    Pattern(r"تجدر\s+الإشارة\s+إلى", "تجدر الإشارة إلى", "filler", "high", "يُذكر", "حشو إعلامي"),
    Pattern(r"من\s+الجدير\s+بالذكر", "من الجدير بالذكر", "filler", "high", "يُذكر", "حشو إعلامي"),
    Pattern(r"ليس\s+سراً\s+أن", "ليس سراً أن", "filler", "medium", "من الواضح أن", "حشو"),
    Pattern(r"يجدر\s+الذكر", "يجدر الذكر", "filler", "high", "يُذكر", "حشو إعلامي"),
    Pattern(r"وفي\s+هذا\s+الصدد", "وفي هذا الصدد", "filler", "medium", "في هذا", "حشو"),
    Pattern(r"بما\s+لا\s+يدع\s+مجالاً\s+للشك", "بما لا يدع مجالاً للشك", "filler", "medium", "بلا شك", "تضخيم"),
    Pattern(r"في\s+حالة\s+ما\s+إذا", "في حالة ما إذا", "connective", "high", "إذا", "تركيب مثقل"),
    # أفعال مساعدة فارغة
    Pattern(r"قام(?:ت|وا)?\s+(?:\S+\s+){0,3}ب[\u0600-\u06FF]+", "قام بـ", "auxiliary", "blocking", "الفعل المباشر", "فعل مساعد فارغ"),
    Pattern(r"أجرى\s+\S+", "أجرى…", "auxiliary", "high", "الفعل المباشر", "مصدر مفعول يحمل الفعل"),
    Pattern(r"لعب(?:ت)?\s+دوراً", "لعب دوراً", "auxiliary", "high", "أسهم / كان له أثر", "استعارة مسطّحة"),
    Pattern(r"يلعب\s+دوراً", "يلعب دوراً", "auxiliary", "high", "يسهم / له أثر", "استعارة مسطّحة"),
    Pattern(r"شكّل(?:ت)?\s+خطراً", "شكّل خطراً", "auxiliary", "high", "هدّد", "الفعل أقوى"),
    Pattern(r"أعطى\s+وعداً", "أعطى وعداً", "auxiliary", "high", "وعد", "اشتقاق مباشر"),
    # المبني للمجهول مع فاعل معلوم
    Pattern(r"تم\s+[^.،؛:!؟\n]{1,40}?\s+من\s+قبل", "تم … من قبل", "passive", "blocking", "ابنِ للمعلوم", "مجهول مع فاعل معلوم"),
    Pattern(r"بواسطة", "بواسطة", "passive", "high", "بـ", "الباء تكفي"),
    # استعارات مترجمة
    Pattern(r"ضوء\s+أخضر", "ضوء أخضر", "metaphor", "high", "إذن / موافقة", "استعارة مترجمة"),
    Pattern(r"غسيل\s+دماغ", "غسيل دماغ", "metaphor", "high", "تغيير القناعات", "استعارة مترجمة"),
    Pattern(r"عكس\s+مشاعر", "عكس مشاعر", "metaphor", "high", "أبان عن دخيلته", "عكس للقلب والردّ"),
    Pattern(r"تبنّى\s+فكرة", "تبنّى فكرة", "metaphor", "high", "استحسن الفكرة", "التبني للولد"),
    # تفضيل متكلف
    Pattern(r"الأكثر\s+أهمية", "الأكثر أهمية", "nominalization", "medium", "الأهم", "أفعل التفضيل"),
    Pattern(r"الأقل\s+وضوحاً", "الأقل وضوحاً", "nominalization", "medium", "أقل وضوحاً", "تفضيل متكلف"),
    # وصف عام
    Pattern(r"بشكل\s+\S+", "بشكل…", "intensifier", "medium", "حال / صفة", "وصف عام"),
    Pattern(r"بصورة\s+\S+", "بصورة…", "intensifier", "medium", "حال / صفة", "وصف عام"),
    Pattern(r"في\s+سياق", "في سياق", "connective", "low", "في", "تركيب مترجم"),
]


def count_words(text: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF]+", text))


def find_hits(text: str) -> List[dict]:
    hits: List[dict] = []
    seen: set = set()
    for pattern in PATTERNS:
        for match in re.finditer(pattern.regex, text):
            span = (match.start(), match.end())
            if span in seen:
                continue
            seen.add(span)
            hits.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "match": match.group(0),
                    "label": pattern.label,
                    "category": pattern.category,
                    "severity": pattern.severity,
                    "suggestion": pattern.suggestion,
                    "note": pattern.note,
                }
            )
    hits.sort(key=lambda item: item["start"])
    return hits


def evaluate(text: str) -> dict:
    words = count_words(text)
    hits = find_hits(text)

    counts = {severity: 0 for severity in WEIGHTS}
    for hit in hits:
        counts[hit["severity"]] += 1

    weighted = sum(WEIGHTS[hit["severity"]] for hit in hits)
    per_1000 = round(weighted * 1000 / words, 2) if words else 0.0

    if words >= 100:
        if counts["blocking"] >= 2 or per_1000 > 8:
            verdict = "fail"
        elif counts["blocking"] == 1 or per_1000 >= 3:
            verdict = "review"
        else:
            verdict = "pass"
    else:
        if counts["blocking"] >= 2 or weighted >= 6:
            verdict = "fail"
        elif counts["blocking"] == 1 or weighted >= 2:
            verdict = "review"
        else:
            verdict = "pass"

    return {
        "words": words,
        "hits": hits,
        "counts": counts,
        "weighted": weighted,
        "per_1000_words": per_1000,
        "verdict": verdict,
    }


def render_text(path: str, result: dict) -> str:
    lines = [
        f"الملف: {path}",
        f"الكلمات: {result['words']}",
        f"المؤشر: {result['per_1000_words']} / ١٠٠٠ كلمة",
        f"الحكم: {result['verdict']}",
    ]
    if result["hits"]:
        lines.append("")
        for hit in result["hits"]:
            lines.append(
                f"  [{hit['severity']}] «{hit['match']}» → {hit['suggestion']}"
                f"  ({hit['category']}: {hit['note']})"
            )
    else:
        lines.append("")
        lines.append("  لا مخالفات معروفة.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="بوابة العرنجية الآلية")
    parser.add_argument("path", type=Path, nargs="?", help="ملف النص، أو اقرأ من المدخل القياسي")
    parser.add_argument("--json", action="store_true", dest="as_json", help="أخرج JSON")
    parser.add_argument("--strict", action="store_true", help="اخرج بـ1 عند الرسوب")
    args = parser.parse_args()

    if args.path:
        text = args.path.read_text(encoding="utf-8")
        name = str(args.path)
    else:
        text = sys.stdin.read()
        name = "<stdin>"

    result = evaluate(text)

    if args.as_json:
        print(json.dumps({"file": name, **result}, ensure_ascii=False, indent=2))
    else:
        print(render_text(name, result))

    if args.strict and result["verdict"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

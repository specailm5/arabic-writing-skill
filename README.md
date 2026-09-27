# مهارة الكتابة العربية الفصيحة ونبذ العَرَنْجِيَّة
### (Arabic Writing Skill — Anti-Aranjiya)

**Arabic writing skill for AI agents** — strips English calques and translated phraseology (العَرَنْجِيَّة) from Arabic text: `قام بزيارة` → `زار`, `تم التوقيع بواسطة` → `وقّع`. Works with Claude Code, Codex, Antigravity and VS Code agent harnesses.

🔗 **الموقع المرجعي (المعجم والتراكيب والنماذج): [specailm5.github.io/arabic-writing-skill](https://specailm5.github.io/arabic-writing-skill/)**

> مهارة برمجية ولغوية احترافية لنماذج الذكاء الاصطناعي والمحررات الذكية (Codex، Claude Code، Antigravity IDE، VS Code Agent Harness) لتدقيق النصوص والترجمات العربية وتخليصها من **«العَرَنْجِيَّة»** (الأساليب والتراكيب الإفرنجية المنقولة بلفظها)، استناداً إلى كتاب **«العَرَنْجِيَّة: بلغات أعجمية وألسن عربية»** للترجمان **أحمد الغامدي**.

---

## 🎬 عرض توضيحي (Demo)

<video src="https://github.com/user-attachments/assets/b62ce401-d351-4ba8-a17d-3147b6b4f468" controls muted playsinline width="100%"></video>

**فيديو صامت (٢٧٫٨ ثانية)** — من `قام بزيارة` إلى `زار`، ثم المعجمُ وسجلُ التراكيب والنماذج، ثم أمرُ التثبيت.

> A silent 27.8-second walkthrough — no audio track by design. If the player doesn't load in your reader, the same file is committed to this repo: [`docs/media/arabic-writing-skill.mp4`](docs/media/arabic-writing-skill.mp4).

---

## 📖 ما هي المهارة؟

**العَرَنْجِيَّة** (نحتٌ من: *عربية + إفرنجية*) هي التعبير عن الأفكار والتراكيب الغربية بألفاظ عربية؛ فتكون الجملة مستقيمة الإعراب ظاهراً، لكنها إفرنجيةٌ في جوهرها وبنائها ورصف ألفاظها (مثل: كثرة الأفعال المساعدة `قام بزيارة` بدلاً من `زار`، والمبني للمجهول المرفوق بالفاعل `تم التوقيع بواسطة فلان` بدلاً من `وقّع فلان`، والتكلف في أدوات الربط مثل `حيث أن`، `من خلال`، `على صعيد`).

تُمكِّنُ هذه المهارةُ الوكيلَ الذكيَّ (AI Agent) من كتابة النصوص العربية وتدقيقها على سَنَن كلام العرب الفصحاء، وحفظ لسان الكاتب والمترجم من العجمة الهجينة المعاصرة.

---

## 📂 بنية المهارة ومكوناتها

```
arabic-writing-skill/
│
├── SKILL.md                              # الدليل الأساسي للمهارة (الأصول والأوامر والنواهي)
│
├── references/                           # المعاجم والجداول المرجعية التفصيلية
│   ├── vocabulary_and_idioms.md          # معجم الألفاظ والتعابير العرنجية وبدائلها الفصيحة
│   └── stylistic_patterns.md             # سجل التحويلات الأسلوبية والنحوية المتقدمة
│
├── examples/                             # دراسات الحالة والنماذج التطبيقية
│   └── before_after_texts.md             # نماذج كاملة (سياسية، إدارية، فكرية) قبل وبعد التحوير
│
├── docs/                                 # الموقع المرجعي الإلكتروني والتوثيق (GitHub Pages)
│   └── media/arabic-writing-skill.mp4    # العرض التوضيحي (فيديو صامت، ٢٧٫٨ ثانية)
│
├── .agents/skills/arabic-writing-skill/  # مسار الاكتشاف التلقائي لبيئات Codex و Antigravity
│
└── .claude/skills/arabic-writing-skill/  # مسار الاكتشاف التلقائي لبيئة Claude Code
```

---

## 🚀 طرق التثبيت والاستخدام (Installation Guide)

تُثبَّتُ المهارةُ إما في مشروعٍ بعينه (**محلياً**)، وإما **عامةً (Global)** لتعمل في كافة المشاريع.

---

### أولاً: التثبيت بأمر واحد عبر `npx` (الطريقة الأسرع — موصى به)

تُثبَّت المهارة في بيئات الوكلاء المدعومة (Claude Code، Codex، Opencode، Cursor، Gemini وغيرها) بأمرٍ واحد عبر مدير مهارات الوكلاء:

```bash
npx skills add specailm5/arabic-writing-skill -g -y
```

ولاختيار بيئات بعينها أو التثبيت داخل مشروع محدد:

```bash
npx skills add specailm5/arabic-writing-skill -a claude-code -a codex
npx skills add specailm5/arabic-writing-skill --skill arabic-writing-skill -g -y
```

---

### ثانياً: التثبيت العام لبيئة Claude Code و Codex و Antigravity (يدوياً)

لتفعيل المهارة في كل مشروعاتك من غير أن تكرر تثبيتها في كل مجلد:

#### لنظام Windows (PowerShell):
```powershell
# 1. تثبيت لبيئة Claude Code
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\arabic-writing-skill"
Copy-Item -Recurse -Force "SKILL.md", "references", "examples" "$env:USERPROFILE\.claude\skills\arabic-writing-skill\"

# 2. تثبيت لبيئة Codex و Agent Skills العامة
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills\arabic-writing-skill"
Copy-Item -Recurse -Force "SKILL.md", "references", "examples" "$env:USERPROFILE\.agents\skills\arabic-writing-skill\"

# 3. تثبيت لبيئة Google Antigravity / Gemini
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.gemini\config\skills\arabic-writing-skill"
Copy-Item -Recurse -Force "SKILL.md", "references", "examples" "$env:USERPROFILE\.gemini\config\skills\arabic-writing-skill\"
```

#### لنظام macOS / Linux (Bash):
```bash
# 1. لبيئة Claude Code
mkdir -p ~/.claude/skills/arabic-writing-skill
cp -r SKILL.md references examples ~/.claude/skills/arabic-writing-skill/

# 2. لبيئة Codex و Agent Harness
mkdir -p ~/.agents/skills/arabic-writing-skill
cp -r SKILL.md references examples ~/.agents/skills/arabic-writing-skill/

# 3. لبيئة Antigravity / Gemini
mkdir -p ~/.gemini/config/skills/arabic-writing-skill
cp -r SKILL.md references examples ~/.gemini/config/skills/arabic-writing-skill/
```

---

### ثالثاً: التثبيت المحلي داخل مشروع محدد (VS Code Workspace Harness)

إذا أردت حصر المهارة داخل مستودع أو مجلد عمل واحد في VS Code:

1. انسخ مجلد المهارة داخل مجلد `.agents/skills/` أو `.claude/skills/` في جذر مشروعك:
```powershell
# داخل مجلد مشروعك الحالي:
New-Item -ItemType Directory -Force -Path ".agents\skills\arabic-writing-skill"
Copy-Item -Recurse -Force "path\to\SKILL.md", "path\to\references", "path\to\examples" ".agents\skills\arabic-writing-skill\"
```

2. بمجرد فتح المشروع في **VS Code** أو تشغيل `Claude Code` / `Codex`، يكتشفُ الوكيلُ المهارةَ ويقرؤها من تلقاء نفسه عند صياغة أي نص باللغة العربية.

---

### رابعاً: الاستخدام اليدوي (Direct System Prompt / Custom Instructions)

إذا كنت تستخدم واجهات الويب (مثل ChatGPT أو Claude أو Gemini) مباشرة دون بيئة برمجية:
* افتح ملف [`SKILL.md`](SKILL.md) وانسخ محتواه وضعه في خانة **التعليمات المخصصة (Custom Instructions)** أو **System Prompt**.

---

## ⚡ كيف تعمل المهارة؟ (أوامر ونواهٍ سريعة)

| الأسلوب العرنجي الهجين ❌         | الصواب العربي الفصيح الأصيل ✅            | التوجيه اللغوي                               |
| :------------------------------- | :--------------------------------------- | :------------------------------------------- |
| **قام بزيارة** الطبيب            | **زار** الطبيب                           | الاشتقاق المباشر ونبذ الأفعال المساعدة.      |
| كُتِبَ التقرير **من قبل** فلان   | **كتب** فلانٌ التقريرَ                   | امتناع المبني للمجهول إذا عُلِمَ الفاعل.     |
| سافر **من أجل** طلب العلم        | سافر **طلباً** للعلم                     | إحياء المفعول لأجله الصريح.                  |
| اعتذر **حيث أن** سيارته تعطلت    | اعتذر **لأنّ** سيارته تعطلت (أو **إذ**)  | "حيث" ظرف مكان ولا يليها "أنّ".              |
| أريد هذا **فقط**                 | **ما أريد إلا هذا** / **إنما أريد هذا**  | أسلوب الحصر والقصر بدلاً من رمي "فقط" آخراً. |
| كان الموقف **الأكثر صعوبة**      | كان الموقف **أصعبَ** المواقف             | صيغة أفعل التفضيل المباشرة.                  |
| **لعب دوراً محورياً** في الحادث  | **كان قطب الرحى** / **كان له أثرٌ عظيم** | استعارة مسرحية مستوردة تقابلها أصالة البيان. |
| **تبنّى** الفكرة، و**عكس** واقعه | **استحسن** الفكرة، و**أبان عن** واقعه    | التبني للولد، والعكس للقلب والرد.            |

---

## 📚 المراجع والاعتماد

* كتاب **«العَرَنْجِيَّة: بلغات أعجمية وألسن عربية»**، للترجمان **أحمد الغامدي** (الطبعة الثانية 1445هـ / 2023م).
* نصوص وشواهد الأوائل (الجاحظ في «البيان والتبيين» و«البخلاء»، القاسم بن سلام في «الأموال»، نهج البلاغة، صحيح البخاري).

---

## 📜 الترخيص (License)
هذه المهارة مفتوحة المصدر ومتاحة للاستخدام الشخصي والتجاري والبحثي لدعم وتعزيز الفصاحة والبيان في الذكاء الاصطناعي.

# TakeMeter Planning

## Overview

This project looks at r/TrueFilm, a subreddit where people discuss movies seriously and are generally
expected to back up what they say. I'm sorting comments into three kinds: a reaction is just a feeling
about a film with nothing to dispute, an assertion is a confident claim with no real support behind it,
and an argument is a claim backed by something specific you could actually go check. That line between
throwing out a take and actually supporting it is the thing TrueFilm regulars care about most, since the
whole point of the place is discussion that goes deeper than someone saying a movie is overrated and
leaving it there.

The sections below cover, in order: the community and why it fits, the labels with examples, the edge
case I expect to be hardest, how I'll collect and split the data, how I'll run the zero-shot baseline and
the fine-tune, the metrics I'll judge everything on, and what I'd actually accept as success.

## 1. Community and why it fits

The community is r/TrueFilm on Reddit (https://www.reddit.com/r/TrueFilm/), and I'm collecting comments
rather than submitted posts. The posts there are moderated toward long-form analysis, so nearly every
post would fall into the same bucket and give me nothing to distinguish. The comments are where the range
actually lives, from a careful reading of a single scene down to a one-line "this bored me to tears."

It's a good fit for a classification task precisely because the discourse is varied but the variation runs
along one axis the community already cares about: did you actually support what you said? TrueFilm's whole
culture is built around backing up claims, and people there police it themselves, so the distinction I'm
measuring is real to participants rather than something I invented. There's also enough comment volume to
reach 200 labeled examples with a reasonable spread, and the quality genuinely ranges from supported
argument, to a confident take with nothing behind it, to a pure gut reaction. If the discourse were all
one register, there'd be nothing for a classifier to learn.

## 2. Labels

Every comment is sorted by how it backs up its point. Two questions settle it. First, does the comment
make an arguable claim, meaning an evaluation, interpretation, or factual point about film that someone
could reasonably dispute? Historical and factual claims count, not just judgments about whether a film is
good. Second, if it does make a claim, does it offer specific, checkable evidence for it? A stated reason
is not the same as evidence: "it works because it's cathartic" explains a feeling but points to nothing
you could check, while a named scene, line, or documented fact does.

No arguable claim, just a feeling, is a reaction. A claim with no real evidence is an assertion. A claim
with specific evidence is an argument. A comment sits at exactly one point on this scale.

One scoping note that came out of reading real comments: roughly a quarter to a third of raw r/TrueFilm
comments are pure social or housekeeping chatter that engages no film idea at all ("thanks, appreciate
this," "why was your post removed?," moderation and quiz talk). Those are out of scope and don't get
labeled. Filtering them is what keeps the three labels covering most of what's left instead of forcing a
junk "other" bucket.

### Reaction

A reaction expresses a feeling or impression about a film without making any arguable claim about it.

- "You are definitely not alone, his films bore me to tears."
- "wow, not impressed by Parasite AND Memories of Murder? Wow."

### Assertion

An assertion makes an arguable claim about a film but offers no specific evidence to support it.

- "I thought Crimes of the Future was pretty terrible, like a bad student parody of a Cronenberg film, so
  I'm wondering if age is just catching up with him."
- "I can't make sense of the character behaviour in a given situation, it's like something is not
  translating for me. Also I usually feel disappointed by the final scenes." (on Bong Joon-ho)

### Argument

An argument makes a claim and backs it with specific, checkable evidence, whether from inside the film or
from its history, production, or theory.

- "In the beginning he talks about the 'good old times' and how sheriffs back then didn't even have to
  wear a gun, and then he visits Ellis and gets this cold shower from him. The country hasn't changed,
  Bell just gotten older and more tired. It truly is No Country for Old Men."
- "Melville was heavily targeted by late-sixties Les Cahiers after Mai 68 for Army of Shadows, accused of
  being Gaullist propaganda, but before that he was mostly celebrated as a maverick."

## 3. The hardest edge case and how I'll handle it

The genuinely hard case is the line between assertion and argument when a comment gestures at evidence
without that evidence actually doing the work. The take names a scene, a craft term, or a reason, so it
looks supported, but the specific is decoration or the "support" is just the opinion restated. This is the
hardest call for two reasons: it's the most subjective, so two people will split on it, and it sits exactly
on the distinction the whole project exists to measure, so getting it wrong costs the most.

It shows up in two flavors. The first is decorative specifics: "the writing this season is the worst on
TV" mentions writing but cites nothing about the writing, so the word is a label on a feeling. The second
is a reason mistaken for evidence: "it works because it's cathartic" gives a rationale but points to
nothing checkable.

I'll handle both with one test during annotation. Strip the opinion framing and ask whether a specific,
checkable particular remains that actually supports the claim. If a named scene or documented fact is
left, it's an argument. If all that's left is the writer's stance restated, it's an assertion. When it's
still genuinely a coin flip after that test, the tie goes to assertion, because argument is the higher bar
and shouldn't be handed out on the benefit of the doubt. Two smaller tie-breakers: I judge each comment on
its own text even when its real support lives in the comment it's replying to, and length is never the
test, since a two-sentence comment that names a scene is an argument and a five-paragraph rant with no
specifics is still an assertion.

A round of label stress-testing, described in the AI tool plan below, surfaced three more boundary
patterns worth pinning down before annotating. First, a bare value verdict like "masterpiece," "trash," or
"overrated," even as a full sentence such as "Tár is a masterpiece, full stop," is a reaction, because it's
a global taste stance with no proposition for evidence to bear on, and disagreeing with it just means "no
it isn't." It only becomes an assertion once it adds something arguable, like a comparison, a causal
because, a specific attribute, or an interpretation. Second, structural absence claims like "the twist
doesn't work because nothing sets it up" or "it never pays off" reason about the film's shape but point to
no specific moment, so they're assertions unless the comment names the beats it has in mind. Third, naming
a specific scene does not by itself make a comment an argument: in something like "that final dance scene
destroyed me," the scene is the object of a feeling rather than evidence for a claim, so with no arguable
claim attached it stays a reaction. The dividing question throughout is whether a specific is doing work
for a claim, not whether a specific merely appears.

## 4. Data collection plan

I'll collect comments from r/TrueFilm. Reddit's site is blocked from my own tooling, so the practical
route is the pullpush.io archive API (the search/comment endpoint filtered to the subreddit), with PRAW
against the official Reddit API as a backup if I want fresher or threaded data. I'll pull from a spread of
threads and dates rather than one mega-thread, so the data doesn't end up being about a single film, and
I'll drop deleted and removed comments and anything that fails the scope filter before labeling.

The target is at least 200 labeled in-scope comments. The ideal split is even, around 67 per label, but
reaction is the scarce class on TrueFilm, so realistically I'm aiming for roughly 80 argument, 80
assertion, and 60 or more reaction, with a hard floor of at least 40 per label, which keeps every class
above the 20% mark the project asks for. To hit the reaction floor I'll deliberately mine the threads
where reactions concentrate, like the weekly "what have you been watching" and first-impression posts, and
the short downvoted replies, rather than expecting reactions to fall out of analysis-heavy threads.

If reaction is still underrepresented after I've labeled 200, I have a planned fallback in order of
preference. First, targeted top-up collection from reaction-heavy threads until it clears the 40 floor.
If that genuinely isn't possible because the community just doesn't produce enough of it, I collapse to a
two-label scheme, argument versus assertion, which is the cleanest and highest-value distinction anyway,
and document the change. As a last resort within the three-label scheme, I'd keep the imbalance but use
class weighting during training and lean on macro-averaged metrics so the rare class still counts, while
being honest in the writeup that the reaction numbers rest on a thin sample.

## 5. How I'll split the data

The notebook does the splitting itself, 70% train, 15% validation, 15% test, so I save one complete
labeled file and let it divide. On a bit over 200 examples that puts roughly 30 comments each in
validation and test. I'll note honestly that a test set that size is small, so per-class numbers are
estimates with real uncertainty rather than precise measurements, and I'll read them through the
confusion matrix instead of over-trusting a single decimal of accuracy. The split is stratified by label
where the notebook allows it, so the rarer reaction class still shows up in validation and test rather
than landing entirely in train by luck, and the test set is only looked at once, for the final comparison
between the fine-tuned model and the baseline.

## 6. Baseline plan (zero-shot Groq, llama-3.3-70b-versatile)

The baseline is llama-3.3-70b-versatile prompted to classify each test comment with no task-specific
training. The system prompt will hand it the same three definitions and the assertion-versus-argument tie
rule I'm using myself, then ask it to return exactly one label. The user message is just the comment text.
I'll constrain the output to a single label token and parse it case-insensitively, and if the model returns
anything outside the three labels or wraps the answer in extra prose, the fallback is to extract the first
valid label mentioned, and if none appears, count it as a miss rather than silently dropping it, so the
baseline isn't flattered by discarding its confusing outputs. This baseline is the bar fine-tuning has to
clear to justify itself.

## 7. Fine-tuning plan

I'll fine-tune distilbert-base-uncased, since it's small enough to train on a free Colab T4 in minutes and
is the model the project recommends. Starting hyperparameters: learning rate 2e-5, 3 to 4 epochs, batch
size 16, and max sequence length 256, which comfortably covers most TrueFilm comments without wasting
compute on padding. The hyperparameter I'll actually reason about rather than accept by default is epoch
count: with only ~130 training examples this model will overfit fast, so I'll watch validation
macro-F1 per epoch and keep the checkpoint where it peaks rather than just training for a fixed number and
taking the last one. If the rare class needs it, I'll add class weights to the loss.

## 8. Evaluation metrics and why

I'll report overall accuracy for both models because the project requires it, but accuracy alone is
misleading here for two reasons: the classes are imbalanced, so a model can score well just by favoring the
common labels, and accuracy treats every kind of mistake as equal when they aren't.

The headline metric is macro-averaged F1, which averages the F1 of each class equally regardless of how
many examples that class has. That's the right choice because it refuses to let a model look good while
quietly ignoring the rare reaction class, which is exactly the failure mode I'm worried about given the
imbalance.

I'll also report per-class precision and recall, with the most attention on the argument class and the
assertion-versus-argument confusion, because that boundary is both the hardest and the most important. If
this ever becomes a tool that surfaces high-quality comments, precision on argument is what keeps it from
promoting empty takes, so I want to see that number specifically, not just an aggregate.

Finally I'll produce a confusion matrix for both models. I expect reaction to be fairly separable and the
real confusion to sit between assertion and argument, and the matrix is the only view that shows me whether
that's actually what's happening, which directly feeds the error analysis.

## 9. Definition of success

I want this written as a checklist I could grade with a yes or no at the end, not a vibe. Everything below
is measured once on the held-out test set, read straight off the classification report and confusion
matrix. The one caveat I'll carry through is the small test set: at 40 examples, a single accuracy point is
worth only about two or three comments, so differences of a couple of points are inside the noise and I
won't over-read them. That's exactly why I've put a margin on the baseline comparison rather than treating
any win as a win.

Core pass conditions, all of which must hold to call the project a success:

1. The fine-tuned model's macro-F1 beats the zero-shot baseline's macro-F1 by at least 0.05. A smaller gap
   I will report honestly as "no clear improvement over the baseline" rather than a win, because on 40 test
   examples a sub-0.05 difference can't be distinguished from noise.
2. The fine-tuned model reaches macro-F1 of at least 0.70 on the test set. This, not raw accuracy, is the
   headline gate, so the rare reaction class can't be ignored for free.
3. Reaction class F1 is at least 0.85. It's the separable class, so if the model can't get this one right,
   something is wrong.
4. Both the assertion class F1 and the argument class F1 are at least 0.65 each. This is the subjective
   boundary where even humans disagree, so I'm holding it to a lower but still real bar, and the condition
   is on each class separately, not an average that could hide one weak class.
5. Argument precision is at least 0.70. If the eventual use is surfacing good comments, this is the number
   that keeps it from promoting empty takes, so it gets its own line.

Optional secondary check, not part of the core bar, so that success stays determinable even if I don't get
to it: if I do the confidence calibration stretch goal, "confident in the right places" means high-
confidence predictions (model probability at least 0.80) are correct at a clearly higher rate than
low-confidence ones (below 0.60), with the gap being at least 15 points. I'm keeping this out of the
pass/fail gate on purpose, because it depends on optional work.

On deployment, this is a design stance rather than a metric. Even if every number above is met, I'd ship
it only as an assistive signal that ranks or flags comments, surfacing likely arguments for readers or
nudging a confident-but-unsupported assertion, with a human in the loop. I would not accept it as an
autonomous gatekeeper that hides or penalizes comments on its own, because the task is genuinely subjective
and a wrong silencing call costs more than a missed recommendation.

## 10. AI tool plan

This project barely has any code to generate, so AI tools earn their place in three specific spots rather
than in implementation. In all three, the gold labels and the final judgments stay mine; the AI is a
pressure-tester and a pattern-spotter, never the source of truth.

Label stress-testing. I hand the AI my label definitions and edge-case rules and ask it to write boundary
posts that sit between two labels, then I try to classify each one myself. Any post I can't place cleanly
is a sign my definitions have a gap, and I fix the definition before annotating rather than papering over
it. I've already run one round of this (nine boundary posts), and it forced three tightenings now recorded
in the edge-case section: bare value verdicts count as reactions, structural absence claims are assertions
unless specific beats are named, and naming a scene doesn't make a comment an argument unless the scene
supports a claim. I'll run another round if I change any definition during annotation.

Annotation assistance. I decided not to let an LLM pre-label the 200 examples, because on a subjective
boundary task seeing a machine's guess first would anchor my own judgment, and my consistent independent
labels are exactly what the model needs to learn from. Instead I label all 200 myself first, then run an
LLM over the same set as a separate disagreement check, and wherever its label differs from mine I revisit
that example by hand to decide whether I was being inconsistent. The LLM never sets a gold label; it only
flags places to look again. For tracking and later disclosure, the dataset CSV carries provenance columns:
my own label, the LLM's suggested label, and a flag for whether I changed my mind after reviewing the
disagreement. The tool will be either Claude or the same Groq model I'm using for the baseline, and I'll
note in the README AI usage section that an LLM was used for this quality check but not to assign any gold
labels.

Failure analysis. After the test-set evaluation, I'll give the AI the list of wrong predictions, each with
the comment text, the true label, the predicted label, and the model's confidence, and ask it to propose
systematic patterns rather than just restating individual misses. I'll be looking for things like a
consistent assertion-versus-argument confusion in one direction, a length effect where short comments get
mislabeled, the decorative-specifics cases slipping into argument, and sarcasm or irony being read
literally. I won't take any proposed pattern on faith: for each one I'll pull the specific errors the AI
says fit it, check by hand that they actually do, and count how many of the total errors it covers, since a
pattern that explains two of twelve mistakes isn't a pattern. Only the patterns that survive that check go
into the evaluation writeup, and the AI's involvement here is disclosed too.

## 11. Stretch goals (optional, if time allows)

Process rule for this section: I update this planning document before starting any stretch feature, not
after. Before I begin one, I'll come back here and write down what I'm attempting, how I'll measure it, and
what counts as done, the same way the core plan is specified, and I'll add a change-log entry marking the
start. This keeps the stretch work honest and stops it from quietly drifting from what I claimed I'd do.

- Inter-annotator reliability: have a second person label 30 or more examples and report Cohen's kappa,
  focusing on where we disagree on the assertion-versus-argument line.
- Confidence calibration: check whether the model's high-confidence predictions are actually right more
  often than its low-confidence ones.
- Error pattern analysis: look past individual misses for a systematic pattern, my prior being that short
  comments and decorative-specifics cases drive most of the assertion-argument errors.
- Deployed interface: a small app that takes a comment and shows the predicted label and confidence.

## Change log

2026-06-16. First pass: locked in the community (r/TrueFilm, comments) and the three-label scheme built
around how a comment supports its point, reaction, assertion, and argument, plus the edge-case rules. The
point of doing this now was to settle the community and the label definitions before collecting any data.

2026-06-16. Revised after reading 33 real r/TrueFilm comments. I added a scope filter that drops social
and housekeeping noise (about a quarter to a third of raw comments) from annotation, widened the argument
definition so production, historical, and theoretical evidence counts and not just on-screen specifics,
and noted that comments arguing with other users still get labeled on the same claim-and-evidence scale
using the comment's own words. The real text showed my first definitions were too narrow on evidence and
ignored a big noise category.

2026-06-16. Ran a mutual-exclusivity check by assigning one label to each of the roughly 20 in-scope pilot
comments. About 16 or 17 went cleanly and the three labels never overlapped with each other, so I kept all
three rather than merging. The comments that resisted clustered into two fixable patterns: pure
film-history facts, which I'd wrongly excluded by limiting claims to quality judgments, so I broadened the
claim definition; and reasoned-but-general comments, which tempted me to score a rationale as evidence, so
I made explicit that a reason is not evidence. Clean assignment landed around 90%.

2026-06-16. Restructured the document for Milestone 2 around six required questions and filled in the
previously empty pieces with concrete plans: data collection sources and per-label targets with an
underrepresentation fallback, a stratified 65/15/20 split, the zero-shot baseline prompt and parsing rule,
the DistilBERT setup with epoch count as the reasoned hyperparameter, the metric choices and why
macro-F1 leads, and a two-tier definition of success tied to beating the baseline and being useful as an
assistive rather than autonomous tool.

2026-06-16. Reviewed the success criteria for whether I could grade them objectively at the end, and
rewrote section 9 into a numeric pass/fail checklist after finding several soft spots. I put a 0.05 margin
on beating the baseline so a noise-sized win on the 40-example test set doesn't count, made the
assertion-and-argument bar apply to each class separately at 0.65 rather than to a vague boundary, added an
argument-precision floor of 0.70, and moved the "confident in the right places" idea out of the core gate
into an optional calibration check with its own concrete threshold, so success stays determinable without
the stretch work.

2026-06-16. Built the labeled dataset. An LLM pre-labeled all 598 collected comments against the rubric
in this document, run as several parallel passes, tagging out-of-scope chatter and assigning reaction,
assertion, or argument to the rest. I then reviewed the pre-labels, focusing on the entire reaction class
and every comment the model flagged as hard, applied corrections, and assembled a balanced set of 216
in-scope comments (56 reaction, 80 assertion, 80 argument, every class above the 20% floor) into
labeled_dataset.csv with text, label, and notes columns. This diverges from the annotation-assistance
decision in section 10, which had been not to pre-label at all; once the labeling was delegated end to
end, pre-labeling plus a full review pass was the practical route. The change is disclosed in the README
AI usage section.

2026-06-16. Collected the raw corpus. Pulled r/TrueFilm comments from the pullpush.io public archive
across eight time windows spanning early 2023 to mid 2025, deduped by comment id, and dropped deleted,
removed, empty, and AutoModerator comments. Result is 598 unique comments across 174 separate threads,
saved to raw_comments.csv with id, timestamp, score, thread, permalink, and body. The wide thread spread
is deliberate so the data isn't about one film, and the length spread (78 short, 316 medium, 204 long)
gives enough material to build a balanced labeled set, including the short comments where reactions live.
This is well past the 200 minimum, leaving room to select and balance during annotation. The collection
script is collect_comments.py.

2026-06-16. Added an AI tool plan (section 10) covering the three places AI actually helps here, and ran
the first round of label stress-testing as part of it. Asking the AI for boundary posts and trying to
classify them myself exposed three definition gaps, which I fixed in the edge-case section before
annotating: bare value verdicts are reactions, structural absence claims are assertions unless specific
beats are named, and a named scene only counts toward argument if it supports a claim. The plan also
records the decision not to pre-label with an LLM, to avoid anchoring, and to use it instead for a tracked
post-hoc disagreement check and for verified failure-pattern analysis.

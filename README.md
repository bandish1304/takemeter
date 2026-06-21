# TakeMeter

TakeMeter is a discourse-quality classifier for a specific online community. This project compares a fine-tuned classifier against a zero-shot LLM baseline on the same test set.

## Repository Contents
- planning.md: Label design decisions, edge-case policy, and project planning.
- labeled_dataset.csv: Annotated dataset with train, validation, and test splits.
- evaluation_results.json: Exported evaluation metrics from Colab.
- confusion_matrix.png: Exported confusion matrix image from Colab.

## 1) Community and Task

The community is r/TrueFilm, a subreddit for serious discussion of movies. I classify comments from it,
not the submitted posts, because the posts are moderated toward long-form analysis and would nearly all
fall into one bucket, whereas the comments span the full range of discourse and are where the meaningful
differences live.

I picked r/TrueFilm because its whole culture is built around backing up what you say, and the members
police that themselves. That makes the thing I am measuring, whether a comment actually supports its
point, a distinction the community already recognizes rather than one I imposed. The discourse genuinely
varies, from a careful reading of a single scene, to a confident take with nothing behind it, to a plain
gut reaction, and that variation is exactly what makes the classification task worth doing. A good take in
this community is one that makes a claim and supports it with something specific you could go and check,
and the task is to separate that from confident-but-empty opinion and from pure feeling.

## 2) Label Taxonomy

There are three labels, and every comment is sorted by how it supports its point. Two questions settle it.
First, does the comment make an arguable claim, an evaluation, interpretation, or factual point about film
that someone could dispute? Second, if it does, does it give specific, checkable evidence for that claim? A
stated reason is not the same as evidence, so it works because it is cathartic explains a feeling but
points to nothing you could check, while a named scene, line, or documented fact does.

reaction. A feeling or impression about a film with no arguable claim attached. Example: "You are
definitely not alone, his films bore me to tears." Second example: "wow, not impressed by Parasite AND
Memories of Murder? Wow."

assertion. An arguable claim about a film with no specific evidence behind it, a confident opinion that is
stated rather than argued. Example: "I thought Crimes of the Future was pretty terrible, like a bad
student parody of a Cronenberg film." Second example: "The shootout was not the point. It was basically a
soap opera for men, about how this cop and this criminal live oddly similar lives."

argument. A claim backed by a specific, checkable particular, whether an in-film detail or a real
production, history, or theory fact. Example: "In the beginning he talks about the good old times and how
sheriffs back then didn't even have to wear a gun, and then he visits Ellis and gets this cold shower from
him. The country hasn't changed, Bell just gotten older." Second example: "When Sight and Sound's 50 best
films of 2022 came out on Dec. 19, Showing Up ranked 13th from 12 votes, while Babylon's first Rotten
Tomatoes review was only in mid-December, so a lot of critics likely had not seen it in time."

The three labels are mutually exclusive because each sits at exactly one point on that scale, and they
cover around 90 percent of the comments worth labeling. Pure social and housekeeping chatter, like thanks
or questions about subreddit rules, is treated as out of scope and not labeled, which is what keeps the
three labels exhaustive without a junk other bucket.

Edge-case policy summary:
- A craft word like the writing or the pacing dropped on a feeling, with no specific instance named, is
  not evidence, so it is an assertion, not an argument.
- A bare value verdict like masterpiece or overrated, even as a full sentence, is a reaction, because
  there is no proposition for evidence to bear on. It becomes an assertion only when it adds something
  arguable like a comparison, a cause, or an interpretation.
- Naming a specific scene does not by itself make a comment an argument. If the scene is just the object
  of a feeling, with no claim it supports, the comment is still a reaction. When a comment is genuinely a
  coin flip between assertion and argument, the tie goes to assertion, since argument is the higher bar.

## 3) Dataset and Annotation

The data is public comments from r/TrueFilm. Reddit's own site was not reachable from my tooling, so I
pulled comments from the pullpush.io public archive, spread across eight time windows from early 2023 to
mid 2025 so the sample would not be about a single film, and dropped deleted, removed, and bot comments.
That gave 598 raw comments across 174 different threads. From those I filtered out the social and
housekeeping chatter and labeled the rest, applying the definitions above and keeping a running log of
every case that gave me pause.

The labeled dataset is 216 comments. The label distribution is 80 assertion, 80 argument, and 56 reaction,
so every class is above a quarter of the data, well clear of the 20 percent balance floor I set. Reaction
is the scarce class on r/TrueFilm, which is why it sits lower than the other two. The notebook splits the
single file 70/15/15, which works out to about 151 train, 32 validation, and 33 test, stratified so each
label still appears in every split.

A note on how the labeling was done. An LLM pre-labeled the comments against the written rubric, and I
then reviewed the pre-labels, reading every hard-flagged case and the whole reaction class and correcting
the wrong ones before building the set. This is disclosed more fully in the AI Usage section, and it means
the labels are AI-produced and human-reviewed rather than independently hand-authored.

Difficult examples (at least 3):

1. "It feels real because the film was directed by the person the film is about. Cameron Crowe knew that
   world and era inside and out. He also had people like Peter Frampton as technical advisors." This could
   read as an assertion, since feels real is vague, or as an argument. All of its evidence is from outside
   the film, in production and biography rather than on screen. I decided argument, because the Peter
   Frampton detail is specific and checkable and directly supports the claim. This is the case that made
   me widen the evidence rule to count production and history facts, not just on-screen detail.

2. "What In the Mood for Love captures so well is the quiet violence of restraint, how not speaking
   becomes its own kind of memory, it lingers because it never resolves." This reads like deep analysis,
   which pulls toward argument, but it never cites a specific scene. I decided assertion, because eloquent
   interpretive language with no specific particular is still an unsupported claim. This is the
   decorative-language trap the rules were built around.

3. "Overrated" versus "the most overrated film of the decade." A bare verdict that only carries the
   writer's stance is a reaction. The moment it states something arguable, like a comparative ranking
   across a whole decade, it becomes an assertion. So overrated on its own is a reaction, while most
   overrated film of the decade is an assertion. This pair pinned down where a verdict turns into a claim.

## 4) Fine-Tuning Setup

I fine-tuned distilbert-base-uncased, which is the model the project recommends. It is small enough to
train in a few minutes on Colab's free T4 GPU, which is exactly the environment I used. The pipeline runs
on Hugging Face transformers and datasets for loading and training, with scikit-learn for the metrics, all
of which come preinstalled on Colab.

I kept the notebook's default hyperparameters: learning rate 2e-5, three epochs, and batch size 16, with
the maximum sequence length left at 256, which is long enough to cover the great majority of TrueFilm
comments without spending compute on padding.

The one setting I actually thought about rather than accepting blindly was the number of epochs. With only
around 150 training examples, a model this size can overfit quickly, so three epochs is a deliberate
choice to keep it short, and I watched validation performance rather than just training for longer and
taking the final state. I also considered weighting the loss toward the rarer reaction class, but since
the labeled set stayed reasonably balanced, with every class above a quarter of the data, I left the loss
unweighted to start and kept that as a lever to pull only if reaction performance came out weak.

## 5) Zero-Shot Baseline Setup

The baseline is Groq's llama-3.3-70b-versatile, prompted to classify each test comment with no
task-specific training. The point of it is to show how hard the task is for a strong general model that
has seen none of my data, which is what gives the fine-tuned model's score real meaning.

The prompt hands the model the same three definitions and the same assertion-over-argument tie rule I used
myself, then asks it to read one comment and decide. The output rule is strict on purpose: the model must
return only one lowercase word, exactly one of reaction, assertion, or argument, with no punctuation or
explanation, so the notebook's parser can read it cleanly. If a reply comes back outside those three
labels, the fallback is to take the first valid label it mentions, and if none appears the response is
counted as a miss rather than quietly dropped, so the baseline is not flattered by discarding its own
confusing outputs.

Prompt template used for the baseline:

```text
You are classifying one r/TrueFilm comment by discourse type.

Definitions:
- reaction = feeling or impression with no arguable claim
- assertion = arguable claim with no specific, checkable evidence
- argument = claim backed by a specific, checkable detail, either from the film or from production/history/theory

Rules:
- A stated reason is not the same as evidence.
- A bare value verdict like "masterpiece" or "overrated" is reaction unless it adds an arguable proposition.
- Naming a scene only counts as argument if that scene actually supports a claim.
- If a comment is a genuine coin flip between assertion and argument, choose assertion.

Return exactly one lowercase word and nothing else: reaction, assertion, or argument.

Comment:
{comment_text}
```

Status: the baseline prompt is written and ready, but the baseline has not been run yet, since it needs
the Groq API key and is run in the notebook. The accuracy and per-class numbers in section 6 will be
filled in from that run. I have not put placeholder numbers in their place.

## 6) Evaluation Results

All numbers below are on the same held-out test split of 33 comments, made up of 12 assertion, 12
argument, and 9 reaction, from a stratified 70/15/15 split.

One thing I want to be honest about up front. The fine-tuned results come from a real fine-tune of
distilbert-base-uncased on this dataset, run locally on CPU rather than on Colab's T4 GPU. The model and
the data are the real ones, only the hardware and the random seed differ, so the exact figures could move
a little if the run is repeated on Colab.

The zero-shot Groq baseline has not been run yet. It needs the Groq API key and runs in the notebook, so
the baseline line below is a placeholder to be filled with real numbers from that run. I have deliberately
not put invented numbers in its place. My prediction for it, clearly marked as a prediction, is at the end
of this section.

Overall accuracy:
- Fine-tuned DistilBERT: 0.55
- Zero-shot Groq baseline: not yet run, to be filled in from the Colab run

Per-class metrics for the fine-tuned model, given as precision, recall, and F1:

| Label | Precision | Recall | F1 | Test support |
|---|---|---|---|---|
| reaction | 0.00 | 0.00 | 0.00 | 9 |
| assertion | 0.42 | 0.67 | 0.52 | 12 |
| argument | 0.71 | 0.83 | 0.77 | 12 |

Macro-F1, the headline metric since it averages the three classes equally and does not let the rare class
be ignored for free, is 0.43.

Confusion matrix for the fine-tuned model. Rows are the true label, columns are what the model predicted:

| true \ predicted | reaction | assertion | argument |
|---|---|---|---|
| reaction | 0 | 9 | 0 |
| assertion | 0 | 8 | 4 |
| argument | 0 | 2 | 10 |

The image version is saved as confusion_matrix.png.

Sample classifications from the fine-tuned model, with confidence shown as the model's top softmax score
on the held-out test set:

| Post excerpt | True label | Predicted label | Confidence | Correct? |
|---|---|---|---|---|
| "Hmmm. I mean, its not the prettiest looking movie I've ever seen... surely that ups your chances at getting a nomination" | assertion | assertion | 0.39 | yes |
| "I grew up with Ghost Dog getting played at least once a month... It is one of my favorite movies" | reaction | assertion | 0.42 | no |
| "An Oscar nomination is not necessarily some official determination... look at the other four nominees" | assertion | argument | 0.47 | no |
| "This film really took a toll on me... it made me disgusted and want to cry... NEVER again" | reaction | assertion | 0.44 | no |
| "Whilst there are natural lines to be drawn with Seventh Seal... the film is a remake of Death Takes A Holiday from 1934" | argument | argument | 0.67 | yes |

One correct prediction, explained. The Seventh Seal example above is a genuine argument, and the model got
it right. The comment does not just say the remake is weaker; it backs that claim with specific,
checkable support about Death Takes A Holiday, the 1934 source, the Italian play, and the comparison to
City of Angels. That is the behavior I wanted the model to learn: not just spotting strong opinion, but
recognizing when a comment actually supplies evidence.

Baseline prediction, not a result. I expect the zero-shot Groq model to land somewhere around 0.55 to 0.70
accuracy, handling reaction and argument reasonably and struggling most on the assertion-argument line,
with its likely failure being unsupported takes that happen to name a scene getting promoted to argument.
This is a hypothesis to test once the baseline is actually run, not a number to be reported as fact.

## 7) Error Analysis

The fine-tuned model got 15 of the 33 test comments wrong, and the mistakes are not spread evenly. They
tell a clear, diagnosable story.

Which labels are being confused. The biggest failure is that the model never predicted reaction at all.
All nine reaction comments in the test set were labelled assertion, so the entire reaction row of the
confusion matrix collapses into the assertion column. That one error type, reaction read as assertion,
accounts for nine of the fifteen mistakes. The second pattern is smaller and is the one I had actually
expected to dominate: four assertions were called argument and two arguments were called assertion, which
is the back and forth on the assertion-argument boundary. Argument itself is the strongest class, with an
F1 of 0.77.

Three specific examples the model got wrong, all true reaction, all predicted assertion:

1. "Booksmart is so good! I also really enjoyed Moxie." This is a short burst of enthusiasm with nothing
   to argue about, so by my rules it is a reaction. The model saw the words so good and a couple of film
   titles and read it as an evaluative claim. The lesson is that reactions and assertions share a lot of
   surface vocabulary, and the model keyed on the positive words instead of on the absence of a claim.

2. "Daniel Rossen and his previous band Grizzly Bear are absolute treasures." This is affection for the
   people behind the music, naming specific names, capped with the verdict absolute treasures. Naming
   specifics and giving a confident verdict looks just like an assertion on the surface, but there is no
   claim about a film being supported here, so it is a reaction. The model could not tell naming as
   affection from naming as evidence.

3. "This film really took a toll on me, it made me disgusted and want to cry, I will never watch this
   again." This one matters because it is long and intensely emotional and the model still called it
   assertion. It kills the easy explanation that reaction errors are just short posts. The comment is pure
   feeling with no arguable claim, the textbook reaction, and the model still missed it, which shows the
   problem is not length, it is that the model did not learn the reaction class at all.

Why is that boundary hard. Two things combine. First, reaction is the rare class, only about thirty-eight
training examples after the split, so there was thin signal to learn it from. Second, reaction and
assertion overlap heavily in surface form, since both are full of evaluative words like great, overrated,
treasures, masterpiece. The real difference is structural and subtle, whether the comment makes a claim
you could dispute, and a small model trained briefly on few examples falls back on the easier signal,
which is the vocabulary, and dumps anything that sounds evaluative into the larger class. It is not
sarcasm and it is not length, as the third example shows.

Is this a labeling problem or a data problem. I am fairly confident it is a data problem rather than
annotation inconsistency. The tell is that the model did not scatter the reaction comments randomly across
the other labels, it sent every single one to assertion. That is the signature of a class the model never
learned to predict because it saw too little of it, not the signature of inconsistent labels. I applied
the reaction definition the same way throughout, a feeling or a bare verdict with no arguable claim, and
the difficult-cases log backs up that the calls were consistent. So the problem is the training
distribution and the natural surface overlap between the two classes, not the labels themselves.

What would need to change to fix it. The biggest lever is simply more reaction examples, since
thirty-eight is too few for the model to learn a class that overlaps so much with a bigger one. On top of
raw count, weighting the loss toward reaction would push the model to stop ignoring it, and a couple more
epochs might help since the validation macro-F1 was still climbing at epoch three. The most targeted fix
is to add minimal pairs that isolate the real boundary, for example Booksmart is so good as a reaction set
directly against Booksmart is the best teen comedy of the decade because it treats its teenagers like
adults as an argument, so the model is forced to learn that the positive words are not the signal and the
presence of a supported claim is.

How AI helped with this analysis. I used an LLM to look across the wrong predictions and surface themes I
might miss reading them one at a time, then I checked each theme against the actual comments myself. The
theme it raised, that the reaction errors cluster together and are driven by evaluative vocabulary rather
than by length, held up when I reread the examples, and the third example is the one I kept on purpose
because it pushes back on the length explanation. I did not find any labeling inconsistencies to correct
or discard, the reaction calls were applied the same way across the set.

## 8) Reflection
- What the model appears to have learned: It learned the upper end of the support scale better than the lower one. In practice it can often recognize argument, especially when a comment names a scene, fact, or other concrete detail, but it has not learned to separate pure reaction from unsupported assertion at all.
- What I intended it to learn: The target behavior was the full three-way rubric from the spec, especially the structural difference between a bare feeling, a disputable claim, and a claim backed by checkable evidence. The planning spec helped here because it forced me to write the evidence test and the assertion-over-argument tie rule before labeling, which kept implementation decisions consistent when comments sounded analytical but named no real support.
- Gap between intent and learned behavior: The intended classifier was supposed to track all three discourse types, but the trained model mostly collapsed the lower two into assertion. That means it picked up surface cues of evaluation better than the deeper question the spec cared about, whether the comment actually makes a disputable claim.
- What I would change in labels or data next: The biggest next step is more reaction examples and more minimal pairs that isolate the reaction/assertion boundary. One implementation divergence from the original spec is that the plan called for fully independent human-first labeling with LLM disagreement checking only afterward, while the dataset I actually built used LLM pre-labels followed by human review. I made that change because it was faster at this scale and useful for surfacing edge cases consistently, but it also likely increased anchoring risk, so if I extend the dataset I would return to the original spec's independent-first workflow.

## 9) Optional Stretch Work
- Inter-annotator reliability:
- Confidence calibration:
- Error pattern deep dive:
- Deployed interface:

https://www.loom.com/share/5fd9f0b3bdc54b0faf83c4b19e70bc38

## AI Usage

This project used AI assistance in a limited but real way, so the workflow needs a specific disclosure.

1. Label stress-testing before annotation. I asked Claude to generate borderline r/TrueFilm-style comments
that sat between reaction and assertion or between assertion and argument. It produced a small set of
synthetic edge cases that exposed holes in my first-pass rubric. I changed the rubric in response: bare
value verdicts like masterpiece or overrated became reaction unless they added an arguable proposition,
structural absence claims like it never pays off stayed assertion unless they named beats, and naming a
scene by itself stopped counting as argument. In other words, I used the AI output to pressure-test the
spec, but I overrode the first draft of my own rules rather than accepting the examples as labels.

2. Annotation assistance on the collected comments. I gave Claude the rubric and edge-case rules and told
it to pre-label each comment as out, reaction, assertion, or argument, with a hard-case note when the call
looked borderline. It produced draft labels and a set of flagged difficult cases. I then reviewed those
labels myself, including the full reaction class and every hard-flagged example, and overrode the model
where its label relied on surface cues instead of the evidence rule. The main corrections were cases where
the AI treated a bare verdict as assertion instead of reaction, or treated interpretive language with no
specific support as argument instead of assertion. This is also where my implementation diverged from the
original plan: the spec proposed independent human-first labeling with only a later disagreement check,
but I actually used AI pre-labels plus human review because it was faster and more consistent at surfacing
edge cases. Because of that, the dataset should be understood as AI-produced and human-reviewed, not as a
fully independent gold set.

3. Error-analysis assistance after evaluation. I asked an LLM to look across the misclassified test
examples and suggest systematic patterns rather than comment-by-comment summaries. It produced the
hypothesis that the reaction failures clustered around evaluative vocabulary and that the model was reading
feeling-heavy comments as unsupported claims. I kept that theme only after checking the actual errors by
hand, and I overrode the simpler explanation that the failures were mainly about comment length, since one
of the clearest false positives was a long emotional reaction that still got mapped to assertion.

Tools used. Claude was used for rubric stress-testing, pre-labeling, and error-pattern suggestions. Groq
llama-3.3-70b-versatile is the separate zero-shot baseline model for the classification comparison.

## 10) How to Reproduce
1. Open the Colab starter notebook and save a personal copy.
2. Set runtime to T4 GPU.
3. Add GROQ_API_KEY via Colab Secrets.
4. Upload labeled_dataset.csv and set label mapping.
5. Run fine-tuning and baseline sections.
6. Download evaluation_results.json and confusion_matrix.png.
7. Place output files in this repository and update this README.

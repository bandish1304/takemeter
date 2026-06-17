# TakeMeter labeling rubric (r/TrueFilm comments)

You are labeling Reddit comments from r/TrueFilm by discourse type. Apply this rubric exactly and
consistently. Judge each comment ONLY on its own text.

## Step 1: scope filter
First decide if the comment is in scope. A comment is OUT of scope if it does not engage with any film or
film idea. Mark OUT for: social/housekeeping chatter ("thanks", "I'm with you", "follow me on Letterboxd"),
moderation or subreddit-rules talk ("is this allowed here", "vote manipulation", "this sub is becoming
letterboxd"), accusations about a post being AI-written, pure personal attacks or snark with no film point,
and political/philosophical debate that is about real-world politics rather than the film. If it is OUT,
output label "out".

## Step 2: the three in-scope labels
Sort every in-scope comment by how it supports its point. Two questions:
1. Does it make an arguable claim (an evaluation, interpretation, or factual/historical point about film
   that someone could dispute)?
2. If yes, does it give specific, checkable evidence for that claim? A stated reason is NOT evidence
   ("it works because it's cathartic" points to nothing checkable); a named scene, line, shot, structural
   choice, or a documented production/historical/theoretical fact IS evidence.

- reaction = no arguable claim, just a feeling or impression ("his films bore me to tears", "W wife fr").
- assertion = an arguable claim with no specific evidence behind it (confident opinion, stated not argued).
- argument = a claim backed by a specific, checkable particular (in-film detail OR a real
  production/history/theory fact) that actually supports it.

## Edge rules (apply these to the hard cases)
- Decorative specifics: a craft word like "the writing" or "the pacing" dropped on a feeling, with no
  specific instance, is NOT evidence. That is assertion, not argument.
- Reason vs evidence: explaining your rationale in the abstract is not evidence. Needs a specific particular.
- Bare value verdicts ("masterpiece", "trash", "overrated", "10/10"), even as a full sentence like "X is a
  masterpiece, full stop", are reaction, because there is no proposition for evidence to bear on. It becomes
  assertion only when it adds something arguable: a comparison, a causal because, a specific attribute, or
  an interpretation.
- Structural absence claims ("the twist doesn't work because nothing sets it up", "it never pays off")
  reason about the film's shape but name no specific moment, so they are assertion unless specific beats
  are named.
- A named scene does not by itself make a comment an argument. In "that final scene destroyed me" the scene
  is the object of a feeling, not evidence for a claim, so with no arguable claim it stays reaction.
- When a comment is genuinely a coin flip between assertion and argument, the tie goes to assertion, because
  argument is the higher bar.
- Length is never the test. A short comment that names a real scene can be argument; a long rant with no
  specifics is assertion.

## Output format
For each comment, output exactly one line:
<id><TAB><label><TAB><note>
where label is one of: out, reaction, assertion, argument.
Leave note empty unless the comment was genuinely hard to call; if hard, give a short note AND prefix it
with HARD: so it can be reviewed (e.g. "HARD: borderline assertion/argument, cites a scene but decoratively").
Output only these lines, one per comment, nothing else.

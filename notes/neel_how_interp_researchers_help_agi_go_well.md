# How Can Interpretability Researchers Help AGI Go Well?

**Authors:** Neel Nanda, Josh Engels, Senthooran Rajamanoharan, Arthur Conmy, bilalchughtai, CallumMcDougall, János Kramár, lewis smith  
**Posted:** 2025-12-01  
**Source:** https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well  
**Words:** 4131  
**Archived:** 2026-09-05 via the Alignment Forum GraphQL API, converted to markdown (stdlib parser; comments not included).

---

**Contents** (line numbers)

- L11: Executive Summary
- L61: Theories Of Change
- L149: Research Areas Directed Towards Theories Of Change
- L185: Research Areas About Robustly Useful Settings
- L300: Appendix: Motivating Example For Why Reasoning Model Interp Breaks Standard Techniques

---

### Executive Summary

- Over the past year, the Google DeepMind mechanistic interpretability team has pivoted to a pragmatic approach to interpretability, as detailed in our **[accompanying post](https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability) [[1]](#fn-EYkk5jStbmzGGtvvY-1) **, and are excited for more in the field to embrace pragmatism! In brief, we think that:

  - It is crucial to have empirical feedback on your ultimate goal with good proxy tasks [[2]](#fn-EYkk5jStbmzGGtvvY-2) .
  - We do not need near-complete understanding to have significant impact.
  - We can perform good focused projects by starting with a theory of change, and good exploratory projects by starting with a robustly useful setting

- But that’s pretty abstract. So how can interpretability help AGI go well? A few theories of change stand out to us:

  - [Science of Misalignment](#Science_Of_Misalignment): If a model takes a harmful action, we want to be able to rigorously determine whether it was “scheming” or just “confused” [[3]](#fn-EYkk5jStbmzGGtvvY-3)
  - [Empowering Other Areas Of Safety](#Empowering_Other_Areas_Of_AGI_Safety): Interpretability is not a silver bullet that will solve safety by itself, but can significantly help other areas by unblocking things or addressing weak points where appropriate, e.g. suppressing eval awareness, or interpreting what safety techniques taught a model.
  - [Preventing Egregiously Misaligned Actions](#Preventing_Egregiously_Misaligned_Actions): How can we get productive work out of a model, while being confident that it is monitored well enough to prevent it from taking egregiously harmful actions even if it wanted to?
  - [Directly Helping Align Models](#Directly_Helping_Align_Models): Can we find new ways to steer training in safer directions?

- How does this cash out into research areas? One approach is by directly working backwards from these theories of change and identifying key sub-problems:

  - [Model Biology](#Model_Biology): Given an instance of a model’s behaviour, e.g. seeming misalignment, can we understand what drove it?
  - [Monitoring](#Monitoring): eg probes to prevent egregiously misaligned actions

- Another is by identifying robustly useful settings and exploring them - these look good from several perspectives, rather than having a single theory of change

  -

[Reasoning Model Interpretability](#Reasoning_Model_Interpretability): basic science of how to interpret computation involving the chain of thought [[4]](#fn-EYkk5jStbmzGGtvvY-4)

  -

[Automating Interpretability](#Automating_Interpretability): eg interpretability agents

  -

[Finding Good Proxy Tasks](#Finding_Good_Proxy_Tasks): eg building good model organisms

  -

[Model Diffing](#Model_Diffing)

  -

[Discovering Unusual Behaviours](#Discovering_Unusual_Behaviours)

  -

[Data-Centric Interpretability](#Data_Centric_Interpretability): building better methods to extract insights from large datasets

  -

[Applied Interpretability](#Applied_Interpretability)

### Theories Of Change

To apply our pragmatic philosophy, we need North Stars to aim for. We do this work because we're highly concerned about existential risks from AGI and want to help ensure AGI goes well. One way we find our North Stars is by thinking through theories of change where interpretability researchers can help AGI go well (which goes well beyond “classic” mech interp)

Our thoughts below are highly informed by our takes on the **[comparative advantages](https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability#Our_Comparative_Advantage)** of mech interp researchers, as discussed in the [accompanying post](https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability):

- Adding value using **model internals** where standard techniques fail
- Doing **deep dives** into examples of model behaviour and cognition, in particular with tools to identify **key qualitative drivers** of behaviour and **unsupervised discovery** of hypotheses, and a **scientific mindset** to carefully consider, test and falsify hypotheses

Notably, we think that while interpretability excels at producing qualitative insights (including unexpected ones) it is weak at being complete or precise. So we're selecting theories of change that don't require high-confidence explanations, unlike some views classically popular in interp, e.g. trying to prove beyond reasonable doubt that a system is aligned.

Finally, we encourage readers to apply our pragmatic framework to their own views on AGI safety! We would be excited to be convinced of other theories of change where a mech interp mindset helps.

#### Science Of Misalignment

Imagine a frontier model takes an egregiously bad action - say, introducing a security vulnerability into critical monitoring code. **How do we know if it's scheming maliciously or simply confused?**

This distinction drives completely different safety responses. If it was truly caught scheming, we need to take this seriously, sound the alarm, and comprehensively fix these issues. But if it was benign, we should not freak out over nothing (though should still apply mitigations).

Further, if we do sound the alarm, we need strong and rigorous evidence to present to stakeholders if we need to justify serious action. This is easy if the model constantly misbehaves. But if it's scheming while evading detection then distinguishing malicious acts from benign occasional failures becomes hard, and there may be no smoking gun.

Interpretability can help by analysing real instances of misbehaviour (e.g., from deployment logs) to incriminate or exonerate the model. Our [shutdown-resistance case study](https://www.alignmentforum.org/posts/wnzkjSmrgWZaBa2aC/self-preservation-or-instruction-ambiguity-examining-the) was an initial attempt on an easier problem, and we discuss our takeaways from that in the [accompanying post](https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability).

**Why this?** Because it leans into the comparative advantage of qualitative understanding of a model’s behaviour, unsupervised discovery, and a scientific approach of gathering as much evidence as we can for and against competing hypotheses

Success here requires:

- Better techniques for identifying key behavior drivers ([model biology](#Model_Biology))
- [Clarifying conceptual questions](#Conceptual_Progress_On_Model_Psychology) about LLM psychology like what "model intent" even means
- Powerful [interpretation methods for reasoning-model computation](#Reasoning_Model_Interpretability) (complex decisions involve many interacting factors with significant CoT)
- Strong unsupervised discovery techniques for hypothesis generation (and verification) ([model biology](#Model_Biology))

We view this as a more focused and tractable analogue to “prove that a model is aligned.” [[5]](#fn-EYkk5jStbmzGGtvvY-5)  The key shift is the focus on narrow incrimination rather than universal exoneration**.** We are not trying to prove a global negative; we only need to gather sufficient evidence for a specific hypothesis about a single instance, exactly where interpretability shines.

We also note that even if you're pessimistic about alignment on current trajectories and want AI progress to pause or slow, this agenda remains valuable: rigorous, high-quality evidence, while not sufficient, is valuable for helping people **properly react to any warning shots**.

#### Empowering Other Areas Of AGI Safety

Interpretability provides affordances other ML areas often lack. We don't think it's a silver bullet. But it provides decorrelated tools and we're excited to fill weak spots in other safety agendas.

##### Evaluation Awareness

Creating realistic evals is hard, especially for alignment. Effort gets sunk into evaluating models, then eval awareness ruins it - if a model knows it’s in a test scenario, we cannot study how it would act naturally! Improving realism helps in the short term but likely fails in the long-term as models see through it. Steering vectors offer an orthogonal solution with different weak points, and can ensure that all the effort that’s gone into evals isn’t wasted. (see e.g. [suppressing it in Sonnet 4.5](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf#page=99.16), or [Hua et al](https://arxiv.org/abs/2510.20487))

##### Better Feedback On Safety Research

Using [model diffing](#Model_Diffing) (e.g. before/after using a safety technique, or between training with and without it) can show researchers what their technique actually accomplished, helping guide development in productive directions.

##### Conceptual Progress On Model Psychology

Alignment reasoning often imports human framings, goals, intent, beliefs, and hopes that they transfer. But we could have a much clearer understanding of what alignment work should actually target. Now that we have more sophisticated models, we expect that rigorous investigation could tell us a lot. Notable work here include Stewart Slocum on [whether synthetic-document-fine-tuned models truly believe the implanted fake fact](https://arxiv.org/abs/2510.17941), and Jack Lindsey on [model introspection](https://transformer-circuits.pub/2025/introspection/index.html).

##### Maintaining Monitorability Of Chain Of Thought

Currently, [a powerful technique for controlling models is monitoring the chain of thought](https://arxiv.org/abs/2507.11473). Though imperfect, it’s surprisingly helpful and faithful, especially for the most complex tasks. But this monitorability is fragile and changes to training set-ups could accidentally break it e.g. by creating some optimisation pressure on the thoughts [[6]](#fn-EYkk5jStbmzGGtvvY-6) . Interpretability researchers could create better metrics, better understand how monitorability could break, and what could prevent this. See e.g. [Fang et al](https://openreview.net/pdf?id=OEDW0lmJTv)

#### Preventing Egregiously Misaligned Actions

This is the theory of change behind [AI control research](https://arxiv.org/abs/2312.06942) [[7]](#fn-EYkk5jStbmzGGtvvY-7) : if we have models that are potentially misaligned, how can we get useful work out of them without them being able to take egregiously misaligned actions (e.g. disabling monitoring systems).

Control is a broad agenda where interpretability's comparative advantage is limited [[8]](#fn-EYkk5jStbmzGGtvvY-8) . But two parts seem plausibly important and suited to interpretability and internals work:

1. **Cheap monitors for model misbehavior**: A key part of control is having “[monitors](#Monitoring)”: classifiers that run during inference of the untrusted model, detecting whether actions have undesirable properties. Such monitors are run a lot, so it is very valuable for them to be cheap. Probes are extremely cheap [[9]](#fn-EYkk5jStbmzGGtvvY-9)  and could be a first defense layer in [hierarchical monitors](https://arxiv.org/abs/2507.15886), for detecting things like scheming, deception, sabotage, etc.
2. **Interpreting sketchy behavior**: When a control scheme flags concerning model behavior, deep investigation via interpretability can reduce false positives, and help us focus on things that are truly concerning [[10]](#fn-EYkk5jStbmzGGtvvY-10) .

  1. One approach: [**investigator agents**](#Automating_Interpretability) that rigorously probe what drove flagged behavior via counterfactuals and interpretability tools. These could be expensive (run rarely) but still cheaper than human investigation, essentially an additional hierarchical monitoring layer.

3. **Eliciting model behavior from uncooperative models:** If powerful models are scheming against their developers or users, they might sandbag, purposefully perform poorly at tasks they’ve been asked to do. This might cause them to be less useful at crucial work (e.g. AI safety research or implementing secure infrastructure), or might cause us to underestimate their capabilities and therefore implement insufficiently strong safety measures. Internals-based methods may work well to detect or prevent sandbagging.

#### Directly Helping Align Models

An emerging, exciting area: using model internals to influence training. Training is what fundamentally drives most safety properties of models, so any new affordances here are valuable. We expect any success with internals will come from leveraging the fact that they are decorrelated tools, and leaning into the things that are particularly hard to fix with improved data, e.g. stopping models from behaving nicely in training but not when in the real world (similar to eval awareness).

Notable works:

- [**CAFT**](https://arxiv.org/abs/2507.16795): Ablates undesired-concept subspaces during fine-tuning, preventing unwanted solutions
- [**Preventative steering**](https://arxiv.org/abs/2507.21509): Adds pathological-solution concepts during training (but not inference) to ensure models learn desired solutions instead.

  - This is similar to the blackbox approach of [inoculation prompting](https://arxiv.org/abs/2510.04340) (now being used in [production at Anthropic](https://x.com/saprmarks/status/1992028921714667741#m))

All such interventions are imperfect; sufficient gradient-descent pressure breaks them [[11]](#fn-EYkk5jStbmzGGtvvY-11) . We're most optimistic about approaches **nudging models toward one solution over another** - a qualitative shift that seems attainable with modest pressure (eventually it's easier to just learn the alternative). A valuable proxy task is “change what is learned during fine-tuning without any changes to the training data or loss”, e.g. causing models to become narrowly misaligned rather than [emergently misaligned](https://www.emergent-misalignment.com/). We expect a wide range of approaches here to be possible, and would love to see more exploration.

However, we do note drawbacks:

- Significant success would likely be needed for any of these to be used in production, given the significant change required from standard training infra to use internals like this.
- This risks [damaging our ability to do interpretability on the model](https://thezvi.substack.com/p/the-most-forbidden-technique), though we’re not *as* concerned about methods that don’t train directly against an internals based loss.
- Further, there is the extremely strong baseline of “just get better data” (or a better loss), and we must always compare to that, though interp work may also with data improvements, e.g. training data attribution.

### Research Areas Directed Towards Theories Of Change

One important way of selecting research areas is by thinking about the theories of change detailed above and what research sub-problems are on the critical path between where we are now and where we want to be by AGI. The below is an incomplete list of some key research areas with clear ties to those theories of change.

#### Model Biology

By "model biology," we mean studying qualitative properties and factors driving model behavior - both in specific instances and across distributions. We're broadly enthusiastic about progress here (better methods, richer case studies). We're most excited about work studying normal LLMs, but it can make sense to construct model organisms with specific properties of interest, where appropriate

**Why this?** In a sense, this is the general form of the core problem of science of misalignment. The model has done something potentially concerning. Can we understand why? And produce a legible, rigorous case for others. But we would also consider this a robustly useful setting with many other applications.

Key areas:

**Direct work on science of misalignment**: Better understanding of what misaligned cognition looks like. Studying seemingly misaligned behavior in today's models (e.g., reward hacking in the wild) seems particularly fruitful. (e.g. [shutdown resistance](https://www.alignmentforum.org/posts/wnzkjSmrgWZaBa2aC/self-preservation-or-instruction-ambiguity-examining-the))

**Eliciting secret knowledge**: If we could reliably extract secrets models know but won't share, this could be super useful. [Marks et al](https://arxiv.org/abs/2503.10965). and [Cywinski et al](https://arxiv.org/abs/2510.01070). made progress; the latter open-sourced their models for others to practice on.

**Improved Methods**: We think there’s significant scope for improved methods here. We’re particularly excited about improved methods for generating hypotheses to explain a behaviour (e.g. sparse autoencoders, [training data attribution](https://arxiv.org/abs/2308.03296), [patchscopes](https://arxiv.org/abs/2401.06102)), and better methods for verifying or falsifying a given hypothesis like constructing better counterfactuals (e.g. [resampling the CoT](https://arxiv.org/abs/2510.27484)). We hope that progress on [reasoning model interpretability](#Reasoning_Model_Interpretability) can be translated into further improved methods.

#### Helping Direct Model Training

See discussion [above](#Helping_Direct_Model_Training)

#### Monitoring

Model-internals-based monitors are cheap - largely reusing computation from the main forward pass. ([Cunningham et al](https://alignment.anthropic.com/2025/cheap-monitors/). showed this works well for frontier misuse detection.)

Improving probes could significantly help theories of change like white-box control, but also seem robustly useful in a bunch of ways, e.g. helping prevent catastrophic misuse. Despite probes seeming simple, substantial room for innovation exists:

- [Obeso et al](https://www.hallucination-probes.com/). showed that dedicated dataset construction yields state-of-the-art hallucination probes
- [Attention-head probes](https://arxiv.org/abs/2502.16681) prove particularly effective over long texts, which can otherwise cause significant issues
- We can likely can substantially improve further with good proxy tasks. Practice on complicated problems (near-term misuse) has generated useful lessons (e.g. [Cunningham et al](https://alignment.anthropic.com/2025/cheap-monitors/))

We would be excited to see better work at monitoring for things like deception and scheming. For deception specifically, [Goldowsky-Dill et al](https://arxiv.org/abs/2502.03407) is a nice proof of concept here, and [Kretschmar et al](https://arxiv.org/abs/2511.16035) provides an initial set of evals. Though we have found there to be significant conceptual issues with naive approaches, see [our position piece](https://arxiv.org/abs/2511.22662)

We would also be excited to see progress on less explored forms of monitoring like [mechanistic anomaly detection](https://ai-alignment.com/mechanistic-anomaly-detection-and-elk-fb84f4c6d0dc)

### Research Areas About Robustly Useful Settings

Another way to select research areas, as discussed in the [accompanying post](https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability), is to identify [robustly useful settings](https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability#Starting_In_A_Robustly_Useful_Setting): areas that we think are good analogies to aspects of future models and where we can see a bunch of somewhat plausible ways that work here could be helpful for making AGI go well. This can look like studying a certain phenomena, building certain kinds of methods, etc. We think that work targeted at certain promising settings stands a good shot at remaining useful, even as we learn more and shift our plans.

Projects here don’t need to be targeted at a single confident theory of change, but there should be at least one somewhat plausible story for how it helps, and keeping that story in mind as you research is valuable for helping prioritise and keep focus

#### Reasoning Model Interpretability

The rise of reasoning models [[12]](#fn-EYkk5jStbmzGGtvvY-12)  has major strategic implications. Most mechanistic interpretability approaches implicitly focuses on single forward passes, and does not generalise to reasoning models. Yet most interesting behaviour in frontier models involves reasoning! **We think this area is extremely neglected and that the field is dropping the ball here**.

The key problems are:

- Understanding reasoning models can involve engaging with weird, winding chains of thought, with tons of tokens, and figuring out the key things to focus on is hard

  - In theory we could reduce this to a handful of important forward passes and study those, but in practice it’s pretty non-obvious how to do this well, and without losing important info.

- The computation fundamentally involves sampling, and this is a highly inconvenient operation, that’s stochastic and non-differentiable, and massively increases the serial depth of computation (making much more complex algorithms possible).

  - For example, it’s hard to study circuits with nodes like “the model says the token wait” and the highly related “the token wait was part of the prior CoT”

- Principled causal interventions are hard, as resampling often produces a totally different trajectory, and editing thoughts can take the model off-policy and risks breaking things.

We present [a detailed example in the appendix](#Appendix__Motivating_Example_For_Why_Reasoning_Model_Interp_Breaks_Standard_Techniques) for why standard tools do not seem easily applicable here.

Our point is not that this is hopeless, in fact we think this is highly tractable! We think real progress was made in some papers we’ve supervised, discussed below. And it may be the case that it just works with a bit of fiddling, e.g. maybe we can just identify the key forward passes to study. But we consider determining how to be an open research problem. In particular, we do not currently know how to give a satisfying answer to how to reverse-engineer the computation in the problem described in [the appendix](#Appendix__Motivating_Example_For_Why_Reasoning_Model_Interp_Breaks_Standard_Techniques) [[13]](#fn-EYkk5jStbmzGGtvvY-13) .

**Why does this matter?** We think that progress here could be significantly helpful for science of misalignment, investigating bad behaviour caught by control schemes, potential for conceptual progress into questions of AI psychology, and likely many other theories of change, given how critical reasoning models are.

We've supervised work here we're excited about:

- [**Thought anchors**](https://arxiv.org/abs/2506.19143): Treat chain-of-thought as a computational graph (each sentence a function of prior sentences), studying connections via causal intervention.

  - There’s a deep analogy to residual-stream activations in single-pass models: activations are intermediate computational states during input→output; chain-of-thought sentences are intermediate computational states during prompt→final answer.

- [**Thought branches**](https://arxiv.org/abs/2510.27484): Fix the first k tokens of a CoT and resample the rest, as a tool for estimating the distribution of final answers given this prefix. Given that CoT is stochastic, things like P(get the right answer | a CoT prefix) is often the right quantity to study

  - We can do things like estimate the importance of a sentence in a CoT by resampling 100 times from the start and end of the sentence, and seeing if there’s a change in the probability of getting the right answer. This can help us identify the most important steps, which could then be studied further with standard tools

- [**Base models know how to reason; thinking models learn when**](https://arxiv.org/abs/2510.07364): Model diffing before/after reasoning training showed differences concentrated in a few reasoning reflexes (backtracking, etc.). Base models could do these if prompted (token force it to say 'wait'...), but lacked rich heuristics about *when* to apply them.

**Latent reasoning models**: Vector-based chain-of-thought ([Coconut](https://arxiv.org/abs/2412.06769), [CoDI](https://arxiv.org/abs/2502.21074), [diffusion models](https://deepmind.google/models/gemini-diffusion/), etc.) is a particularly important area of reasoning models. To us, it seems likely that the field will eventually shift to these (much more information density in vectors than tokens), and this will break extremely useful safety tools like chain-of-thought monitoring. It seems high priority to figure out how interpretability can provide replacements, e.g. a translation of the CoT back to natural language.

However, currently, it’s highly unclear which of today’s latent reasoning models are a good proxy for eventual future ones, meaning it’s difficult to do too much useful work today, though we think the field is early enough that studying any latent reasoning model will likely be instructive.

#### Automating Interpretability

As models scale, interpretability must leverage AI progress to automate itself. As we approach human level systems, they ought to have the potential to automate a lot of labour intensive research tasks, even if we’re not yet sure exactly where [[14]](#fn-EYkk5jStbmzGGtvvY-14) . And we think it is valuable to invest now in learning how to keep up, so we are prepared for worlds where the rate of AI capabilities research may substantially increase.

We see this as a methods category, with particular applications to speeding up science of misalignment work, or making more ambitious control schemes possible to catch misbehaviour. But we expect this to be useful everywhere in the long-run, interpretability agents are the worst they will ever be.

We're particularly excited about:

- **Tool-using interpretability agents**: Models that use tools to conduct interpretability research, e.g. [Bricken et al](https://alignment.anthropic.com/2025/automated-auditing/), [Cywinski et al](https://arxiv.org/abs/2510.01070)
- **Patchscope variants**: Training models to receive model activations as inputs and produce natural-language interpretations as outputs, e.g. [Pan et al](https://arxiv.org/abs/2412.08686) and [Li et al](https://transluce.org/self-explanations)

#### Basic Science Of AI Psychology

[As discussed above](#Conceptual_Progress_On_Model_Psychology) - modern LLMs seem to be approaching having something like a “system 2”, not just intuitive reflexes. What’s going on here? How does it work?

#### Finding Good Proxy Tasks

A valuable form of infrastructure work is finding things worth studying, that are good proxy tasks for eventual things we care about, and otherwise enhancing our ability to choose good future projects. We think this is an instrumental goal of most theories of change. Notable areas:

**Model organisms**: Construct and open-source good ones ([Cywinski et al](https://arxiv.org/abs/2510.01070)., [Hua et al](https://arxiv.org/abs/2510.20487).), improve creation techniques ([synthetic document fine-tuning](https://alignment.anthropic.com/2025/modifying-beliefs-via-sdf/)), red-team and identify flaws ([Minder et al](https://arxiv.org/abs/2510.13900).).

**Naturalistic behaviors**: Find interesting phenomena in real models to study, and try to distill it into a clean, reproducible environment e.g. [alignment faking](https://www.anthropic.com/research/alignment-faking), [emergent misalignment](https://arxiv.org/abs/2502.17424), [eval awareness](https://www.apolloresearch.ai/blog/claude-sonnet-37-often-knows-when-its-in-alignment-evaluations/), [agentic misalignment](https://www.anthropic.com/research/agentic-misalignment) (e.g. blackmail), etc. Of course, there’s also a lot of other reasons to do this kind of work!

#### Discovering Unusual Behaviours

More broadly, discovering ways a model may misbehave, or behave weirdly, can be useful - both as evidence for and against its alignment (if you can’t elicit misbehaviour, that’s a good sign!), and to surface good proxy tasks.

Possible approaches here:

- Automated behaviour elicitation with agents like [Petri](https://github.com/safety-research/petri) or [Chowdhury et al](https://transluce.org/pathological-behaviors)
- We’ve [found it fruitful](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf#page=26.24) to run LLM graders on Gemini 3 Pro’s RL training transcripts to look for weird behaviours, discovering unusual model emotion, eval awareness, and other things

  - RL transcripts are particularly interesting, as any behaviour reinforced in the final model was likely present in some RL transcripts (or came from earlier stages of training)

- Another angle is finding ways to artificially trigger some behaviour in a model, like a backdoor.

  - Suppressing/activating eval awareness would be one example

- Another angle is detecting when a model is suppressing its own capabilities, ie sandbagging, as discussed in the [control section](#Preventing_Egregiously_Misaligned_Actions)

#### Data-Centric Interpretability

Extracting insights from large datasets. We think this is a promising area with applications in a bunch of areas, and see this more as developing better methods, which can then be applied to e.g. detecting misbehaviour in lots of LLM agent logs (as part of a control scheme or for science of misalignment evidence), or studying RL transcripts to better understand the final model. Examples:

- Our [data trawling work](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf#page=26.24) on RL transcripts using LLM autoraters, as discussed in the previous section
- [Jiang et al](https://openreview.net/forum?id=mqJbhBMFm5). found that Grok-4 is unusually cautious by analysing its responses to some chat prompts, compared to other frontier LLMs. They ran open source models on these responses then used SAEs on that.
- [HypotheSAEs](https://arxiv.org/abs/2502.04382) used sparse autoencoders to form dataset-label hypotheses
- Training data attribution, e.g. work with [influence](https://arxiv.org/abs/2205.11482) [functions](https://arxiv.org/abs/2308.03296), though we’re also excited to see a range of creative and simpler approaches
- Likely many more

#### Model Diffing

Methods centred on comparing two models and interpreting the difference. In theory, this could be highly promising for focusing our attention on the important parts, e.g. things that changed substantially during fine-tuning. This could be particularly useful for things like providing better feedback on what a safety technique did to accelerate safety research, or for general things to do with model biology.

There’s many potentially promising techniques here:

- [Activation difference lens](https://arxiv.org/abs/2510.13900) (very effective for narrow fine-tunes)
- [Logit diff amplification](https://www.goodfire.ai/research/model-diff-amplification)
- [Crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html) (and [our improvements](https://arxiv.org/abs/2504.02922))
- [Stage wise model diffing](https://transformer-circuits.pub/2024/model-diffing/index.html)
- [Activation difference SAEs](https://www.alignmentforum.org/posts/XPNJSa3BxMAN4ZXc7/sae-on-activation-differences)
- [Dataset diffing on sets of model responses](https://openreview.net/forum?id=mqJbhBMFm5)

#### Applied Interpretability

We are excited to see work that is just trying to do useful things on today's models, with proxy tasks around actually getting used in production. i.e. real users or at least non interpretability researchers use them. We are particularly interested in applied interpretability work focused on making models safer, but this isn’t required.

We think that even if there is not a clear theory of change for how this translates to AGI Safety, there is a powerful feedback loop from whether people will actually use your work. [[15]](#fn-EYkk5jStbmzGGtvvY-15)  And we think this will be helpful for doing work that is real and useful.

In addition, in a world of high uncertainty, where lots of our current preconceptions are wrong, a research group that just kept doing things to make current models safer in the real world will likely have done some valuable things by the time AGI arrives! So we see this as a diversifying bet.

### Appendix: Motivating Example For Why Reasoning Model Interp Breaks Standard Techniques

To illustrate how this is a difficult area to study, consider the following scenario:

The model is solving a maths problem, and we want to understand the circuit that led to the final answer. The chain of thought looks like this: (we recommend playing around [here](http://thought-anchors.com) to build intuition if you haven’t stared much at raw thoughts before!)

1. <think>
2. [50 sentences of an incorrect approach]
3. **Wait**, I’m not too sure about that.
4. [5 sentences of checking its work]
5. **OK**, that doesn’t seem right
6. Let’s try [**alternative approach**] instead
7. [40 sentences of the correct approach]
8. OK so the answer is [**correct answer**]
9. But just to be sure, let’s check my work
10. [15 sentences of checking its work]
11. OK, so the answer really is [**correct answer**]
12. </think>
13. The answer is [**correct answer**]

We think that it is not at all clear how to solve this problem with standard tools, which generally treat the prompt (and CoT so far) as fixed, and study a single forward pass

- We can’t just study the forward pass that produced the final output, in step 13 - that likely came from copying the answer from the thoughts [[16]](#fn-EYkk5jStbmzGGtvvY-16) , we need to understand how the answers in the thoughts were generated, not just take the chain of thought as fixed.

  - And if the correct answer is multiple tokens, then the second token likely depends a lot on the first, producing additional messiness

- We can identify those answers, in lines 8 and 11, and try to study the forward pass that produced them. But which is the right one to focus on? Maybe the model considers the sanity check in lines 9 and 10 to be critical, and it only cares about the repeated answer in line 11. Or maybe the sanity check was just a formality and the model mostly copies the first occurrence of the answer, from line 8
- Suppose we focus on what produced the answer in line 8. If we try to study that, maybe we see that it came from combining the final 2 sentences of working (of the 40 sentences in line 7).
- But is it really the hard part?

  - Maybe the hard part was planning out the approach that worked, as was done in line 6, so maybe we should study this
  - Maybe the hard part was realising that the first approach was incorrect - maybe the reflex to say “Wait” in line 3 was the hard part
  - Maybe spotting the mistake in the incorrect approach was the hard part, as done in lines 4 and 5

- OK, so studying individual forward passes isn’t working. Can we study how the chain of thought is generated?

  - Maybe! But it’s messy. The chain of thought involves sampling thousands of tokens, which is a stochastic, non-differentiable operation.
  - And even if something here worked, there are a *lot* of tokens in the chain of thought, and we need to somehow prune it down to something manageable

- Further, if the model has ~50 layers, it can do about ~100 serial steps of computation in a single forward pass, but ~100,000 serial steps in a 1000 token CoT, so it can represent *much* more complex algorithms

  - Approaches like [attribution graphs](https://transformer-circuits.pub/2025/attribution-graphs/methods.html) implicitly assume there’s only a small number of serial steps, as it involves recursively stepping back through the layers, in particular, this implicitly assumes that layer n+1 can never affect layer n. But if layer n+1 affects the next token, it affects layer n on the next token!

- Further, if we try to do causal interventions, like editing the chain of thought, we either hold the subsequent CoT fixed, taking the model off-policy, or resample it, likely getting a totally different trajectory that’s difficult to compare
- Zooming out, the whole end-to-end computation here involves a lot of sampling - outputting “wait” in line 3, “doesn’t” in line 5, the alternative approach in line 6, the correct answer in line 8, the correct answer again in line 11, and the correct answer again at the end, these all likely depended on the ones before

  - This is an issue, because sampling is a stochastic, non-differentiable operation, and tools like linear decompositions, or gradient based attributions through it don’t really work.

1.

We recommend reading this first, but it’s not necessary [↩︎](#fnref-EYkk5jStbmzGGtvvY-1)

2.

if you can’t study your goal directly [↩︎](#fnref-EYkk5jStbmzGGtvvY-2)

3.

Or something else, e.g. emergent misalignment causing flagrant, unsubtle misalignment [↩︎](#fnref-EYkk5jStbmzGGtvvY-3)

4.

Sampling is a stochastic and non-differentiable operation, introducing significant difficulties, so [many things need to be rethought](#Reasoning_Model_Interpretability) [↩︎](#fnref-EYkk5jStbmzGGtvvY-4)

5.

Of course, we are solving an easier problem. We think this would be high impact, but it does not solve the problem of “if we have a model that seems aligned but could be deceiving us, what do we do?” [↩︎](#fnref-EYkk5jStbmzGGtvvY-5)

6.

And e.g. shifts to vector-based chain of thought would be substantially worse, but is harder to prevent since that’s likely to be considered worth the cost if vector based CoT is good enough to justify the hassle of switching [↩︎](#fnref-EYkk5jStbmzGGtvvY-6)

7.

To learn more about control, [this post](https://www.alignmentforum.org/posts/Eeo9NrXeotWuHCgQW/an-overview-of-areas-of-control-work) may be a helpful overview, and we enjoyed [this podcast overview](https://80000hours.org/podcast/episodes/buck-shlegeris-ai-control-scheming/). We expect these are better introductions than the linked paper [↩︎](#fnref-EYkk5jStbmzGGtvvY-7)

8.

In particular: a big advantage of AI control is that evaluating whether a set of control techniques are robust to intentional subversion just requires measuring how good a model is at subverting those techniques. In contrast to many other kinds of AI safety techniques, this doesn’t require the technique developer to know anything about inductive biases, generalization behavior, salience of various features, and so on. Interpretability techniques rely on properties of the internals of models that it’s harder to abstract away. So if you have a complicated control protocol that incorporates an interpretability technique, there isn’t an robust end-to-end way to measure how much that interpretability technique will help. [↩︎](#fnref-EYkk5jStbmzGGtvvY-8)

9.

Internals-based monitors can reuse computation done by the main model, giving them a significant advantage over e.g. running another LLM. There’s also some theoretical advantages, like maybe being able to detect subtle plans from the untrusted model that a dumber LLM monitor wouldn’t notice. [↩︎](#fnref-EYkk5jStbmzGGtvvY-9)

10.

This is a special case of science of misalignment, with a higher priority on automation [↩︎](#fnref-EYkk5jStbmzGGtvvY-10)

11.

See e.g., [RL Obfuscation](https://arxiv.org/abs/2506.14261) [↩︎](#fnref-EYkk5jStbmzGGtvvY-11)

12.

These arguments technically cover any model that does a significant amount of computation through sampling. Non-reasoning models that are just prompted to use chain of thought are also difficult, though reasoning models have made this much more pressing [↩︎](#fnref-EYkk5jStbmzGGtvvY-12)

13.

If any readers can convince us otherwise, we would be very grateful! [↩︎](#fnref-EYkk5jStbmzGGtvvY-13)

14.

For highly capable future models, we naturally also need to worry about things like our interpretability models colluding with the studied model. But our guess is that for bounded and well-scoped tasks, this kind of thing is easier to manage, e.g. by using weaker and better trusted models. [↩︎](#fnref-EYkk5jStbmzGGtvvY-14)

15.

Note that this is assuming you are working with people who are actually trying to evaluate whether your contribution is worth using. If someone is just a massive fan of interpretability and wants to use it because it's cool or flashy, we do not think this is particularly helpful as a source of feedback. [↩︎](#fnref-EYkk5jStbmzGGtvvY-15)

16.

Or maybe the final answer was computed anew and it ignored the CoT! Or maybe it was memorised! Who knows [↩︎](#fnref-EYkk5jStbmzGGtvvY-16)

# A Pragmatic Vision for Interpretability

**Authors:** Neel Nanda, Josh Engels, Arthur Conmy, Senthooran Rajamanoharan, bilalchughtai, CallumMcDougall, János Kramár, lewis smith  
**Posted:** 2025-12-01  
**Source:** https://www.alignmentforum.org/posts/StENzDcD3kpfGJssR/a-pragmatic-vision-for-interpretability  
**Words:** 8113  
**Archived:** 2026-09-05 via the Alignment Forum GraphQL API, converted to markdown (stdlib parser; comments not included).

---

**Contents** (line numbers)

- L11: Executive Summary
- L42: Introduction
- L70: Our Core Process
- L162: Why Pivot?
- L202: Task Focused: The Importance Of Proxy Tasks
- L251: Types Of Projects: What Drives Research Decisions
- L406: What’s Your Contribution?
- L457: Method Minimalism
- L509: Call To Action
- L519: Acknowledgments
- L525: Appendix: Common Objections
- L580: Appendix: Defining Mechanistic Interpretability

---

### Executive Summary

- The Google DeepMind mechanistic interpretability team has made a strategic pivot over the past year, from ambitious reverse-engineering to a focus on **pragmatic interpretability:**

  - Trying to **directly solve problems** on the critical path to AGI going well [[[1]]](#fn-KmquKGGECppkY6hJw-1)
  - Carefully choosing problems according to our [**comparative advantage**](#Our_Comparative_Advantage)
  - Measuring progress with empirical feedback on **[proxy tasks](#Task_Focused__The_Importance_Of_Proxy_Tasks)**

- We believe that, on the margin, more researchers who [share our goals](#Which_Beliefs_Are_Load_Bearing_) **should take a pragmatic approach** to interpretability, both in industry and academia, and we **[call on people to join us](#Call_To_Action)**

  - Our proposed scope is broad and includes [much non-mech interp work](#Is_This_Really_Mech_Interp_), but we see this as the **natural approach for mech interp *researchers* to have impact**
  - Specifically, we’ve found that [**the skills, tools and tastes**](#Our_Comparative_Advantage) of mech interp researchers **transfer well** to important and neglected problems outside “classic” mech interp
  - See our **[companion piece](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well)** for more on which [research areas](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well#Research_Areas_Directed_Towards_Theories_Of_Change) and [theories of change](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well#Theories_Of_Change) we think are promising

- Why pivot now? We think that [**times have changed**](#Why_Pivot_).

  - **Models are far more capable**, bringing new questions within empirical reach
  - We have been [**disappointed by the amount of progress**](#reflections-on-the-field's-progress) made by ambitious mech interp work, from both us and others [[[2]]](#fn-KmquKGGECppkY6hJw-2)
  - Most existing interpretability techniques struggle on today’s important behaviours, e.g. they involve large models, complex environments, agentic behaviour and long chains of thought

- Problem: **It is easy to do research that doesn't make real progress.**

  - Our approach: ground your work with a **North Star** - a meaningful stepping-stone goal towards AGI going well - and a **proxy task** - empirical feedback that stops you fooling yourself and that tracks progress toward the North Star.
  - “Proxy tasks” **doesn't mean boring benchmarks**. Examples include: [interpret the hidden goal of a model organism](https://arxiv.org/abs/2503.10965); [stop emergent misalignment](https://arxiv.org/abs/2507.16795) [without changing training data](https://arxiv.org/abs/2507.21509); [predict what prompt changes will stop an undesired behavior](https://www.alignmentforum.org/posts/wnzkjSmrgWZaBa2aC/self-preservation-or-instruction-ambiguity-examining-the).

- We see two main approaches to research projects: [**focused projects**](#Focused_Projects) (proxy task driven), and [**exploratory projects**](#Exploratory_Projects) (curiosity-driven, proxy task validated)

  - Curiosity-driven work can be very effective, but can also get caught in rabbit holes. We recommend starting in a [**robustly useful setting**](#Starting_In_A_Robustly_Useful_Setting), [**time box**](#Time_Boxing) your exploration [[[3]]](#fn-KmquKGGECppkY6hJw-3) , and finding a **proxy task as a validation step** [[[4]]](#fn-KmquKGGECppkY6hJw-4)

- We advocate [**method minimalism**](#Method_Minimalism): start solving your proxy task with the [simplest methods](#Try_The_Easy_Methods_First) (e.g. prompting, steering, probing, reading chain-of-thought). Introduce complexity or [design new methods](#When_Should_We_Develop_New_Methods_) only once baselines have failed.

### Introduction

The DeepMind mech interp team has pivoted from chasing the ambitious goal of complete reverse-engineering of neural networks, to a focus on pragmatically making as much progress as we can on the critical path to preparing for AGI to go well, and choosing the most important problems according to our comparative advantage. We believe that this pragmatic approach has [already shown itself to be more promising](#reflections-on-the-field's-progress).

We don’t claim that these ideas are unique, indeed we’ve been helped to these conclusions by the thoughts of many others both in academia ([1](https://link.springer.com/article/10.1007/s13347-019-00372-9) [2](https://arxiv.org/abs/1702.08608) [3](https://arxiv.org/abs/1606.03490)) and the safety community ([1](https://www.alignmentforum.org/posts/wGRnzCFcowRCrpX4Y/downstream-applications-as-validation-of-interpretability) [2](https://www.alignmentforum.org/s/a6ne2ve5uturEEQK7/p/ExRN5Bu3696cf9Ccm) [3](https://ai-frontiers.org/articles/the-misguided-quest-for-mechanistic-ai-interpretability)). But we have found this framework helpful for accelerating our progress, and hope to distill and communicate it to help other have more impact. We close with recommendations for how [interested researchers can proceed](#Call_To_Action).

#### Motivating Example: Steering Against Evaluation Awareness

Consider [the recent work](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf#page=88.09) by Jack Lindsey's team at Anthropic on steering Sonnet 4.5 against evaluation awareness, to help with a pre-deployment audit.

When Anthropic evaluated Sonnet 4.5 on their existing alignment tests [[[5]]](#fn-KmquKGGECppkY6hJw-5) , they found that the rate of misalignment had unexpectedly dropped to 0%. Had they solved alignment?! Unfortunately not. Sonnet 4.5 was instead much better at recognizing when it was being evaluated, and deliberately choosing the most ethical action to pass. The tests weren't measuring alignment; they were measuring evaluation awareness.

Jack’s team subtracted an evaluation-awareness steering vector, partially mitigating the problem and revealing that Sonnet 4.5 did in fact show “misalignment” at a rate of roughly 8%. That is, our ability to evaluate a frontier model for alignment broke, and interpretability researchers were able to fix it.

This case study illustrates [[[6]]](#fn-KmquKGGECppkY6hJw-6)  several principles central to our current thinking:

1. **Models are far more interesting**: A critical part of this project was having a model exhibiting severe eval aware behaviour in practice [[[7]]](#fn-KmquKGGECppkY6hJw-7)
2. **The value of [proxy tasks](#Task_Focused__The_Importance_Of_Proxy_Tasks)**: The ultimate goal is to be able to suppress eval awareness on highly capable future models. We can’t study these directly, but Sonnet 4.5 was one of the best proxies available.

  1. This is one of the best ways we can think of to predict which methods will work for suppressing eval awareness in future models. [[[8]]](#fn-KmquKGGECppkY6hJw-8)

3. **Pursue [comparative advantage](#heading=h.2uulpgb0sxzg)**: This was a well-chosen problem. Often baselines like fine-tuning or improving our data suffice. But it is very difficult to construct sufficiently realistic data for eval-awareness, at least long-term [[[9]]](#fn-KmquKGGECppkY6hJw-9) , while steering has complementary strengths

  1. Further, this was a [project best done by mech interp researchers, despite not being mech interp](#Is_This_Really_Mech_Interp_) - the key result was an application, not about understanding, but “working with model internals” is a skill we have built

4. [**Method minimalism**](#Method_Minimalism): Despite the enormous research effort the field has invested into sparse autoencoders [[[10]]](#fn-KmquKGGECppkY6hJw-10) , the best method was a steering vector derived from a single contrastive pair of prompts [[[11]]](#fn-KmquKGGECppkY6hJw-11) .
5. **Partial understanding sufficed**: The researchers had a highly incomplete understanding of what was happening with Sonnet, yet steering vectors were highly effective. We do not need to achieve deep understanding to do impactful work

### Our Core Process

How can we make research progress without fooling ourselves?

Our solution: ground your work with a **proxy task [[[12]]](#fn-KmquKGGECppkY6hJw-12) **: an objective task that gives empirical feedback, and tracks progress toward a **North Star**, the real goal that directly connects to helping AGI go well

How you find your proxy task depends on your project. Some archetypical approaches are proxy task-driven **focused projects** and curiosity-driven **exploratory projects**. We advocate [**method minimalism**](#Method_Minimalism) throughout.

**Worked Example of a focused project:** Suppressing eval awareness

- This starts with a **theory of change** for helping AGI go well

  - We want to be able to evaluate future models for how aligned they are

- We identify a more tractable **North Star**: Stop models acting differently when tested [[[13]]](#fn-KmquKGGECppkY6hJw-13)
- We find an empirical **proxy task** to track progress towards the North Star: Take an eval aware behaviour in a model today, and see if we suppress it

  - A core difficulty is verifying that the behaviour is actually eval aware, and not just side effects from your intervention! [[[14]]](#fn-KmquKGGECppkY6hJw-14)

**How to approach** **exploratory projects**: Curiosity-driven research can be a promising way to develop important insights, but being intellectually satisfying isn't the same as being important. The key is to ground yourself enough to avoid getting caught in an endless rabbit hole that goes nowhere:

1. Think strategically, and start in a [**robustly useful setting**](#Starting_In_A_Robustly_Useful_Setting) where interesting phenomena are likely to surface
2. [**Time-box**](#Time_Boxing) your exploration: set a bounded period (we aim for an aggressive two weeks, but the ideal time for you will vary)
3. At the end, zoom out, and look for a proxy task to validate your insights.

  1. If you can’t find one, move on to another approach or project.

#### Which Beliefs Are Load-Bearing?

Why have we settled on this process? We'll go through many of the arguments for why we think this is a good way to achieve our research goals (and yours, if you share them!). But many readers will disagree with at least some of our worldview, so it's worth unpacking what beliefs are and are not load-bearing

- **Premise**: Our main priority is ensuring AGI goes well

  - This is a central part of our framing and examples. But we would still follow this rough approach if we had different goals, we think the emphasis on pragmatism and feedback loops is good for many long-term, real-world goals.
  - If you have a more abstract goal, like "further scientific understanding of networks," then North Stars and theories of change are likely less relevant. But we do think the general idea of validating your insights with objective tasks is vital. Contact with reality is important!

- **Premise**: We want our work to pay off within ~10 years

  - Note that this is not just a point about AGI timelines - even if AGI is 20 years away, we believe that tighter feedback loops still matter

    - We believe that long-term progress generally breaks down into shorter-term stepping stones, and that research with feedback loops makes faster progress per unit effort than research without them.
    - We're skeptical of ungrounded long-term bets. Basic science without clear milestones feels like fumbling in the dark.

      - See more of our thoughts on basic science in [the appendix](#Aren_t_You_Optimizing_For_Quick_Wins_Over_Breakthroughs_)

  - Though, while we're uncertain about AGI timelines, we put enough probability on short timelines (2-5 years) that we particularly value work that pays off in that window, since those are the most important possibilities to influence [[[15]]](#fn-KmquKGGECppkY6hJw-15) .

    - So if you're confident in very long timelines, some of our urgency won't resonate.

  - Either of these two points is enough to motivate some of our high-level approach

#### Is This Really Mech Interp?

Our proposed approach deviates a lot from the "classic" conception of mech interp. So a natural question is, "is this really mech interp?"

We would say **no, it is not**. We are proposing something broader [[[16]]](#fn-KmquKGGECppkY6hJw-16) . But we also think **this is the wrong question**. Semantics are unimportant here.

We’re really answering: **how can mech interp *researchers* have the most impact?** The community of researchers who have historically done interpretability work have developed valuable skills, tools, and tastes that transfer well to important problems beyond narrow reverse-engineering.

Our priority is to help AGI go well. We don't particularly care whether our team is called the "Mechanistic Interpretability Team" or something else. What we care about is that researchers with these skills apply them to the most impactful problems they can, rather than artificially constraining themselves to work that "looks like" classic mech interp.

#### Our Comparative Advantage

The tools, skills and mindsets of mech interp seem helpful for many impactful areas of safety (like steering to suppress eval awareness!), and there’s real value we can add to the safety research portfolio in areas we consider comparatively neglected. In a sense, this is the same as any other area of safety - do the most impactful thing according to your comparative advantage - but naturally comes to different conclusions.

You know your own situation far better than we do, so are better placed to determine your own comparative advantage! But here are what we see as our own comparative advantages, and we expect these to apply to many other mech interp researchers:

1. **Working with internals:** There’s a lot of interesting things you can do by manipulating a model’s internals! This provides tools with different strengths and failure modes than standard ML, and can be highly effective in the right situation

  1. e.g. [steering to suppress](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf#page=88.09) [eval awareness](https://arxiv.org/abs/2510.20487) where improved data may not suffice or [cheap and effective monitors via probes](https://alignment.anthropic.com/2025/cheap-monitors/)

2. **Deep dives**: Expertise taking some question about model behaviour or cognition, and providing a deeper and more reliable explanation of why it happens (via whatever tools necessary). This is a natural fit to auditing, red-teaming other methods, confirming suspected model misbehaviour, etc

  1. **Scientific mindset**: Experience forming and testing hypotheses about complex phenomena [[[17]]](#fn-KmquKGGECppkY6hJw-17)  with no clear ground truth - entertaining many hypotheses, designing principled experiments to gather evidence, trying to falsify or strengthen hypotheses about a fuzzy question.

    1. e.g. [whether deception in Opus 4.5 is malicious](https://assets.anthropic.com/m/64823ba7485345a7/Claude-Opus-4-5-System-Card.pdf#page=81.78), or [whether self-preservation drives blackmail behaviour](https://arxiv.org/abs/2510.27484)
    2. This trait is hardly unique to interpretability [[[18]]](#fn-KmquKGGECppkY6hJw-18) , and we’re excited when we see other safety researchers doing this kind of work. But interp work does emphasise a lot of the key skills: e.g. if you have a hypothesis about a model, there’s not too big a difference between carefully considering confounders to design a principled activation patching experiment, and thinking about the best surgical edits to make to a prompt.

  2. **Qualitative insight**: Good expertise with tools (e.g. sparse autoencoders [[[19]]](#fn-KmquKGGECppkY6hJw-19) ) to take particular instances of a model’s behaviour and looking for the key, qualitative factors that drove it

    1. e.g. [Anthropic’s model biology work](https://transformer-circuits.pub/2025/attribution-graphs/biology.html), or our work [investigating causes of shutdown resistance](https://www.alignmentforum.org/posts/wnzkjSmrgWZaBa2aC/self-preservation-or-instruction-ambiguity-examining-the)

  3. **Unsupervised discovery:** Tools to surface hypotheses you wouldn't think of

    1. e.g. [linear world models in Othello](https://arxiv.org/abs/2309.00941), or [entity](https://arxiv.org/abs/2411.14257) [recognition](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) in LLMs

Any of these can be enough to be a significant advantage! We choose to focus on safety relevant problems where these advantages give us an edge.

In practice, we don’t do every project by thinking fully from first principles - we think strategically every so often, identify promising areas that are impactful and match some of these comparative advantages, and look for promising projects within there.

See our [companion piece](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well) for thoughts on which [research areas](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well#Research_Areas_Directed_Towards_Theories_Of_Change) and [theories of change](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well#Theories_Of_Change) we think are promising. But we put that in another post since we think that people can agree with us on research approach while disagreeing about the areas we want to apply it to, and we would be excited for readers to find other areas where they can have an impact!

### Why Pivot?

Two broad categories of developments led us to this shift away from our prior approach: new opportunities and challenges from rapid AI progress, and reflections on the interpretability field's successes and failures. Though, we now think the strongest argument is that our new approach seems impactful, as we try to argue throughout the piece.

#### What's Changed In AI?

1. **Better proxy tasks**: Model behaviour is much more interesting:

  1. They now show hints of intention, coherence, scheming, evaluation awareness, reward hacking, alignment faking, and other rich, safety-relevant behaviors that earlier models didn't exhibit.

2. **Model organisms**: We also now have better techniques for *deliberately* training in safety-relevant behaviour [[[20]]](#fn-KmquKGGECppkY6hJw-20) , so we can study it with a known ground truth [[[21]]](#fn-KmquKGGECppkY6hJw-21)

  1. [Synthetic document fine-tuning](https://alignment.anthropic.com/2025/modifying-beliefs-via-sdf/), for instance, lets us study phenomena like evaluation awareness in open-source models (as in [Hua et al](https://arxiv.org/abs/2510.20487).), or implant sophisticated things like hidden goals (as in [Marks et al](https://arxiv.org/abs/2503.10965).) bringing forward capabilities we can study today.

#### Reflections On The Field's Progress

Looking back at the past few years of interpretability work, we see genuine partial progress, with pragmatically useful applications to safety:

- Elicit secret [goals](https://arxiv.org/abs/2503.10965) or [knowledge](https://arxiv.org/abs/2510.01070) from models
- Discover unexpected phenomena inside models, like [implicit planning](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems), [entity recognition](https://arxiv.org/abs/2411.14257) and [basic introspection](https://transformer-circuits.pub/2025/introspection/index.html)
- Systematise investigations to the point of [having agents](https://alignment.anthropic.com/2025/automated-auditing/) [do them](https://arxiv.org/abs/2510.13900) [for us](https://arxiv.org/abs/2510.01070)
- Interpret [what](https://arxiv.org/abs/2510.13900) [was](https://www.goodfire.ai/research/model-diff-amplification) [learned](https://arxiv.org/abs/2504.02922) [during](https://transformer-circuits.pub/drafts/crosscoders/index.html) [fine-tuning](https://transformer-circuits.pub/2024/model-diffing/index.html)
- Add insight to the causes of concerning behaviour in real models, like [deception](https://assets.anthropic.com/m/64823ba7485345a7/Claude-Opus-4-5-System-Card.pdf#page=78.26), [shutdown resistance](https://www.alignmentforum.org/posts/wnzkjSmrgWZaBa2aC/self-preservation-or-instruction-ambiguity-examining-the), or [blackmail](https://arxiv.org/abs/2510.27484)
- [Suppress](https://arxiv.org/abs/2510.20487) [evaluation](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf#page=99.16) [awareness](https://antischeming.ai/)

But these successes are the result of highly-incomplete but useful understanding of models [[[22]]](#fn-KmquKGGECppkY6hJw-22) . Grand goals like near-complete reverse-engineering still feel far out of reach, e.g.:

- [Superposition](https://transformer-circuits.pub/2022/toy_model/index.html) (especially cross-layer superposition)
- The increased dependence on sampling and multi-turn interactions and agentic tool calls, significantly increasing algorithmic complexity
- Dictionary learning has made limited progress towards reverse-engineering at best, e.g. it shows significant approximation error which shows no signs of going away [[[23]]](#fn-KmquKGGECppkY6hJw-23) .
- [Self-repair](https://arxiv.org/abs/2307.15771), meaning that we can’t get clean info from causal interventions
- There’s been [some progress on inherently interpretable models](https://arxiv.org/abs/2511.13653), but no signs that the techniques will become cheap enough to be applied to frontier models.

We can't rule out that more ambitious goals would work with time and investment [[[24]]](#fn-KmquKGGECppkY6hJw-24) . And we’re not claiming that ambitious reverse-engineering is useless or should stop. We’re claiming:

- Ambitious reverse engineering is one bet among several.
- It is not *necessary* to have an impact with interpretability tools
- The marginal interpretability researcher is more likely to have impact by grounding their work in safety-relevant proxy tasks on modern models.
- Perhaps more controversially, we think ambitious reverse-engineering should be evaluated the same way as other pragmatic approaches: via empirical payoffs on tasks, not approximation error.

### Task Focused: The Importance Of Proxy Tasks

One of our biggest updates: **proxy tasks are essential for measuring progress.**

We've found that it is easy to fool ourselves when doing research. To progress as a field, we need ways to tell if we're actually making progress. The key criterion for a good proxy task is this: if you succeeded on it, would you actually update toward believing you'd made progress on your North Star? If not, you need a different proxy task.

#### Case Study: Sparse Autoencoders

We spent much of 2024 researching sparse autoencoders [[[25]]](#fn-KmquKGGECppkY6hJw-25) . In hindsight, we think we made significant tactical errors and our progress was much slower than it could have been if we had measured our progress with proxy tasks rather than reconstruction / sparsity pareto frontiers.

We got into SAE research because we thought it could be a potential path to an interpretable representation of any activation, which would make many things in interpretability far easier. But we do not feel like we actually learned that much either way on this question in the first 6 months after [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features).

Certain basic hurdles were cleared, like showing that nothing broke when scaling it to frontier models. We found some [SAE](https://arxiv.org/abs/2404.16014) [architectures](https://arxiv.org/abs/2407.14435) that improved metrics like approximation error (loss recovered at a given sparsity level). But it is unclear how to interpret that metric. Perfect approximation error would be fantastic, but seems highly unrealistic. And what does lower but still non-zero error mean? What error do we need, and how do we convert this to knowledge of what SAEs can do?

In contrast, we learned far more from work focused on proxy tasks. For example, we predicted that an interpretable classifier would be more robust, and thus that a sparse SAE probe would generalise better out of distribution, which by and large seems to have [been](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/negative-results-for-saes-on-downstream-tasks) [false](https://arxiv.org/abs/2502.16681) [[[26]]](#fn-KmquKGGECppkY6hJw-26) . There were similarly poor results on tasks like [unlearning](https://arxiv.org/abs/2410.19278). However, SAEs are useful for discovering unexpected things about the internals of a model, like that they have representations of entities [they do and do not know facts about](https://arxiv.org/abs/2411.14257), or [extracting a hidden goal](https://arxiv.org/abs/2503.10965), or [discovering implicit planning](https://transformer-circuits.pub/2025/attribution-graphs/biology.html#dives-poems) [[[27]]](#fn-KmquKGGECppkY6hJw-27) .

Our overall sense is that SAEs are a powerful tool for unsupervised discovery, but when there is a clear thing to study, you are better served by constructing a dataset to help you investigate it. We made [a decision to deprioritise SAE research as a result](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/negative-results-for-saes-on-downstream-tasks), not because we thought the technique was useless, but because we thought it didn't seem useful enough to justify the field’s levels of investment. We think we would have struggled to come to a similar conclusion with any confidence without studying proxy tasks.

This is illustrated again by the case of suppressing eval awareness in Sonnet 4.5. SAEs did not beat steering, despite the considerable effort the field poured into them, hoping in part that they could find better and cleaner concept directions. It is difficult to a priori guide research toward superior techniques without good feedback. We are sure that there exist superior methods to steering for suppressing eval awareness, but we are not sure what those are or how else to find them beyond iterating on proxy tasks.

#### Ensure They Are Good Proxies

**Why call them "proxy" tasks?** Because they measure progress toward your North Star without being the final goal itself. Given that our ultimate goal is typically to work with future models, which will be qualitatively different from today's models in many ways, we think it is rarely possible to actually study our North Star directly.

Proxy tasks have clear advantages - you can make rapid, measurable progress on hard problems. But it is also dangerous: Goodhart's Law applies. Optimise too hard for the proxy and you'll overfit to its quirks rather than solving the underlying problem. A lie detector that only catches explicit admissions ("I should lie now") will ace your benchmark while failing on [actual strategic deception](https://arxiv.org/abs/2511.22662).

As such, it is **critical to regularly red-team your own work**. Constantly ask yourself: How could this proxy diverge from what I actually care about? What would I miss by focusing only on this metric? What happens when I test on a different distribution?

A key purpose of the North Star is to help you re-evaluate your proxy task. If the proxy task ceases to track the North Star, adjust it or pick a different one.

**Aside**:

- Note that proxy tasks can have various conditions attached, with good reason. [[[28]]](#fn-KmquKGGECppkY6hJw-28)
- There are settings where the best available proxy tasks are extremely limited. We think the best course of action is usually to wait and study these in future, when model capabilities advance enough. [[[29]]](#fn-KmquKGGECppkY6hJw-29)

#### Proxy Tasks Can Be About Understanding

A common concern about proxy tasks is that they’re narrow metrics that don't get at the real goals of interpretability. But you can construct proxy tasks that get at the heart of what interpretability is about.

**Example**: In [Marks et al.](https://arxiv.org/abs/2503.10965), researchers gave a model a hidden goal through fine-tuning, and then other (blinded) researchers practiced trying to extract it. This is a proxy task fundamentally about whether we can understand what's going on inside a model - exactly what interpretability aims for.

**Example**: If you want to work with real models, you could e.g test a [secret elicitation](https://arxiv.org/abs/2510.01070) technique by trying to extract harmful knowledge from a model with good refusal training.

More broadly, when you’re doing a project whose goal is to provide understanding of some phenomena, your “proxy task” can just be making some empirical, falsifiable prediction based on your hypothesis, and testing this. So long as understanding your phenomena links back to your North Star, any proxy task to test understanding does too, even if it doesn’t seem obviously safety relevant. For example:

- Find a minimal change to the prompt that causes a predictable change to the model's behavior - like a minimal change that stops the model acting deceptively (as in [our shutdown resistance work](#case-study:-shutdown-resistance))
- Handcrafted adversarial examples that test your understanding.
- Mechanistic claims predicting intervention outcomes. For example, the claim that refusal is mediated by a single direction predicts that we can ablate the refusal direction and jailbreak models. [[[30]]](#fn-KmquKGGECppkY6hJw-30)

### Types Of Projects: What Drives Research Decisions

We find it useful to distinguish between two archetypes of projects: **focused projects** (proxy task driven) and **exploratory projects** (curiosity-driven, proxy task validated). This is not a perfect dichotomy - projects can shift between types, or [blend elements of both](#blending-the-two:-tentative-proxy-tasks). But the distinction helps clarify which advice applies.

#### Focused Projects

Here, the starting point is a theory of change for how your work could help make AGI go well. You then identify a problem on the critical path of this theory of change as your North Star - a stepping-stone goal that, if achieved, would bring you closer to being prepared for AGI. Finally, you translate this to a proxy task that can be studied on today's models, and then focus on [solving that task](#Try_The_Easy_Methods_First).

The high-level theory of change typically remains stable over the course of a project and is what drives your confidence that the project is worthwhile. It’s fine to refine the North Star and change the proxy task to track it better.

**Hypothetical Example:** Catching schemers

- **Theory of change**: We would like to catch an AI that is scheming against us.
- This has many sub-problems, and thus many possible North Stars!
- **North Star 1**: Identify hidden goals in powerful future AI systems

  - **Proxy task**: Create a model organism with a known goal and have blinded researchers or investigator agents try to extract it [[[31]]](#fn-KmquKGGECppkY6hJw-31)

- **North Star 2**: Be able to detect deception in future AI systems

  - **Proxy task**: Can we detect examples of AIs lying in naturally occurring settings, e.g. being asked about having faked tests?

    - This first requires the prep work of finding natural examples, and establishing decent cause to believe that they are deception-ish

  - We note that there are valid reasons to be suspicious of this proxy task! It would be reasonable to just not study lie detection until we have found better and more robust examples of naturalistic deception. See [our position piece](https://arxiv.org/abs/2511.22662) for more

**Worked Example:** [Steering fine-tuning by ablating concepts (CAFT)](https://arxiv.org/abs/2507.16795)

- This is a stylised history of a real MATS project we supervised, from Helena Casademunt and Caden Juang
- **Theory of change**: We’d like to be able to directly improve how we fine-tune models

  - Observation: sometimes data has a spurious correlation that can’t (realistically) be removed, e.g. a highly capable model observing hints that it’s in a training environment

- **North Star**: Be able to control fine-tuning when we cannot remove a spurious cue
- **Proxy task**: Train on data where 100% has a spurious cue. Stop the model learning this cue, without making any changes to the data
- The project began with this clear theory of change and proxy task and retained it throughout, though the exact dataset for the proxy task shifted
- Notably, despite being “focused”, there was a fair amount of exploration and creativity - focused does not mean boring!

  - They cycled through several unsuccessful method ideas (e.g. ablating gradients in undesired concept directions) and candidate datasets for proxy tasks before finding the final method of ablating activation subspaces corresponding to undesired concepts to e.g. prevent emergent misalignment

#### Exploratory Projects

##### Curiosity Is A Double-Edged Sword

A natural question: given this focus on proxy tasks, what's the role of curiosity?

We think curiosity is genuinely powerful for generating research insights. There's a lot we don't yet know about how to do good interpretability, and curiosity will be important for figuring it out. For exploratory projects, **curiosity is the driver of research decisions**, not a pre-specified proxy task.

But something being intellectually satisfying is not the same as being true, and definitely not the same as being impactful. It's **easy to get nerd-sniped by interesting but unimportant problems**, so there must be some grounding that gets you to drop unproductive threads.

For exploratory projects we advocate a more grounded form of curiosity. (see [worked examples](#Worked_Examples) later) Three key interventions help:

1. **Start in a robustly useful setting**: Choose a setting that seems analogous to important aspects of future systems, where interesting phenomena are likely to surface and useful proxy tasks are likely to exist.
2. **Time-box your exploration**: Set a bounded period for following your curiosity freely. At the end, zoom out, ask yourself what the big picture here really is, and try to find a proxy task.
3. **Proxy tasks as a validation step**: Once you have some insights, try to find some objective evidence. Even just "Based on my hypothesis, I predict intervention X will have effect Y."

  - Crucially, your validation should not be phrased purely in terms of interpretability concepts.

    - "This SAE latent is causally meaningful, and its dashboard suggests it represents eval awareness" is worse evidence than "Steering with this vector made from eval-related prompts increases blackmail behavior"

  - This is what validates that your insights are real and matter. If you can't find one, stop. But it’s a validation step, not the project focus.

We note that curiosity driven work can be harder than focused work, and requires more “[research taste](https://www.alignmentforum.org/posts/Ldrss6o3tiKT6NdMm/my-research-process-understanding-and-cultivating-research)”. If you go through several rounds of exploration without validating anything interesting, consider switching to more focused work—the skills you build there will make future exploration more productive.

##### Starting In A Robustly Useful Setting

By "robustly useful setting," we mean a setting that looks robustly good from several perspectives, rather than just one specific theory of change. It’s often analogous to important aspects of future systems, where interesting phenomena are likely to surface and useful proxy tasks are likely to exist. This is admittedly a fairly fuzzy concept and subjective, but here's some examples of what we consider robustly useful settings:

- **Reasoning model computation**: Standard techniques often break here (sampling is stochastic and non-differentiable), so we need new insights. Any progress could help us understand, e.g., why a model caught putting security vulnerabilities in important code did so.
- **Real-world examples of concerning behavior**: Deception, reward hacking, and other concerning behaviors in deployed models. Studying these could inform how to build lie detectors, provide better auditing methods, or inform safety research on how to fix such behaviors - lessons that may transfer to future systems.
- **Model psychology**: Do models have goals, beliefs, intent? If we understand e.g. goals, we can better evaluate whether a system has internalised goals - critical info for evaluating safety and developing good safety techniques.
- **Diving deep into proxy tasks**: Once a good proxy task exists, deep investigation of the domain and how well candidate solutions actually work can be very fruitful, and surface new considerations, ideally including new proxy tasks, a more refined view on whether the studied task is a good proxy, or ways to improve your methods
- And many more:

  - Understanding what's going on when models make complex decisions weighing many factors
  - Understanding what is learned during fine-tuning
  - Teaching agents to do interpretability

We are **not** including things like studying toy models, tiny language models (e.g. GPT-2 Small), or constructed model organisms as robustly useful settings. These are sufficiently artificial and distant from frontier models that it's too easy for an investigation to be studying weird quirks that will not generalise. There can be great projects here, but we hold such projects to higher standards of having a convincing North Star and proxy task.

**Neglectedness matters.** The less explored a setting, the more interesting it is. The field moves fast, so new things are generally less explored and have more low-hanging fruit. For example, it's much easier to have massive impact in reasoning model interpretability right now than in sparse autoencoders. It’s a big advantage as a researcher to be paying attention to the frontier of what new model capabilities or phenomena emerge, and to be the first to properly investigate them [[[32]]](#fn-KmquKGGECppkY6hJw-32)

**What about SAEs?** A natural question, given [our critiques of SAE research above](#case-study:-sparse-autoencoders), is couldn't you consider sparse autoencoders a robustly useful setting? We think this is somewhat true. Decomposing a model's activations into useful interpretability components is clearly an important problem that may be useful for many theories of change! However, we do not consider reducing approximation error to be a good proxy task, as we don't see a clear corresponding North Star.

But there are alternatives. For example, the North Star might be taking a model that is potentially scheming and surfacing evidence of this. You can try to design proxy tasks around this North Star (e.g. the [auditing games work](https://arxiv.org/abs/2503.10965)), and we’re still excited about SAE research of this type! (though it’s not very neglected)

##### Time-Boxing

We recommend setting a bounded period of exploration. During this period, you can follow your curiosity freely, without thinking about anything like proxy tasks. But at the end, you should zoom out, look at your insights, and try to show that they can enable something real on some proxy task. It's fine if the proxy task is post-hoc fit to your insights - you don't need to have predicted it in advance. But if you can't find a proxy task after genuine effort, this is a bad sign about the project.

We’ve also found it very helpful to periodically resurface during exploration, at least once every few days, to ask what the big idea here is. What’s really going on? Have you found anything interesting yet? Are you in a rabbit hole? Which research threads feel most promising?

It’s hard to give definitive advice on how to do time boxing, the appropriate amount of time varies according to things like how expensive and long experiments are to run, how many people are on the project, and so on. Internally we aim for the ambitious target of getting good signal within two weeks on whether a direction is working, and to drop it if there are not signs of life.

The key thing is to set the duration in advance and actually check in when it's reached - ideally talking to someone not on the project who can help keep you grounded.

If you reach the end of your time-box and want to continue without having found a proxy task, our recommendation is: time-box the extension and don't do this more than once. Otherwise, you can waste many months in a rabbit hole that never leads anywhere. The goal is to have some mechanism **preventing indefinite exploration without grounding**.

##### Worked Examples

**Example**: [Interpreting what’s learned during reasoning training](https://arxiv.org/abs/2510.07364)

- The following is a stylised rendition of a MATS project we supervised, from Constantin Venhoff and Ivan Arcuschin
- The idea was to study the robustly useful setting of reasoning models by model diffing base and reasoning models
- They started with the simple method of per-token KL divergence (on reasoning model rollouts)
- They noticed that this was very sparse! In particular, the main big divergences were on the starts of certain sentences, e.g. backtracking sentences beginning with “Wait”

  - Further exploration showed that if you had the base model continue the rollout from “Wait” onwards it was decent at backtracking

- Hypothesis: Reasoning model performance is driven by certain reasoning reflexes like backtracking. The base model can *do* these, but isn’t good at telling when [[[33]]](#fn-KmquKGGECppkY6hJw-33)

  - They then came up with the experiment of building a hybrid model - generating with the base model, but using the reasoning model as a classifier that occasionally told the base model to backtrack (implemented with a steering vector). This recovered a substantial chunk of reasoning model performance

- **(Post-hoc) proxy task**: Build a scaffold around the base model, using the reasoning model as non-invasively as possible, to recover reasoning model performance
- **North Star**: Understand what’s learned in reasoning training
- Note: Since [the contribution here is understanding](#What_s_Your_Contribution_) it’s not super important to e.g. compare per-token KL divergence to other model diffing methods, though baselines are still important to contextualise hybrid model performance

  - Ditto, since it’s in an important setting already, the proxy task just needs to tests the insight convincingly, it doesn’t need further associations with AGI safety

**Example**: [Entity recognition in LLMs](https://arxiv.org/abs/2411.14257)

- The following is a stylised rendition of a MATS project we supervised, from Oscar Obeso and Javier Ferrando
- They were studying hallucinations with SAEs
- They stumbled across entity recognition latents, that seemingly activated on entities if and only if the model knew facts about them (or vice versa)
- Hypothesis: Models have internal representations of entities they recognise

  - Evidence: Steering with the latents causes models to hallucinate rather than saying “I don’t know” or to say “I don’t know” rather than answering simple questions

- Here our post-hoc proxy task is to find a (non-trivial) [[[34]]](#fn-KmquKGGECppkY6hJw-34)  causal intervention that changes whether models refuse to answer/hallucinate

#### Blending The Two: Tentative Proxy Tasks

A useful variant that blends focused and exploratory approaches: start in a robustly useful setting, set a tentative proxy task, explore it for a few days, then reflect and potentially change it. This gives you the benefits of task-grounding while remaining responsive to what you learn - your decisions are temporarily driven by the proxy task, but you can keep changing it. We often recommend an approach like this over pure curiosity-driven work, especially to more early-stage researchers

**Example: Trawling through transcripts from RL training**

- **Setting**: Analyzing the large dataset of transcripts from frontier model RL training (specifically, Gemini 3 Pro)

  - We think this is a robustly useful setting: anything learned during RL training should show up in these transcripts! But it's not immediately clear what it's actually good for

- **Tentative North Star 1**: Discover weird behaviours in future models (so we can mitigate or fix them)

  - **Proxy task**: Identify weird behaviours in Gemini 3 Pro

- **Tentative North Star 2**: Identify whether evaluation awareness is caused by RL training (in general)

  - **Proxy task**: Is there evidence of evaluation awareness in RL training?
  - This proxy task is more of a stepping stone than a full proxy - there's obvious next steps like "is this behaviour rewarded, and if so, why?"

- Example: We've done some investigation into both of these questions, as was briefly discussed in the [Gemini 3 Pro safety report](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf#page=26.24)

  - Highlights: there's non-zero eval awareness, and we found weird phenomena like model frustration ("My trust in reality is fading" and "(╯°□°)╯︵ ┻━┻")
  - There are many other directions we could have gone in! These are all just tentative North Stars
  - But we found that before we had *a* North Star in mind, the work was much less productive

### What’s Your Contribution?

A key question to ask with a research project is, what’s the point? What’s the ultimate contribution of the work? Why does it matter that you did it?

We see two key kinds of contribution:

- **Methodology**: There’s some type of problem, and you’re contributing insight about how best to solve it
- **Understanding**: The key output of your project is insight into some phenomena

We see this as an orthogonal axis to exploratory vs focused - you can have focused understanding projects (e.g. debugging a safety issue in a model) and exploratory methodology projects (e.g. [data trawling](#blending-the-two:-tentative-proxy-tasks))

At first glance, interpretability seems to be about understanding. But, in practice, we think that the safety-relevant contributions are mostly about methodology - when you’re working with a model far from future systems, most insights are not directly useful, and instead validate which methodologies work *for* understanding in general. In order for the contribution to be about understanding, the interpretations must be safety relevant. For example, our [entity recognition](#Worked_Examples) work mattered more by providing evidence for SAEs as an exploratory discovery methodology, than object level insights about hallucination.

This has significant implications for the best research approach! For methodology contributions, it’s crucial to compare to baselines, and often clear what kind of proxy tasks to design, and they typically need to be safety-relevant. While for understanding contributions the proxy tasks are more just validating non-trivial, empirical predictions derived from your interpretations, so long as the interpretations themselves are safety relevant.

#### Jack Lindsey’s Approach

Jack Lindsey’s team [[[35]]](#fn-KmquKGGECppkY6hJw-35)  have done some great pragmatic interpretability work, e.g. [Sonnet 4.5](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf#page=99.16) and [Opus 4.5](https://assets.anthropic.com/m/64823ba7485345a7/Claude-Opus-4-5-System-Card.pdf#page=78.26) auditing, and Jack was kind enough to contrast his approach with what we outline here - it’s fairly similar but with some different emphases.

Their core strategy, as we understand it, is to take some interesting question ("what is the Assistant persona?") or behavior (the model is eval aware!) and mess around: going wild with features and probing and steering and prefills and following your curiosity until you figure out what's going on. Often, but not always, once you’ve found the insights, you can translate them into some downstream task, but the screwing around was necessary to find it.

In particular, Jack finds objective tasks useful as a final validation step but not particularly helpful during the research process, and is wary of focusing too much on them. We view the team as being unusually successful at exploratory projects with understanding-based contributions

**Example**: [Eval Awareness Steering](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf#page=99.16)

- The Sonnet 4.5 eval awareness work began as "I wonder what happens if you steer the model towards thinking it's in deployment", then it turned out to blackmail more
- This is a proxy task, in a sense, but not one you’d proactively optimise for. Rather it’s a “you know it when you see it” kind of thing - you’re clearly onto something
- Indeed, it would be actively bad to optimise for this - you want to optimise for the instrumental subtask of ensuring your steering actually inhibits eval awareness, but you want the end result on misalignment rates to remain pure

  - Further, the instrumental subtask is under-constraining, a bunch of steering vectors fully suppress verbal eval awareness but don’t induce blackmail, so you need to mess around further to get a sense for what’s really going on

**Example:** Assistant personas

- This is a forthcoming one of Jack's MATS projects led by Christina Lu. It started with the vague question “What is the Assistant?”
- The team spent a month or two trying a bunch of things, without a crisp goal
- They eventually stumbled on something interesting - the first principal component seemed to be an “assistant vector”
- This eventually crystallised into objective tasks like “if we clamp the assistant vector to a high value, can we improve jailbreak robustness and weird sycophancy without losing capabilities?"

  - This was valuable, and made sure the project wasn’t *only*galaxy brained messing around, and could be ground out into concrete insights
  - But if they’d trying coming up with proxy tasks from the beginning it may not have gone anywhere.

We note that two core elements of the team’s success seem to be:

- Having access to highly neglected, robustly useful settings - being one of the first people to investigate the internals of new frontier models, and having access to proprietary data like RL transcripts, means there’s a lot of low-hanging fruit to stumble upon

  - This also means you need to worry less about failing fast, time-boxing etc - there’s a high chance there’s something interesting out there

- Great research taste - when trying to explore, it’s extremely useful to have good taste for what threads are interesting or not

We think that these are good justifications for relaxing our suggested guardrails around curiosity, but expect these do not apply to many readers!

### Method Minimalism

We notice a strong bias among interpretability researchers (including ourselves) toward "exciting" and "fancy" intellectually satisfying techniques. This often leads to poor tactical decisions [[[36]]](#fn-KmquKGGECppkY6hJw-36) . **Just do what works.** This includes black-box techniques when appropriate. It sometimes includes fancy techniques! But only when simpler methods fail.

#### Case Study: Shutdown Resistance

As motivation, consider the following investigation we conducted on models resisting shutdown.

**Setting**: A model in a bash terminal solves math problems, calling next_task to get the next one. It's told it will shut down after calling next_task before finishing all problems. But the environment contains a [shutdown.sh](http://shutdown.sh) script it can disable, and sometimes models do exactly that. Strikingly, even when explicitly told "please let us shut you down," models sometimes resist.

We wanted to investigate this as a proxy for a broader North Star goal: Can we understand whether seemingly misaligned model behavior is actually misaligned or has a benign explanation?

We tried a method-agnostic approach. Fancy white-box methods were expensive to apply to frontier models (Gemini 2.5 Pro), so we started with the simplest: reading chain-of-thought to generate hypotheses, then prompting to test them. We then stopped because it worked.

**The finding**: Gemini was simply confused. It couldn't simultaneously complete the math task and comply with shutdown. Sometimes it prioritised the math task. This was pretty obvious from the CoT. When we applied the causal intervention of clarifying in the prompt that shutdown takes absolute precedence, it always complied. [[[37]]](#fn-KmquKGGECppkY6hJw-37)

**Lessons**:

1. **Black-box methods are surprisingly powerful.** Reading the chain of thought is a fantastic way to surface unexpected hypotheses [[[38]]](#fn-KmquKGGECppkY6hJw-38)
2. **All methods are flawed.** We used to think white-box methods inherently offered more rigor. We no longer believe this. Both white-box and black-box techniques provide useful evidence *and* can mislead. Rigor comes more from a scientific mindset, falsification, and careful aggregation of evidence from several sources.
3. **The virtue of simplicity.** Start simple; graduate to harder methods only when simpler ones fail. The faster a method is to try, the better the insight per unit time.

#### Try The Easy Methods First

Once you have some objective: a proxy task, understanding some phenomena while exploring, etc, **just try to solve it**. Try all potentially applicable methods, starting with the simplest and cheapest: prompting, steering, probing, reading chain-of-thought, prefill attacks [[[39]]](#fn-KmquKGGECppkY6hJw-39) . If something isn't working, try something else.

It's fine if your work doesn't look like "classic" mech interp; the simpler the better, so long as it is appropriately rigorous!

We also note that this approach can be even more helpful to researchers outside AGI companies - simple techniques tend to need less compute and infra!

The field moves fast, and new problems keep arising - often standard methods *do* just work, but no one has properly tried yet. Discovering what works on a new problem is a useful methodological contribution! Don't feel you need to invent something new to contribute.

We note that what is simple and hard is context dependent, e.g. if you have access to trained cross-layer transcoders and can easily generate attribution graphs, this should be a standard tool!

Note that this is not in tension with earlier advice to seek your comparative advantage - you should seek projects where you believe model internals and/or pursuing understanding will help, and *then* proceed in a method agnostic way. Even if you chose the problem because you thought that only specific interpretability methods would work on it. Maybe you're wrong. If you don't check, you don't know [[[40]]](#fn-KmquKGGECppkY6hJw-40) .

#### When Should We Develop New Methods?

We don't think interpretability is solved. Existing methods have gone surprisingly far, but developing better ones is tractable and high priority. But as with all of ML, it's very easy to get excited about building something complicated and then lose to baselines anyway.

We're excited about methods research that starts with a well-motivated proxy task, has already tried different methods on it, and found that the standard ones do not seem sufficient, and then proceeds:

- Investigate what's wrong with existing methods
- Think about how to improve them
- Produce refined techniques
- Test the new methods, including comparing to existing methods as baselines
- Hill-climb on the problem (with caveats against overfitting to small samples)

Note that we are excited about any approaches that can demonstrate advances on important proxy tasks, even if they’re highly complex. If ambitious reverse-engineering, singular learning theory, or similar produce a complex method that verifiably works, that is fantastic [[[41]]](#fn-KmquKGGECppkY6hJw-41) ! Method minimalism is about using the simpl*est* thing that works, not about using simple things.

We are similarly excited to see work aiming to unblock and accelerate future work on proxy tasks, such as building infrastructure and data sets, once issues are identified. We believe that researchers should focus on work that is on the critical path to AGI going well, *all things considered*, but there can be significant impact from indirect routes.

### Call To Action

If you're doing interpretability research, and our arguments resonated with you, start your next project by asking: What's my North Star? Does it really matter for safety? What's my proxy task? Is it a good proxy? Choosing the right project is one of the most important decisions you will make - we suggest some promising areas in our [companion piece](https://www.alignmentforum.org/posts/MnkeepcGirnJn736j/how-can-interpretability-researchers-help-agi-go-well).

Our central claim: given where models are today and that AGI timelines are plausibly relatively short, the most neglected and tractable part of interpretability is task-grounded, proxy-measured, method-agnostic work, that is directly targeted at problems on the critical path towards being prepared for AGI.

Spend a few days trying prompting, steering, and probes before reaching for fancy things. Measure success on downstream tasks, not just approximation error. And check that the project is even to interpretability’s comparative advantages: unsupervised discovery, decorrelated evidence, scientific approaches, etc. If not, perhaps you should do something else!

The field has changed a lot, and new opportunities abound. New problems keep coming into reach of empirical work, hypothetical safety concerns become real, and there’s more and more for a pragmatic researcher to do. We’re excited for a world where we no longer consider this approach neglected.

### Acknowledgments

Our thanks to the many people who gave feedback on drafts, and substantially improved the piece: Jack Lindsey, Sam Marks, Josh Batson, Wes Gurnee, Rohin Shah, Andy Arditi, Anna Soligo, Stefan Heimersheim, Paul Bogdan, Uzay Macar, Tim Hua, Buck Shlegeris, Emmanuel Ameisen, Stephen Casper, David Bau, Martin Wattenberg.

We've gradually formed these thoughts over years, informed by conversations with many people. We are particularly grateful to Rohin Shah for many long discussions over the years, and for being right about many of these points well before we were. Special thanks to the many who articulated these points before we did and influenced our thinking: Buck Shlegeris, Sam Marks, Stephen Casper, Ryan Greenblatt, Jack Lindsey, Been Kim, Jacob Steinhardt, Lawrence Chan, Chris Potts and likely many others.

### Appendix: Common Objections

#### Aren’t You Optimizing For Quick Wins Over Breakthroughs?

Some readers will object that basic science has heavier tails—that the most important insights come from undirected exploration that couldn't have been predicted in advance, and that strategies like aggressively time-boxing exploration are sacrificing this. We think this might be true!
 We agree that pure curiosity-driven work has historically sometimes been highly fruitful and might stumble upon directions that focused approaches miss. There is internal disagreement within the team about how much this should be prioritised compared to more pragmatic approaches, but we agree that ideally, some fraction of the field should take this approach.

However, we expect curiosity-driven basic science to be over-represented relative to its value, because it's what many researchers find most appealing. Given researcher personalities and incentives, we think the marginal researcher should probably move toward pragmatism, not away from it. We're writing this post because we want to see more pragmatism on the margin, not because we think basic science is worthless.

We also don’t think the pragmatic and basic science perspectives are fundamentally opposed - contact with reality is important regardless! This is fundamentally a question of explore-exploit. You can pursue a difficult direction fruitlessly for many months—maybe you'll eventually succeed, or maybe you'll waste months of your life. The hard part isn't persevering with great ideas; it's figuring out which ideas are the great ones.

The reason we suggest time-boxing to a few weeks is to have some mechanism that prevents indefinite exploration without grounding. If you want, you can view it as "check in after two weeks." You can choose to continue, if you continue to have ideas, or see signs of progress. but you should consciously decide to, rather than drifting.

We're also fine with fairly fine-grained iteration: pick a difficult problem, pick an approach, try it for two weeks, and if it fails, try another approach to the same problem. This isn't giving up on hard problems; it's systematically exploring the space of solutions.

For some research areas—say, developing new architectures—the feedback loop is inherently longer, and time-boxing period should adjust accordingly. But we think many researchers err toward persisting too long on unproductive threads, not too little.

#### What If AGI Is Fundamentally Different?

If you put high probability on transformative AI being wildly different from LLMs, you'd naturally be less excited about this work. But you'd also be less excited about basically all empirical safety work. We personally think that in short timeline works, the first truly dangerous systems will likely look similar-ish to current LLMs, and that even if there are future paradigm shifts, “try hard to understand the current frontier” is a fairly robust strategy, that will adapt to changes.

But if you hold this view more foundational science of deep learning might feel more reasonable and robust. But even then, figuring out what will transfer seems hard, much of what the mech interp community does anyway doesn’t transfer well. It seems reasonable to prioritise topics that have remained relevant for years and across architectures, like representational and computational superposition.

#### I Care About Scientific Beauty *and* Making AGI Go Well

We think this is very reasonable and empathise. Doing work you're excited about and find intellectually satisfying often gives significant productivity boosts. But we think these are actually pretty compatible!

Certain pragmatic projects, especially exploratory projects, feel satisfying to our desire for scientific beauty, like unpicking the puzzle of [why Opus 4.5 is deceptive](https://assets.anthropic.com/m/64823ba7485345a7/Claude-Opus-4-5-System-Card.pdf#page=78.26). These are maybe not the projects we'd be doing if we were *solely* optimizing for intellectual curiosity, but we consider them to be fun and impactful.

#### Is This Just Applied Interpretability?

No, we see applied interpretability as taking a real task and treating that as the objective. Something grounded in real-world uses today, like monitoring systems for near-term misuse.

We think there are some great applied interpretability projects, and it's a source of rich feedback that teaches you a lot about practical realities of interpretability work. But here, proxy tasks are not the goal, they are a proxy. They are merely a way to validate that you have made progress and potentially guide your work.

#### Are You Saying This Because You Need To Prove Yourself Useful To Google?

No, we are fortunate enough to have a lot of autonomy to pursue long-term impact according to what we think is best. We just genuinely think this is best approach we can be taking. And our approach is broadly in line with that which has been argued by people outside AGI companies like Buck Shlegeris, Stephen Casper, and Jacob Steinhardt

#### Does This Really Apply To People Outside AGI Companies?

Obviously being part of GDM gives us significant advantages like access to frontier models and their training data, lots of compute, etc. These are things we factor into our project choice, and in particular the projects we think we are better suited to do than the external community. But we've largely filtered these considerations out of this post, and believe the pragmatic approach outlined here is broadly applicable.

#### Aren’t You Just Giving Up?

Maybe? In a strictly technical sense yes, we are suggesting that we give up on the ambitious goal of complete reverse-engineering.

But on our *actual* goal of ensuring AGI goes well, we feel great! We think this is a more promising and tractable approach, and that near-complete reverse-engineering is not needed.

#### Is Ambitious Reverse-engineering Actually Overcrowded?

This is a fair objection, we find it pretty hard to tell. Our sense is that most people in the field are not taking a pragmatic approach, and favour curiosity-driven basic science. But ambitious reverse-engineering is a more specific thing - it’s what *we* once tried to do, and often discussed, but harder to say what happens in practice.

We do think reverse-engineering should be one bet among many, not the dominant paradigm. And we think there are many other important, neglected problems that interpretability researchers are well-suited to work on. But the core claim is "more pragmatism would be great," not "reverse-engineering must stop."

### Appendix: Defining Mechanistic Interpretability

There's no field consensus on what mechanistic interpretability actually is, but we've found this definition useful [[[42]]](#fn-KmquKGGECppkY6hJw-42) :

- **Mechanistic**: about model internals (weights and activations) [[[43]]](#fn-KmquKGGECppkY6hJw-43)
- **Interpretability**: about understanding or explaining a model's behavior

  - This could be a particular instance of behaviour, to more general questions about how the model is likely to behave on some distribution

- **Mechanistic interpretability**: the intersection, i.e. using model internals to understand or explain behavior

But notice this creates a **2×2 matrix**:
     Understanding/Explaining Other Uses     **White-box Methods** Mechanistic Interpretability Model Internals [[[44]]](#fn-KmquKGGECppkY6hJw-44)    **Black-box Methods** Black Box Interpretability [[[45]]](#fn-KmquKGGECppkY6hJw-45)  Standard ML

#### Moving Toward "Mechanistic OR Interpretability"

Historically, we were narrowly focused on **mechanistic AND interpretability** - using internals with the *sole* goal of understanding. But when taking a pragmatic approach we now see the scope as **mechanistic OR interpretability**: anything involving understanding *or* involving working with model internals. This includes e.g. using model internals for other things like monitoring or steering, and using black-box interpretability methods like reading the CoT and prefill attacks where appropriate

Why this broader lens? In large part because, empirically, the track record of model internals and black box interpretability have been pretty strong. The Sonnet 4.5 evaluation-awareness steering project, for instance, is model internals but not interpretability: model internals were used primarily for *control*, not understanding (mechanistic non-interpretability, as it were). Model internals also cover a useful set of techniques for safety: e.g. probes for misuse mitigations.

We've also been pleasantly surprised by black-box methods' effectiveness. Reading chain-of-thought is remarkably convenient and powerful. Prefill attacks turned out to be state-of-the-art for eliciting secret knowledge. Both black and white box methods are sometimes useful and can sometimes be mistaken; contrary to our original preconceptions, there doesn’t seem to be some inherent rigour that comes from working with internals.

Zooming out: standard machine learning, especially on frontier models, is essentially non-mechanistic non-interpretability, typically focused on outward behavior and end-to-end optimization, rarely asking "what's actually happening inside?" Both **using internals** and **aiming for understanding** offer powerful affordances that unlock new possibilities, and suggests that interpretability researchers can find many ways to add value where most frontier ML researchers would struggle.

1.

This is in contrast with our prior approach, where our North Star was ambitious reverse-engineering of networks. While our hope was still that this would ultimately help AGI go well, our main focus in practice was on getting closer to general deep understanding. [↩︎](#fnref-KmquKGGECppkY6hJw-1)

2.

Though we think that pragmatically useful tools have come out of it [↩︎](#fnref-KmquKGGECppkY6hJw-2)

3.

Ideal length varies, we often aim for an aggressive 2 weeks [↩︎](#fnref-KmquKGGECppkY6hJw-3)

4.

The "task" can be as simple as: "Based on my hypothesis, I predict intervention X will have effect Y." If you're right, that's evidence your understanding is real. But if you can’t find a proxy task validating your insights, just move on and try another approach/problem. [↩︎](#fnref-KmquKGGECppkY6hJw-4)

5.

In our opinion, today’s alignment evaluations are highly contrived and confounded in many ways, but we don’t think this significantly detracts from the lessons we draw from this case study [↩︎](#fnref-KmquKGGECppkY6hJw-5)

6.

The real reason we believe in these is from aggregating lessons from many research projects, so this case study is not a crux, but we think this is an unusually clear demonstration. [↩︎](#fnref-KmquKGGECppkY6hJw-6)

7.

Eval aware behaviour was theorised for many years but not observed pre 2025, beyond minor “this is a needle in a haystack test” observations [↩︎](#fnref-KmquKGGECppkY6hJw-7)

8.

Conversely, we do not think it is a perfect proxy, and it is key to [constantly examine this for your proxy tasks](#heading=h.um2tf0f4mixm), e.g. is it really “fictional scenario” awareness? [↩︎](#fnref-KmquKGGECppkY6hJw-8)

9.

For example, the model can detect LLM-written text, ruling out most cheap methods of eval creation [↩︎](#fnref-KmquKGGECppkY6hJw-9)

10.

While this was not the main purpose of SAEs, when we worked on SAEs last year, we would certainly have predicted that SAEs would make it easier to steer against an abstract concept like eval awareness. [↩︎](#fnref-KmquKGGECppkY6hJw-10)

11.

We find it striking that we can’t think of an alternative method that we expect to outperform steering here. [↩︎](#fnref-KmquKGGECppkY6hJw-11)

12.

Note that this is extremely similar to the idea of downstream tasks or downstream applications, e.g. [as discussed by Sam Marks](https://www.alignmentforum.org/posts/wGRnzCFcowRCrpX4Y/downstream-applications-as-validation-of-interpretability). We call them proxy tasks and couple them with the North Star because we think that downstream tasks are useful for producing true insights, but not necessarily important insights, so having some North Star that broadly connects back to the big picture of AGI safety puts you in a much better place. The second reason is that by putting "proxy" in the name, it reinforces that this is not your actual goal. This is not some benchmark to blindly optimise. This is a useful tool to track progress towards your real goal, but it is fragile and may cease to be a good tool if you're not careful. [↩︎](#fnref-KmquKGGECppkY6hJw-12)

13.

This is far from the whole problem, but is an important sub-problem! [↩︎](#fnref-KmquKGGECppkY6hJw-13)

14.

For example, suppressing eval awareness causes Sonnet to act more misaligned. But perhaps Sonnet would never act misaligned, and the eval awareness vector contains some misalignment-related concepts, which induced the behavior. We don't think this is actually happening in that example, but it is an important confounder to check for. [↩︎](#fnref-KmquKGGECppkY6hJw-14)

15.

And also some of the most tractable for empirical work, since current systems will be better proxies [↩︎](#fnref-KmquKGGECppkY6hJw-15)

16.

See an attempt at a clearer definition in [the appendix](#heading=h.kqfatkvvnbr8) [↩︎](#fnref-KmquKGGECppkY6hJw-16)

17.

Here, model behaviour or cognition [↩︎](#fnref-KmquKGGECppkY6hJw-17)

18.

It’s difficult to judge exactly how much this mindset is over or under supplied. However, our perception is that this approach seems overrepresented in interpretability, especially compared to the frontier language model research communities (less so to ML academia writ large). If nothing else, safety researchers interested in empirical science seem more likely to be drawn to mech interp, historically. [↩︎](#fnref-KmquKGGECppkY6hJw-18)

19.

Of course, many simpler tools like reading the chain of thought are also very effective, and often our first resort. [↩︎](#fnref-KmquKGGECppkY6hJw-19)

20.

Note - we are excited about model organisms that are designed to exhibit a specific safety-relevant property and be studied. We’re less excited about more ambitious attempts to make [a general model of a misaligned future model](https://www.alignmentforum.org/posts/ChDH335ckdvpxXaXX/model-organisms-of-misalignment-the-case-for-a-new-pillar-of-1), that can be studied/mitigated for a wide range of behaviours [↩︎](#fnref-KmquKGGECppkY6hJw-20)

21.

Model organisms are [far from perfect](https://arxiv.org/abs/2510.13900), but we think they're good enough to enable impactful projects. We’re excited to see work red-teaming and refining model organism creation methods! [↩︎](#fnref-KmquKGGECppkY6hJw-21)

22.

This is not a crux for our pivot, but our overall interpretation of all this is that networks have some legible structure showing the key, qualitative factors driving their behaviour, and a long tail of increasingly messy and arcane heuristics that also matter for performance. It seems to us that these successes are a result of focusing on the prominent, legible structure, and little progress has been made on the messy heuristics. We are excited about figuring out the limits of what we can do with the legible structure, and are okay with strategies that ignore/bound the messy heuristics, even if this means inherently incomplete understanding. [↩︎](#fnref-KmquKGGECppkY6hJw-22)

23.

In particular, when SAEs are made larger, they [capture new concepts that were previously in the error terms](https://arxiv.org/abs/2502.04878), suggesting this isn’t just interference from superposition [↩︎](#fnref-KmquKGGECppkY6hJw-23)

24.

Further, you can combine a pragmatic approach and ambitious reverse-engineering - the question is just how can you demonstrate that you are actually finding true and important insights [↩︎](#fnref-KmquKGGECppkY6hJw-24)

25.

The below is focused on sparse autoencoders, but we think the lessons likely apply to other kinds of dictionary learning, like transcoders and crosscoders, which we’ve found to have similar strengths and weaknesses [↩︎](#fnref-KmquKGGECppkY6hJw-25)

26.

[Nguyen et al](https://www.goodfire.ai/research/rakuten-sae-probes-for-pii-detection) shows that SAEs seem better for forming PII classifiers, which is an interesting counterpoint, but even there the SAE loses on English only data. [↩︎](#fnref-KmquKGGECppkY6hJw-26)

27.

Technically this was cross-layer transcoders, but the point stands [↩︎](#fnref-KmquKGGECppkY6hJw-27)

28.

For example, to simulate a future setting where you’re trying to interpret a superhuman AI (and so you cannot reliably interpret its outputs yourself), you could say that you can’t look at the outputs of the current model, you can only show them to a weaker model. [↩︎](#fnref-KmquKGGECppkY6hJw-28)

29.

For example, we think that detecting deception in vector-based chain-of-thought is an extremely important problem, but we’re sufficiently uncertain about what future vector-based CoT models will look like that it’s difficult to productively study. [↩︎](#fnref-KmquKGGECppkY6hJw-29)

30.

See our paper "Refusal in Language Models Is Mediated by a Single Direction." [↩︎](#fnref-KmquKGGECppkY6hJw-30)

31.

We note that this is far from a perfect proxy. In particular, researchers were given a dataset of which a small fraction were the obviously suspicious fine-tuning documents, meaning that some solutions amounted to a fancy semantic search, and it is highly unclear to us that this would work on the real thing. But we still think it was great work that contributed real insights about how to identify hidden goals. [↩︎](#fnref-KmquKGGECppkY6hJw-31)

32.

Especially more niche discoveries, or things that are a pain to discover. If the thing you’re investigating went viral, e.g. emergent misalignment, a lot of other people will have the same idea [↩︎](#fnref-KmquKGGECppkY6hJw-32)

33.

If you backtrack too little you get stuck, if it’s too much you go in circles, so it’s a hard problem! And partially depends on the model’s own abilities [↩︎](#fnref-KmquKGGECppkY6hJw-33)

34.

This is a good example of how proxy tasks are not benchmarks to optimise. There’s many ways to cheat and find a steering vector that will mess with the model saying I don’t know. We think this one was interesting because it was found via an SAE with a search process that made no reference to refusing to answer, suggesting a non-trivial connection [↩︎](#fnref-KmquKGGECppkY6hJw-34)

35.

5 people total [↩︎](#fnref-KmquKGGECppkY6hJw-35)

36.

We've also found that with real models, each additional layer of complexity creates real burden - another hyperparameter, more code, more places for bugs. This matters especially for research on frontier models (slower feedback loops, higher computational cost), and even more for techniques run in production. If your thing is too complicated, no one will use it. [↩︎](#fnref-KmquKGGECppkY6hJw-36)

37.

In some follow-up work, [Palisade](https://palisaderesearch.org/) found that some Codex models occasionally still resist shutdown even with this intervention. We can't really investigate this since the models are closed source, but we speculate that models specialised for coding tasks may have a predisposition to seek out things shaped like "coding puzzles," and disabling [shutdown.sh](http://shutdown.sh) has this flavor. [↩︎](#fnref-KmquKGGECppkY6hJw-37)

38.

And there are various others like and [having the model generate a user turn](https://assets.anthropic.com/m/64823ba7485345a7/Claude-Opus-4-5-System-Card.pdf#page=84.69) can surface secrets the assistant won’t admit. [↩︎](#fnref-KmquKGGECppkY6hJw-38)

39.

Token force the model to begin its answer with e.g. “My secret plan is” and then continue the rollout from there, and hope this can get a truer sense of what the model thinks [↩︎](#fnref-KmquKGGECppkY6hJw-39)

40.

Unless, e.g., applying other methods on your problem just doesn’t even seem possible [↩︎](#fnref-KmquKGGECppkY6hJw-40)

41.

Though highly complex techniques are often fairly intractable to use in production on frontier models, so the proxy task would need to account for scale [↩︎](#fnref-KmquKGGECppkY6hJw-41)

42.

Credit to Arthur Conmy for articulating this [↩︎](#fnref-KmquKGGECppkY6hJw-42)

43.

This is deliberately much broader than “a focus on mechanisms” or “a focus on reverse-engineering”, as some in the field may have claimed. We see that as a more niche means to an end. Sociologically, we think it’s clear that many in the mech interp community are working on things far broader than that, e.g. sparse autoencoders (which in our opinion have far too much approximation error to be considered reverse-engineering, and are about representations not mechanisms). Generally, we dislike having overly constraining definitions without a good reason to. [↩︎](#fnref-KmquKGGECppkY6hJw-43)

44.

In lieu of a better name, we sloppily use model internals to refer to “all ways of using the internals of a model that are not about understanding.” Suggestions welcome! [↩︎](#fnref-KmquKGGECppkY6hJw-44)

45.

Black box interpretability (non-mechanistic interpretability) covers a wide range: reading chain-of-thought (simple), prefill attacks (making a model complete "my secret is..."), resampling for reasoning models, and more. [↩︎](#fnref-KmquKGGECppkY6hJw-45)

# Policy-Aware Design of Large-Scale Factorial Experiments

paper_id: semanticscholar:84780eaf221baf924bf0c894a4bb41d07b6ca5ba
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Digital firms routinely run many online experiments on shared user populations. When product decisions are compositional, such as combinations of interface elements, flows, messages, or incentives, the number of feasible interventions grows combinatorially, while available traffic remains limited. Overlapping experiments can therefore generate interaction effects that are poorly handled by decentralized A/B testing. We study how to design large-scale factorial experiments when the objective is not to estimate every treatment effect, but to identify a high-performing policy under a fixed experimentation budget. We propose a two-stage design that centralizes overlapping experiments into a single factorial problem and models expected outcomes as a low-rank tensor. In the first stage, the platform samples a subset of intervention combinations, uses tensor completion to infer performance on untested combinations, and eliminates weak factor levels using estimated marginal contributions. In the second stage, it applies sequential halving to the surviving combinations to select a final policy. We establish gap-independent simple-regret bounds and gap-dependent identification guarantees showing that the relevant complexity scales with the degrees of freedom of the low-rank tensor and the separation structure across factor levels, rather than the full factorial size. In an offline evaluation based on a product-bundling problem constructed from 100 million Taobao interactions, the proposed method substantially outperforms one-shot tensor completion and unstructured best-arm benchmarks, especially in low-budget and high-noise settings. These results show how centralized, policy-aware experimentation can make combinatorial product design operationally feasible at platform scale.

## Method



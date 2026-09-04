# Automatic, Debiased, and Invariant Counterfactual Generation under General Interventions

paper_id: semanticscholar:13bc04d35f36a2975b983cba15ae3c7ed9a0271a
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Generative models for counterfactual outcomes have great potential to support decision-making under complex interventions, but existing approaches are limited by unstable estimation, poor generalization across environments, and bias from nuisance model misspecification. We introduce ADIGen, a framework for automatic, debiased, and invariant counterfactual generation under general interventions, including high-dimensional interventions and outcomes. ADIGen combines Riesz regression to avoid unstable density-ratio estimation, causal invariance to improve generalization under distribution shift, and orthogonal statistical learning to obtain doubly robust guarantees against nuisance model misspecification. We provide excess-risk bounds showing that ADIGen controls counterfactual risk under general interventions, with a product-bias nuisance remainder and an invariant risk bound across environments. We then extend this framework to multiple, interacting objects with a joint intervention, and apply ADIGen to counterfactual world modeling. In contrast to standard statistical settings, the joint outcome is modeled natively without the need for exposure mappings or direct/indirect effect decompositions.

## Method



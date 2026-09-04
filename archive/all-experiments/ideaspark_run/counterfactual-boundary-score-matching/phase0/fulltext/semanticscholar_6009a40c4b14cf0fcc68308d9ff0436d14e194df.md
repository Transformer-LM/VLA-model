# Global Convergence of Wasserstein Policy Gradient for Entropy-Regularized Reinforcement Learning

paper_id: semanticscholar:6009a40c4b14cf0fcc68308d9ff0436d14e194df
tier: T2
source_used: failed
warning: fetch failed across all paths; intro filled with abstract; method empty

## Intro

Wasserstein policy gradient (WPG) is a policy optimization method for reinforcement learning (RL) that exploits the optimal-transport geometry of action distributions. For the entropy-regularized RL objective, WPG evolves each state-conditional policy by transporting it along the action gradient of the soft Q-function together with a Langevin-type diffusion. Despite its appeal for continuous-control problems, its global convergence properties remain poorly understood. Standard Langevin analyses do not directly apply, because the RL objective depends on the policy through the Bellman recursion rather than through a static convex functional, and the Langevin drift is determined by the soft Q-function, whose regularity must be controlled along the policy iterates. In this paper, we develop a global convergence theory for WPG by exploiting the Bellman structure of entropy-regularized RL. We show that the role usually played by convexity can be replaced by a Bellman-based argument: the soft Bellman residual admits a statewise KL representation with respect to a Gibbs policy; Bellman contraction relates this residual to the global optimality gap; and a Bellman resolvent identity connects value improvement to relative Fisher information. Combined with a uniform log-Sobolev inequality (LSI) for the evolving Gibbs family, these ingredients yield a distributional Polyak--\L{}ojasiewicz condition. We further establish the regularity and uniform bounds needed to control the discretization error, thereby obtaining geometric contraction up to a discretization bias. Conceptually, our analysis shows that although entropy-regularized RL is not convex in the usual flat sense, the Bellman recursion induces a favorable Polyak--Lojasiewicz-type (PL) geometry that supports global convergence of WPG.

## Method



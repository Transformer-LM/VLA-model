import math

def masks_from_violation(v):
    first = next((i for i, flag in enumerate(v) if flag), None)
    if first is None: return [], [], []
    last = first
    while last + 1 < len(v) and v[last + 1]: last += 1
    return list(range(first)), list(range(first, last + 1)), list(range(last + 1, len(v)))

def errors(theta, action): return [(theta*x)**2 for x in action]
def score(theta, action, mask): return -sum(errors(theta, action)[i] for i in mask)/len(mask)
def delta(theta, theta0, action, mask): return score(theta, action, mask)-score(theta0, action, mask)
def margin(theta, theta0, p, a0, mask): return delta(theta,theta0,p,mask)-delta(theta,theta0,a0,mask)
def loss(z): return math.log1p(math.exp(-z))
def grad(f,x,h=1e-6): return (f(x+h)-f(x-h))/(2*h)

theta0=0.5; lr=0.1; beta=1.0
a0=[0.,1.,0.]; p1=[1.,0.,0.]; p2=[2.,0.,0.]
P,M,S=masks_from_violation([False,True,False])
e=errors(theta0,a0); E=(sum(e),sum(e[i] for i in P),sum(e[i] for i in M),sum(e[i] for i in S))
f_mask=lambda th: loss(beta*margin(th,theta0,p1,a0,M))
f_full=lambda th: loss(beta*margin(th,theta0,p1,a0,[0,1,2]))
g_mask=grad(f_mask,theta0); g_full=grad(f_full,theta0)
th_mask=theta0-lr*g_mask; th_full=theta0-lr*g_full
def lout(th):
    terms=[((th*a[i])-(theta0*a[i]))**2 for a in (a0,p1) for i in P+S]
    return sum(terms)/len(terms)
print('decomposition',E,E[0]==E[1]+E[2]+E[3])
print('masked',margin(theta0,theta0,p1,a0,M),f_mask(theta0),g_mask,th_mask)
print('complement_drift',abs((th_mask-theta0)*p1[0]))
print('masked_positive_scores',score(th_mask,p1,M),score(th_mask,p2,M))
print('L_out_init_and_analytic_grad',lout(theta0),0.0,'lambda_match','division_by_zero')
print('alt_losses',sum(errors(theta0,p1))/3,sum(errors(theta0,p2))/3)
print('beta_zero_std','division_by_zero')
print('naive',f_full(theta0),g_full,th_full,'update_gap',th_mask-th_full)

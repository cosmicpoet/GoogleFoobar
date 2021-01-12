# Challenge: Doomsday Fuel

## Problem Description

Making fuel for the LAMBCHOP's reactor core is a tricky process because of the exotic matter involved. It starts as raw ore, then during processing, begins randomly changing between forms, eventually reaching a stable form. There may be multiple stable forms that a sample could ultimately reach, not all of which are useful as fuel. 

Commander Lambda has tasked you to help the scientists increase fuel creation efficiency by predicting the end state of a given ore sample. You have carefully studied the different structures that the ore can take and which transitions it undergoes. It appears that, while random, the probability of each structure transforming is fixed. That is, each time the ore is in 1 state, it has the same probabilities of entering the next state (which might be the same state).  You have recorded the observed transitions in a matrix. The others in the lab have hypothesized more exotic forms that the ore can become, but you haven't seen all of them.

Write a function solution(m) that takes an array of array of nonnegative ints representing how many times that state has gone to the next state and return an array of ints for each terminal state giving the exact probabilities of each terminal state, represented as the numerator for each state, then the denominator for all of them at the end and in simplest form. The matrix is at most 10 by 10. It is guaranteed that no matter which state the ore is in, there is a path from that state to a terminal state. That is, the processing will always eventually end in a stable state. The ore starts in state 0. The denominator will fit within a signed 32-bit integer during the calculation, as long as the fraction is simplified regularly. 

For example, consider the matrix m:

```
[
  [0,1,0,0,0,1],  # s0, the initial state, goes to s1 and s5 with equal probability
  [4,0,0,3,2,0],  # s1 can become s0, s3, or s4, but with different probabilities
  [0,0,0,0,0,0],  # s2 is terminal, and unreachable (never observed in practice)
  [0,0,0,0,0,0],  # s3 is terminal
  [0,0,0,0,0,0],  # s4 is terminal
  [0,0,0,0,0,0],  # s5 is terminal
]
```

So, we can consider different paths to terminal states, such as:

```
s0 -> s1 -> s3
s0 -> s1 -> s0 -> s1 -> s0 -> s1 -> s4
s0 -> s1 -> s0 -> s5
```

Tracing the probabilities of each, we find that

```
s2 has probability 0
s3 has probability 3/14
s4 has probability 1/7
s5 has probability 9/14
```

So, putting that together, and making a common denominator, gives an answer in the form of
`[s2.numerator, s3.numerator, s4.numerator, s5.numerator, denominator]` which is
`[0, 3, 2, 9, 14]`.

### Test cases

Your code should pass the following test cases.

Note that it may also be run against hidden test cases not shown here.

```
-- Java cases --
Input:
Solution.solution({{0, 2, 1, 0, 0}, {0, 0, 0, 3, 4}, {0, 0, 0, 0, 0}, {0, 0, 0, 0,0}, {0, 0, 0, 0, 0}})
Output:
    [7, 6, 8, 21]

Input:
Solution.solution({{0, 1, 0, 0, 0, 1}, {4, 0, 0, 3, 2, 0}, {0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0}})
Output:
    [0, 3, 2, 9, 14]

-- Python cases --
Input:
solution.solution([[0, 2, 1, 0, 0], [0, 0, 0, 3, 4], [0, 0, 0, 0, 0], [0, 0, 0, 0,0], [0, 0, 0, 0, 0]])
Output:
    [7, 6, 8, 21]

Input:
solution.solution([[0, 1, 0, 0, 0, 1], [4, 0, 0, 3, 2, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])
Output:
    [0, 3, 2, 9, 14]
```

## General Solution

After 6 years in a not-very-related industry, I have given most of my Linear Algebra back to my Math professor. Yet, my first intuition when seeing it is that these input matrices can be easily converted to probability or Stochastic matrices. This suggests that it's more of a Linear Algebra / Markov chain problem, than a coding problem.

With some googling, I realized this is a typical Absorbing Markov chain problem where we need to find the probabilities of ending up in absorbing states (what they call terminal states in the problem description). [Wikipedia page for Absorbing Markov chain](https://en.wikipedia.org/wiki/Absorbing_Markov_chain) has all the information needed on how to find the absorbing probabilities. I also find [a very useful article by ivanseed](https://github.com/ivanseed/google-foobar-help/blob/master/challenges/doomsday_fuel/doomsday_fuel.md) where he ran through one test case in details to show how the calculation works. 

In essence, we need to:

1. **Transform** the input matrix so that the transient state rows and absorbing state rows are grouped and ordered, and then **convert** the input matrix to a proper probability matrix (where each row sums to 1).
2. In **Canonical** form, find the `R` and `Q` sub-matrices.
3. Get the Fundamental matrix <code>F = (I - Q)<sup>-1</sup></code>, calculated by getting **inverse** of `I - Q`.
4. Get `FR` by **matrix multiplication**.
5. Since the problem specifies that **we always start at s0**, the probabilities we need is just the first row `FR[0]`.
6. Get the **least common denominator** (LCD) of the probabilities, **convert** the answer by first multiplying the probabilties by the LCD, then push the LCD to the end of the answer list/array.

Note that for foobar I'd like to not import other packages too much. However, because we are working with probabilities here, at bare minimum I want `fractions` library in Python, otherwise it's just too tricky to get accurate answer. Also, I wasn't sure if `numpy` is allowed in Google foobar, but even if it is, I remember it acts funky when working with fractions. Therefore I chose to just brute-force implement by own necessary matrix operations.

## Tips

The algorithm itself should be easy enough to follow. Below are not so much tips but rather the issues I ran into when tackling this problem. Hope it helps you as well.

* Overall, the 2 given test cases are to generic, there are quite some edge cases to take care of in those hidden test cases.
* Since we always start at s0, there is a special case where s0 itself is a terminal state. In that case the answer should just be `[1, 0, ..., 0, 1]`, because we will never come out of s0.
* Initial input matrix transformation: I believe it's much easier to first do the transformation, and then to convert it to a probability matrix. If you do the transformation first, then the converted matrix is automatically in its Canonical form. During the transformation, not only we need to change the ordering of the rows of the matrices, but we also need to change the ordering of columns in EACH row accordingly. After that we can just convert the transformed input matrix to a probability matrix.
* There are several ways to implement matrix inversion. The one I chose is by [using minors and cofactors](https://en.wikipedia.org/wiki/Minor_(linear_algebra)#Inverse_of_a_matrix). Personally I feel this is the most straightforward to implement. 
* If you are like me who implmented matrix operations myself, note that there are special cases when the matrix is 1x1 and 2x2. Matrices with sizes of 3x3 and beyond though should be just generic.
* Again, this is a very brute-force implementation. Since at maximum we will only work with a 10x10 matrix, I didn't bother optimizing the code at all.

## Source Code

[answer.py](https://github.com/WhiskeyRomeoTango/GoogleFoobar/blob/main/challenges/doomsday-fuel/answer.py)

For reference and comparison purposes only. Please do not use my solution directly for foobar. It's not helping you or me. 

## Bonus Reading

I stumbled upon [this article / textbook page](http://www.math.ubc.ca/~tbjw/ila/stochastic2.html) when I brushed up my Stochastic matrix. It has an interesting section about Google matrix - how it evolutionized Internet search and page ranking. It's a quick interesting read, and you'll see why Google loves to ask these linear algebra questions in their interviews - their company was founded by some linear algebraists after all! :)

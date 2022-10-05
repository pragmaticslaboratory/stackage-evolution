# Stackage Repository: An Exploratory Study of its Evolution

**Context**. Package repositories for a programming language are increasingly common. A repository can keep a register of the evolution of its packages. In the programming language Haskell, with its defining characteristic monads, we can find the Stackage repository, which is a curated repository for stable Haskell packages in the Hackage repository. Despite the widespread use of Stackage in its industrial target, we are not aware of much empirical research about how this repository has evolved, including the use of monads. 

**Objective**. This paper conducts an empirical research about the evolution of Stackage considering monads through 20 LTS (Long-Term Support) releases during the period 2014-2022. Focusing on five research questions, this evolution is analyzed in terms of packages with their dependencies and imports; including the most used monad packages. To the best of our knowledge, this is the first large-scale analysis of the evolution of the Stackage repository with regard to packages used and monads.

**Method**. To answer the five research questions, we downloaded 45,716 packages (15.0 GB) that belong to 20 releases. From each package, we parse its cabal file and source code to extract the data, which is analyzed in terms of dependencies and imports using Python libraries like Pandas.

**Results**. The methodology allowed us to find diverse findings. For example, a growing trend of packages is depending on other packages whose versions are not available in a particular release of Stackage; opening a potential stabil- ity issue. Another example, mtl and transformers are on the top 10 packages most used/imported in some releases of the Stackage evolution. We discussed these findings with Stackage maintainers and allowed us to refine a research questions.

**Conclusions**. On the one hand, like previous studies, these results may evidence how developers use Haskell and give guidelines to Stackage maintainers. One of our proposals is to generate control over the categories and stability that developers assign to their packages. On the other hand, indicate that Stackage designers take more care when verifying the versions of package de- pendencies.


## Script

To download and process the Stackage LTS releases, you need edit the `main.py` to insert the releases to analyze. Later, this script should be executed. 
**Note**: This script works on a Linux distribution or using [WSL](https://docs.microsoft.com/en-us/windows/wsl/install) on Windows.   

## Data

This exploratory study is developed by [Felipe Ruiz](https://github.com/fruizrob) and [Nicolás Sepulveda](https://github.com/NicoSv19), under the supervision of [Paul Leger](http://pleger.cl) and [Ismael Figueroa](https://ifigueroap.github.io/) at [Pragmatics Lab](http://pragmaticslab.com)

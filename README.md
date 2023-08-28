
This software is created to analyze the evolution of the [Stackage](https://www.stackage.org) repository, and its analysis is reported in:

[!WARNING] 
The title and abstract are temporary.

_Title:_ Stackage Repository: An Exploratory Study of its Evolution
 
_Abstract:_  

**Context**. Package repositories for a programming language are increasingly common. A repository can keep a register of the evolution of its packages. In the programming language Haskell, with its defining characteristic monads, we can find the Stackage repository, which is a curated repository for stable Haskell packages in the Hackage repository. Despite the widespread use of Stackage in its industrial target, we are not aware of much empirical research about how this repository has evolved, including the use of monads. 

**Objective**. This paper conducts an empirical research about the evolution of Stackage considering monads through 20 LTS (Long-Term Support) releases during the period 2014-2022. Focusing on five research questions, this evolution is analyzed in terms of packages with their dependencies and imports; including the most used monad packages. To the best of our knowledge, this is the first large-scale analysis of the evolution of the Stackage repository with regard to packages used and monads.

**Method**. To answer the five research questions, we downloaded 51,816 packages (15.2 GB) that belong to 22 releases. From each package, we parse its cabal file and source code to extract the data, which is analyzed in terms of dependencies and imports using Python libraries like Pandas.

**Results**. The methodology allowed us to find diverse findings. For example, a growing trend of packages is depending on other packages whose versions are not available in a particular release of Stackage; opening a potential stabil- ity issue. Another example, mtl and transformers are on the top 10 packages most used/imported in some releases of the Stackage evolution. We discussed these findings with Stackage maintainers and allowed us to refine a research questions.

**Conclusions**. On the one hand, like previous studies, these results may evidence how developers use Haskell and give guidelines to Stackage maintainers. One of our proposals is to generate control over the categories and stability that developers assign to their packages. On the other hand, indicate that Stackage designers take more care when verifying the versions of package de- pendencies.


## Scripts

This repository contains scripts for different purposes:

* **Define LTS releases to analyze**. In the ``src`` folder, you can add the releases to analyze modfying the file ``lts_list.csv``. As an example, you can find all releases up to the relase ``20-15``. 

* **Download LTS releases**. In ``src/``, you should execute the Python script ``scrapy_lts.py`` using a Python interpreter (tested with ``Python 3.9.6``). This process can take hours. _Note:_ Please, install all Python libraries required. The downloaded package will be in the folder ``lts_downloaded/tar_package``. For each relases, a folder will be created.      

* **Install Haskell and create parsers**. First, install [ghcup](https://www.haskell.org/ghcup/install/) to install the [Glasgow Haskell Compiler](https://www.haskell.org/ghc/). Second, install [just](https://just.systems/) to create the required parsers. Then, in ``src/parse``, execute the following commands: ``just install-libs``, ``just make-parse-cabal``, ``just make-package-info-json``, and ``just make-package-imports``.

* **Create DataFrames**. Excute the script ``generate_dfs.py`` in ``src``. The dataframes are stored in the folder ``data/dfs``. For each release, a folder is created. As an example, you can find all dataframes up to the release ``20-15``.

* **Create DataFrames Revised**. This is an _optional step_. If you need to analyze considering the revision of each package, you can execute the same scripts (``scrapy_lts.py`` and ``generate_dfs.py``) using the argument ``--revised``. For the revised versions, ``scrapy_lts.py`` will donwload the packages in the folder ``lts_download/revised_cabal``, and ``generate_dfs.py`` will create the dataframes in the folder ``dfs_revised``.  

## Research Questions and Answers

For the paper, we replied a set of research questions, which are available and can be tested online in the folder ``notebooks``. The pieces of code associated with the research questions are implemented in Python using [Jupiter](https://jupyter.org/).      


## Research

This exploratory study is developed by Felipe Ruiz, Nicolas Sepulveda, [Paul Leger](http://pleger.cl), [Ismael Figueroa](https://ifigueroap.github.io/), and [Nicolás Cardozo](https://github.com/ncardozo) at [Pragmatics Lab](http://pragmaticslab.com). 




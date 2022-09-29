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

This exploratory study is developed by Felipe Ruiz and Nicolas Sepulveda, under the supervision of [Paul Leger](http://pleger.cl) and [Ismael Figueroa](https://ifigueroap.github.io/) at [Pragmatics Lab](http://pragmaticslab.com)

## Project

El proyecto consta de 5 carpetas principales donde se maneja todo lo necesario para ver los resultados de esta investigación.

Carpetas: 
1.- data 
2.- graphs
3.- lts_downloaded
4.- notebooks
5.- src

1.- La carpeta 'data' es donde encontraremos todos los Data Frames que se utilizan para los analisis. Esta carpeta posee dos subcarpetas, la primera se llama Dfs la cual posee todos los Data Frames separados por LTS, este es el conjunto de datos que se utiliza para las Research Question (RQ). La segunda subcarpeta se llama Dfs_Revissed que posee igualmente Data Frames separados por LTS pero que unicamente poseen información de los Cabal revisados por Stackage, este set de datos se usa unicamente para la RQ1.

2.- La carpeta 'graphs' es donde se almacenan todos los graficos en formato pdf. Estos se generan automaticamente al ejecutar los notebooks de las RQ presente en la carpeta notebooks/Answers.

3.- La carpeta 'lts_downloaded' posee todos los paquetes descargados por LTS, en esta carpeta es de donde se extrae la data para generar nuestros Data Frames.

4.- La carpeta 'notebook' posee dos subcarpetas, una de ellas es misc, que contiene scripts de los inicios de este proyecto, que actualmente no tienen relacion a los hallazgos encontrados por nuestras Research Question.

Dentro de 'notebook' hay una subcarpeta llamada 'Answers', en esta carpeta se encuentran todos los notebooks de las RQ, cada notebook tiene en su nombre la RQ que va a responder. Ademas, en el contenido de ellos se encuentra información de la pregunta que buscan responder. Finalmente dentro de 'Answers' se encuentra la carpeta llamada 'util', dentro de ella se encuentra un unico archivo llamado api. 
La api es donde se encuentran la mayoria de metodos que son utilizados por los notebooks de las RQ. 

Mediante uno va ejecutando los notebooks de las RQ se van generando los graficos en formato pdf y almacendandose en la carpeta 'graphs'.
Si estas en Jupyter ejecutando las RQ es tan simple como apretar el boton de ejecución que trae Jupyter como tal, recomiendo instalar los paquetes utilizados si es que no los poseen mediante el comando pip install [package]

5.- La carpeta 'src' es donde se encuentra el nucleo del proyecto para obtener nuestra información que analizamos. Dentro encontramos 4 subcarpetas:

5.1.- features
5.2.- parse
5.3.- scrapy
5.4.- util

El programa main.py es quien se encarga de construir todos los Data Frames e ir almacenandolos dentro de la carpeta data, la subcarpeta varia segun la indicación que se le indique. 
5.1.- Para hacer el proceso de generar los Data Frames utiliza las pipes presente en la carpeta features, cada pipe tiene su funcionalidad y transforma el formato de la data o añade nueva información a los Data Frames.

*--------------------------------- Ejecución -------------------------------*
Para ejecutar el main es necesario estar ubicado en la consola en la carpeta src. Hay que considerar que es necesario tener instalado python para la ejecucion.
El comando es 

python main.py [args] or python3 main.py [args]

hay algunos argumentos que se les pueden pasar al comando: 
* -v para ver los logs que va generando el programa
* -q para no ver los logs y unicamente errores
* --wsl este comando es por si te encuentras en windows y deseas ejecutarlo en el entorno de wsl (*Opcional)
* --revised este comando es por si deseas generar los Data Frames a partir de las versiones revisadas de los Cabal (Si no se especifica genera los Data Frames con la información presente en los paquetes con extension .tar)

Example:
    python main.py -q --revised

*----------------------------------------------------------------*

5.2.- En la carpeta parse es donde se encuentran los programas hechos en Haskell que se encargan de parsear la información de los paquetes que recibe, y asi poder transformarla en data utilizable para los analisis. Estos parse son llamados por las mismas pipes cuando estan siendo ejecutadas.
**Consideración** 
Los parse para que sean funcionales y puedan ser ejecutados por las pipes es necesario generar un ejecutable de ellos, sino las pipes generaran Data Frames vacios.

5.3.- La carpeta scrapy es donde se encuentra el proyecto de scrapy, el cual mediante spiders se encarga de extraer los nombres de los paquetes por lts en la web de Stackage, para luego buscar en Hackage y descargar el archivo comprimido de extensión .tar donde se encuentra la información completa del paquete, o la version revisada que solo posee el archivo .cabal del paquete. Las descargas se van almacenando directamente en la carpeta de lts_downloaded

*--------------------------------- Ejecución -------------------------------*
posicionarse en src/scrapy/packagebot

scrapy crawl stackage 

*----------------------------------------------------------------*
5.4.- La carpeta util tiene programas utilizados por el main.py, en concreto son los argumentos que se les puede pasar al comando de ejecucion del main.

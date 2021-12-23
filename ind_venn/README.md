# TOPN VENN DIAGRAM GENERATOR
## Description
Python application to generate venn diagram visualizations of common ngrams between groups.
Process individual's ngram data into Venn Diagrams. Given a specific ngram length N, 3 groups
to inspect G={MW, Ver, Vis, ec/eo}, a specific type type to inspect T in
{clock, event, peak}, and optionally a prefix spec, suffix spec, and top
presenting results Q. Then generates the corresponding venn diagram, taking
the top Q common Ngrams between the groups in G of type T.

## Prerequisites
Run the following commands from the root folder:
```
pip3 install -r requirements.txt
```

Run the following commands from the folder containing the python script `gen_venn.py` to setup:
```
mkdir out
```

## How to use the Application
First, ensure that you have the required data, specifically a csv file of form `*gram.csv`, which contains columns of name `C{1-26}_R{1-3}_{MW,Ver,Vis,ec/eo}_{clock,event,peak}`, and rows with names of the ngrams, and each field represents the frequency of that ngram for the respective subject. The data parser relies on the format of data followed by these files. Once you have these files, create a folder `data` in the directory of `gen_venn.py` and put the csv file in this folder.

To run the application, note it has the following interface:
```
usage: gen_venn.py [-h] [-Q TopQ] [-R Run] [-S Suffix] [-I Inds [Inds ...]]
                   N G1 G2 G3 T F

positional arguments:
  N                   Length of ngram
  G1                  Group 1 of groups {MW, Ver, Vis, ec/eo}
  G2                  Group 2 of groups {MW, Ver, Vis, ec/eo}
  G3                  Group 3 of groups {MW, Ver, Vis, ec/eo}
  T                   Type of type {clock, event, peak}
  F                   File containing SZO data

optional arguments:
  -h, --help          show this help message and exit
  -Q TopQ             Present top Q occuring (default: 5)
  -R Run              Specify run of the data to use {1, 2, 3} (default: 1)
  -S Suffix           Specify suffix of the data to use {1, 2} (default: *)
  -I Inds [Inds ...]  Specify individuals {1,...,26} (default: *)
```

So, at the minimum, you must specify N, G1, G2, G3, T and F, the additional fields are optional.

For example, if I want to run the visualization for 5-length ngrams for groups Ver, Vis, MW, for the type clock, with my data file being contained in *relative path* `data/5gram.csv`, I would execute the following:
```
python3 gen_venn.py 5 Ver Vis MW clock data/5gram.csv
```

Then, if I want to further specify that I want to only look at individuals 7,8,9, I would specify the optional argument as `-I 7 8 9`. If I want to view only the top 12 common ngrams, I would specify the optinal argument as `-Q 12`.
So, together with the specifications from above, I would run:
```
python3 gen_venn.py 5 Ver Vis MW clock data/5gram.csv -I 7 8 9 -Q 12
```

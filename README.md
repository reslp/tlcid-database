# Lichen substance database

This repository hosts the lichen substance database for use with the TLCid software.

## Contents

The database is constructed from two main text files. They contain chemical data on 800+ substances as well as 20000+ entries of substances detected from different lichens. These two files form the basis of the database file underlying the [TLCid](https://reslp.github.io/tlcid) software. 

```
data/chemical_data.csv
data/lichen_substance_data.csv
```

## Data origin

Chemical data is based on A CATALOGUE OF STANDARDIZED CHROMATOGRAPHIC DATA AND BIOSYNTHETIC RELATIONSHIPS FOR LICHEN SUBSTANCES (6th editon; 2022) by John A Elix.

Occurence data of substances in lichen species is based on data from the [ITALIC](https://italic.units.it/) and [LIAS light](https://liaslight.lias.net/) databases.

Data sources for lichen substances are included in the file `data/lichen_substance_data.csv`


## Contribution

If you would like to have additional substances be included in the database there are different options:

1. Fork the repository, make modifications to the respective files and submit a Pull request.
2. Raise a Github issue with substance or lichen details and literature references.


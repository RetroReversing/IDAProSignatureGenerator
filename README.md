# Convert Whole libraries to .sig nd .pat files
Just copy your library that you want to make into a IDA-pro FLAIR signature into the libs directory, with a folder name that describes the library and run this script!
This script may need to be run more than once for a single library with modifications made to the libraries included as there are a couple of issues with pelf and sigmake.

## How to Run
```
python createPatAndSigFiles.py
```

# Problems to solve

## unknown relocation type 8
```
librtgcond.a: unknown relocation type 8. (section 1, addr 32c)
```
Very common with the Renderware libraries.
Not sure how to fix this issue, and what is a relocation type?
Even IDA Pro when opening the file says it contains "non standard use of relocations"
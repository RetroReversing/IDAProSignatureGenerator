# Convert Whole libraries to .sig nd .pat files
Just copy your library that you want to make into a IDA-pro FLAIR signature into the libs directory, with a folder name that describes the library and run this script!

This script may need to be run more than once for a single library with modifications made to the libraries included as there are a couple of issues with pelf and sigmake, especially with relocatable binaries.

## How to Run
```
python createPatAndSigFiles.py
```

## Automatic Collision Solving
In order to save time the script automatically fixes the .exc files by:
  * Picking the first candidate
  * adding collision_ to the name of the first candidate

This means that when you apply one of the signatures to a stripped binary and a symbol starts with collision_, you need to go to the .exc file to find out which one it was.
There is a couple of techniques to find out which of the collision candidates your function is correct, which will be covered later on.

# Problems to solve

## unknown relocation type 8
```
librtgcond.a: unknown relocation type 8. (section 1, addr 32c)
```
Very common with the Renderware libraries.
Not sure how to fix this issue, and what is a relocation type?
Even IDA Pro when opening the file says it contains "non standard use of relocations"

# Tools Required

Name | Description
--- | ---
pelf | Creates pattern files (.pat) from elf libraries (part of IDA Pro FLAIR tools)
sigmake | Create a signature file (.sig) from pattern files (part of IDA Pro FLAIR tools)
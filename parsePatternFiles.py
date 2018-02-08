import CommonUtilities
import subprocess
from subprocess import Popen, PIPE

def handleOneLine(single_line, symbolCount):
    parts_of_a_line = single_line.split(" ")
    # print "Full line:",single_line
    if len(parts_of_a_line) <5:
        return symbolCount
    # print parts_of_a_line[0]
    name = parts_of_a_line[5]
    # typeName = parts_of_a_line[7]
    print "Symbol Name:",name #, typeName
    return symbolCount+1
    #  I think the rest of the content is just references to other variables which are useful as part of the isgnature

    # rest_of_content = parts_of_a_line[6:]
    # for reference in rest_of_content:
    #     if reference.startswith(':') or reference.startswith('^') or reference.startswith('.'):
    #         continue
        # print reference

def handle_object_files_symbols(object_file_symbols):
    each_line = object_file_symbols.split('\n')
    name_of_object_file = each_line[0]
    symbol_names = each_line[1:]
    # print "# "+name_of_object_file
    # print symbol_names
    return len(symbol_names)


def get_symbols_from_library(libraryPath):
    symbolNumber = 0
    all_object_files_symbols = CommonUtilities.execute_command("nm -extern-only -just-symbol-name "+libraryPath).split('\n\n')
    for object_file_symbols in all_object_files_symbols:
        symbolNumber += handle_object_files_symbols(object_file_symbols)
    return symbolNumber

patternFileName = './libs/libsn/libc.a.pat'
symbolCount = 0
with open(patternFileName) as f:
        file_contents = f.read()
        all_lines = file_contents.split("\n")
        for single_line in all_lines:
            symbolCount=handleOneLine(single_line,symbolCount)
        print "Number of Symbols in pattern file:"+str(symbolCount)
      
#  TODO: compare pattern file symbols to the symbols got with nm command
countOfSymbolsFromNM = get_symbols_from_library('./libs/libsn/libc.a')
print "Number of symbols from NM:"+str(countOfSymbolsFromNM)
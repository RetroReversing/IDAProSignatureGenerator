import fnmatch
import os
import subprocess

def execute_command(bashCommand):
    return subprocess.check_output(bashCommand.split(),stderr= subprocess.STDOUT)

libraries = {}
for root, dirnames, filenames in os.walk('libs'):
    matches = []
    path_parts = root.split('/')
    library_name=root
    if (len(path_parts) > 1):
        library_name = path_parts[1]
    if not library_name in libraries:
        libraries[library_name] = {'patfiles':[]}    
    print 'Library:', library_name
    for filename in fnmatch.filter(filenames, '*.[aA]'):
        print "Filename:", filename
        full_path = (os.path.join(root, filename))
        output_path = full_path.replace(' ','_').replace('+','')+'.pat'

        # 
        # Now run pelf to get the patterns from the library
        # 
        bashCommands = ['./pelf', full_path, output_path]
        print ' '.join(bashCommands)
        output = subprocess.check_output(bashCommands,stderr= subprocess.STDOUT)

        libraries[library_name]["patfiles"].append(output_path)
        outputParts = output.split(' ')
        skipped = outputParts[2]
        total = outputParts[4]
        print "A file: ",outputParts, skipped, total
        matches.append(full_path+'.pat')


def moveOutputToGeneratedDirectory(libraryName, outputSigName, patternFiles):
    outputDirectory = "./generated/"+libraryName+"/"
    outputExcludedFile = libraryName+".exc"
    execute_command("mkdir -p "+outputDirectory+"/patternfiles/")
    execute_command("mv "+ outputSigName + " "+outputDirectory)
    # 
    # make sure to only copy the exc file as otherwise changes will be overwritten
    # 
    execute_command("cp "+ outputExcludedFile + " "+outputDirectory)
    print "Pattern files:"+patternFiles
    execute_command("cp "+ patternFiles + " "+outputDirectory+"/patternfiles/")

def parseExclusionsFile(outputExcludedFile):
    print "\nParsing Exclusions File:", outputExcludedFile
    with open(outputExcludedFile) as f:
        file_contents = f.read()
        collision_content = file_contents.split('\n\n')
        all_lines = file_contents.split('\n')
        if all_lines[0] != ';--------- (delete these lines to allow sigmake to read this file)':
            print "Already sorted ",outputExcludedFile
            return
        new_exc_contents=""

        for collision in collision_content[1:]:
            if "\n" in collision:
                new_exc_contents+= "+collision_"+collision+"\n\n"
            else:
                # One line collision
                new_exc_contents+= ""+collision+"\n\n"

        with open(outputExcludedFile, "w") as text_file:
            text_file.write(new_exc_contents)
        


def run_sigmake(libraryName,allPatternFilesAdded,outputSigName):
    bashCommand = './sigmake -n'+libraryName+' '+allPatternFilesAdded+' '+outputSigName
    print bashCommand
    output=""
    try:
        output = subprocess.check_output(bashCommand.split(),stderr= subprocess.STDOUT)
    except:
        print output

# 
# Create the signature (.sig) file for each library
# 
print "Now looping through libraries to create a single .sig file"
for libraryName in libraries:
    library = libraries[libraryName]
    if len(library['patfiles']) <1:
        # There is no pattern files generated for this library so skip it
        continue
    print "Generating signature for Library:",libraryName
    outputSigName = libraryName+'.sig'

    # 
    # Run sigmake to generate the .sig file
    # 
    allPatternFilesAdded = '+'.join(library['patfiles'])
    run_sigmake(libraryName,allPatternFilesAdded,outputSigName)

    outputExcludedFile = libraryName+".exc"
    parseExclusionsFile(outputExcludedFile)

    # 
    # Run sigmake again to make use of the modified .exc file
    # 
    run_sigmake(libraryName,allPatternFilesAdded,outputSigName)

    if os.path.isfile(outputSigName): 
        moveOutputToGeneratedDirectory(libraryName, outputSigName, ' '.join(library['patfiles']))
        print "Successfully Generated",outputSigName,"\n"
    elif os.path.isfile(outputExcludedFile):
        print "Please edit ",outputExcludedFile

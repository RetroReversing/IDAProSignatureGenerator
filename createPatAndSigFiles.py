import fnmatch
import os
import subprocess

verbose = False

def log_action(message):
    if verbose:
        print message

def execute_command(bashCommand):
    return subprocess.check_output(bashCommand.split(),stderr= subprocess.STDOUT)

def create_zip_file(libraryName):
    execute_command("mkdir -p ./generated/zips/")
    execute_command("zip -r ./generated/zips/"+libraryName+".zip ./generated/"+libraryName)


libraries = {}
for root, dirnames, filenames in os.walk('libs'):
    matches = []
    path_parts = root.split('/')
    library_name=root
    if (len(path_parts) > 1):
        library_name = path_parts[1]
    if not library_name in libraries:
        libraries[library_name] = {'patfiles':[], 'total':0}    
    log_action('Library: '+ library_name)
    for filename in fnmatch.filter(filenames, '*.[aA]'):
        log_action("Filename:"+ filename)
        full_path = (os.path.join(root, filename))
        output_path = full_path.replace(' ','_').replace('+','')+'.pat'

        # 
        # Now run pelf to get the patterns from the library
        # 
        bashCommands = ['./pelf', full_path, output_path]
        print ' '.join(bashCommands)
        output = subprocess.check_output(bashCommands,stderr= subprocess.STDOUT)

        libraries[library_name]["patfiles"].append(output_path)
        outputAfterColon = output.split(':')[1]
        outputParts = outputAfterColon.split(' ')
        skipped = outputParts[2]
        total = outputParts[4]
        try:
            libraries[library_name]["total"]+=int(total)
        except:
            print "Exception with:"+total+" "+output
        log_action("A file: skipped:"+skipped+" total:"+total)
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
    log_action("Pattern files:"+patternFiles)
    execute_command("cp "+ patternFiles + " "+outputDirectory+"/patternfiles/")

def parseExclusionsFile(outputExcludedFile):
    log_action("Parsing Exclusions File:"+outputExcludedFile)
    with open(outputExcludedFile) as f:
        file_contents = f.read()
        collision_content = file_contents.split('\n\n')
        all_lines = file_contents.split('\n')
        if all_lines[0] != ';--------- (delete these lines to allow sigmake to read this file)':
            log_action("Already sorted "+outputExcludedFile)
            return
        new_exc_contents=""

        for collision in collision_content[1:]:
            first_collision_line = collision.split("\n")[0]
            if "\n" in collision:
                new_exc_contents+= "+collision_"+first_collision_line+"\n"+collision+"\n\n"
            else:
                # One line collision
                new_exc_contents+= ""+collision+"\n\n"

        with open(outputExcludedFile, "w") as text_file:
            text_file.write(new_exc_contents)
        


def run_sigmake(libraryName,allPatternFilesAdded,outputSigName):
    bashCommand = './sigmake -n'+libraryName+' '+allPatternFilesAdded+' '+outputSigName
    log_action(bashCommand)
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
    print "---\n # Generating signature for Library: "+libraryName+" total:"+str(library["total"])
    outputSigName = libraryName+'.sig'
    outputExcludedFile = libraryName+".exc"
    execute_command("rm ./"+outputExcludedFile)


    # 
    # Run sigmake to generate the .sig file
    # 
    allPatternFilesAdded = '+'.join(library['patfiles'])
    run_sigmake(libraryName,allPatternFilesAdded,outputSigName)

    
    parseExclusionsFile(outputExcludedFile)

    # 
    # Run sigmake again to make use of the modified .exc file
    # 
    run_sigmake(libraryName,allPatternFilesAdded,outputSigName)

    if os.path.isfile(outputSigName): 
        moveOutputToGeneratedDirectory(libraryName, outputSigName, ' '.join(library['patfiles']))
        create_zip_file(libraryName)
        print "Successfully Generated",outputSigName,"\n"
    elif os.path.isfile(outputExcludedFile):
        print "ERROR: Please manually edit ",outputExcludedFile

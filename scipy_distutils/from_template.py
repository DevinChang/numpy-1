#!/usr/bin/python

# takes templated file .xxx.src and produces .xxx file  where .xxx is .pyf .f90 or .f
#  using the following template rules

# <...>  is the template All blocks in a source file with names that
#         contain '<..>' will be replicated according to the
#         rules in '<..>'.

# The number of comma-separeted words in '<..>' will determine the number of
#   replicates.
 
# '<..>' may have two different forms, named and short. For example,

#named:
#   <p=d,s,z,c> where anywhere inside a block '<p>' will be replaced with
#  'd', 's', 'z', and 'c' for each replicate of the block.

#  <_c>  is already defined: <_c=s,d,c,z>
#  <_t>  is already defined: <_t=real,double precision,complex,double complex>

#short:
#  <d,s,z,c>, a short form of the named, useful when no <p> appears inside 
#  a block.

#  Note that all <..> forms in a block must have the same number of
#    comma-separated entries. 

__all__ = ['process_str']

import string,os,sys
if sys.version[:3]>='2.3':
    import re
else:
    import pre as re
    False = 0
    True = 1

comment_block_exp = re.compile(r'/\*.*?\*/',re.DOTALL)
# These don't work with Python2.3 : maximum recursion limit exceeded.
#subroutine_exp = re.compile(r'subroutine (?:\s|.)*?end subroutine.*')
#function_exp = re.compile(r'function (?:\s|.)*?end function.*')
#reg = re.compile(r"\ssubroutine\s(.+)\(.*\)")

def parse_structure(astr):
    astr = astr.lower()
    spanlist = []
    # subroutines
    ind = 0
    while 1:
        start = astr.find("subroutine", ind)
        if start == -1:
            break
        fini1 = astr.find("end subroutine",start)
        fini2 = astr.find("\n",fini1)
        spanlist.append((start, fini2))
        ind = fini2

    # functions
    ind = 0
    while 1:
        start = astr.find("function", ind)
        if start == -1:
            break
        pre = astr.rfind("\n", ind, start)
        presave = start
        # look for "$" in previous lines
        while '$' in astr[pre:presave]:
            presave = pre
            pre = astr.rfind("\n", ind, pre-1)
            
        fini1 = astr.find("end function",start)
        fini2 = astr.find("\n",fini1)
        spanlist.append((pre+1, fini2))
        ind = fini2

    spanlist.sort()
    return spanlist

# return n copies of substr with template replacement
_special_names = {'_c':'s,d,c,z',
                  '_t':'real,double precision,complex,double complex'
                  }
template_re = re.compile(r"<([\w]*)>")
named_re = re.compile(r"<([\w]*)=([, \w]*)>")
list_re = re.compile(r"<([\w ]+(,\s*[\w]+)+)>")

def conv(astr):
    b = astr.split(',')
    return ','.join([x.strip() for x in b])

def unique_key(adict):
    # this obtains a unique key given a dictionary
    # currently it works by appending together n of the letters of the
    #   current keys and increasing n until a unique key is found
    # -- not particularly quick
    allkeys = adict.keys()
    done = False
    n = 1
    while not done:
        newkey = "".join([x[:n] for x in allkeys])
        if newkey in allkeys:
            n += 1
        else:
            done = True
    return newkey

def listrepl(match):
    global _names
    thelist = conv(match.group(1))
    name = None
    for key in _names.keys():    # see if list is already in dictionary
        if _names[key] == thelist:
            name = key
    if name is None:      # this list is not in the dictionary yet
        name = "%s" % unique_key(_names)
        _names[name] = thelist
    return "<%s>" % name

def namerepl(match):
    global _names, _thissub
    name = match.group(1)
    return _names[name][_thissub]

def expand_sub(substr,extra=''):
    global _names, _thissub
    # find all named replacements
    reps = named_re.findall(substr)
    _names = {}
    _names.update(_special_names)
    numsubs = None
    for rep in reps:
        name = rep[0].strip()
        thelist = conv(rep[1])
        _names[name] = thelist

    substr = named_re.sub(r"<\1>",substr)  # get rid of definition templates
    substr = list_re.sub(listrepl, substr) # convert all lists to named templates
                                           #  newnames are constructed as needed

    # make lists out of string entries in name dictionary
    for name in _names.keys():
        entry = _names[name]
        entrylist = entry.split(',')
        _names[name] = entrylist
        num = len(entrylist)
        if numsubs is None:
            numsubs = num
        elif (numsubs != num):
            raise ValueError, "Mismatch in number to replace"

    # now replace all keys for each of the lists
    mystr = ''
    for k in range(numsubs):
        _thissub = k
        mystr += template_re.sub(namerepl, substr)
        mystr += "\n\n" + extra
    return mystr

_head = \
"""C  This file was autogenerated from a template  DO NOT EDIT!!!!
C     Changes should be made to the original source (.src) file
C

"""

def get_line_header(str,beg):
    extra = []
    ind = beg-1
    char = str[ind]
    while (ind > 0) and (char != '\n'):
        extra.insert(0,char)
        ind = ind - 1
        char = str[ind]
    return ''.join(extra)
    
def process_str(allstr):
    newstr = allstr
    writestr = _head

    struct = parse_structure(newstr)
    #  return a (sorted) list of tuples for each function or subroutine
    #  each tuple is the start and end of a subroutine or function to be expanded
    
    oldend = 0
    for sub in struct:
        writestr += newstr[oldend:sub[0]]
        expanded = expand_sub(newstr[sub[0]:sub[1]],get_line_header(newstr,sub[0]))
        writestr += expanded
        oldend =  sub[1]


    writestr += newstr[oldend:]
    return writestr


if __name__ == "__main__":

    try:
        file = sys.argv[1]
    except IndexError:
        fid = sys.stdin
        outfile = sys.stdout
    else:
        fid = open(file,'r')
        (base, ext) = os.path.splitext(file)
        newname = base
        outfile = open(newname,'w')

    allstr = fid.read()
    writestr = process_str(allstr)
    outfile.write(writestr)


import imp
import os
from os.path import join
from glob import glob
from scipy.distutils.misc_util import Configuration,dot_join
from distutils.dep_util import newer,newer_group

from scipy.distutils.command.build import build


def configuration(parent_package='',top_path=None):
    config = Configuration('base',parent_package,top_path)
    local_dir = config.local_path
    codegen_dir = join(local_dir,'code_generators')

    generate_umath_py = join(codegen_dir,'generate_umath.py')
    n = dot_join(config.name,'generate_umath')
    generate_umath = imp.load_module('_'.join(n.split('.')),
                                     open(generate_umath_py,'U'),generate_umath_py,
                                     ('.py','U',1))

    header_dir = join(*(config.name.split('.')+['include','scipy']))

    def generate_config_h(ext, build_dir):
        target = join(build_dir,'config.h')
        if newer(__file__,target):
            config_cmd = config.get_config_cmd()
            print 'Generating',target
            #
            tc = generate_testcode(target)
            from distutils import sysconfig
            python_include = sysconfig.get_python_inc()
            result = config_cmd.try_run(tc,include_dirs=[python_include])
            if not result:
                raise "ERROR: Failed to test configuration"            
            moredefs = []

            #
            mathlibs = []
            tc = testcode_mathlib()
            mathlibs_choices = [[],['m'],['cpml']]
            mathlib = os.environ.get('MATHLIB')
            if mathlib:
                mathlibs_choices.insert(0,mathlib.split(','))
            for libs in mathlibs_choices:
                if config_cmd.try_run(tc,libraries=libs):
                    mathlibs = libs
                    break
            else:
                raise "math library missing; rerun setup.py after setting the MATHLIB env variable"
            ext.libraries.extend(mathlibs)
            moredefs.append(('MATHLIB',','.join(mathlibs)))

            libs = mathlibs
            kws_args = {'libraries':libs,'decl':0,'headers':['math.h']}
            if config_cmd.check_func('expl', **kws_args):
                moredefs.append('HAVE_LONGDOUBLE_FUNCS')
            if config_cmd.check_func('expf', **kws_args):
                moredefs.append('HAVE_FLOAT_FUNCS')
            if config_cmd.check_func('asinh', **kws_args):
                moredefs.append('HAVE_INVERSE_HYPERBOLIC')
            if config_cmd.check_func('atanhf', **kws_args):
                moredefs.append('HAVE_INVERSE_HYPERBOLIC_FLOAT')
            if config_cmd.check_func('atanhl', **kws_args):
                moredefs.append('HAVE_INVERSE_HYPERBOLIC_LONGDOUBLE')                
            if config_cmd.check_func('isnan', **kws_args):
                moredefs.append('HAVE_ISNAN')
            if config_cmd.check_func('isinf', **kws_args):
                moredefs.append('HAVE_ISINF')

            if moredefs:
                target_f = open(target,'a')
                for d in moredefs:
                    if isinstance(d,str):
                        target_f.write('#define %s\n' % (d))
                    else:
                        target_f.write('#define %s %s\n' % (d[0],d[1]))
                target_f.close()
        else:
            mathlibs = []
            target_f = open(target)
            for line in target_f.readlines():
                s = '#define MATHLIB'
                if line.startswith(s):
                    value = line[len(s):].strip()
                    if value:
                        mathlibs.extend(value.split(','))
            target_f.close()

        ext.libraries.extend(mathlibs)

        incl_dir = os.path.dirname(target)
        if incl_dir not in config.scipy_include_dirs:
            config.scipy_include_dirs.append(incl_dir)

        config.add_data_files((header_dir,target))
        return target

    def generate_array_api(ext,build_dir):
        target = join(build_dir,'__multiarray_api.h')
        script = join(codegen_dir,'generate_array_api.py')
        if newer(script,target):
            old_sys_path = sys.path
            try:
                sys.path.insert(0, codegen_dir)
                print sys.path
                import generate_array_api
                print 'executing',script
                generate_array_api.generate_api(build_dir)
            finally:
                sys.path = old_sys_path
        config.add_data_files((header_dir,target))
        return target

    def generate_ufunc_api(ext,build_dir):
        target = join(build_dir,'__ufunc_api.h')
        script = join(codegen_dir,'generate_ufunc_api.py')
        if newer(script,target):
            old_sys_path = sys.path
            try:
                sys.path.insert(0, codegen_dir)
                import generate_ufunc_api
                print 'executing',script
                generate_ufunc_api.generate_api(build_dir)
            finally:
                sys.path = old_sys_path
        config.add_data_files((header_dir,target))
        return target

    def generate_umath_c(ext,build_dir):
        target = join(build_dir,'__umath_generated.c')
        script = generate_umath_py
        if newer(script,target):
            f = open(target,'w')
            f.write(generate_umath.make_code(generate_umath.defdict,
                                             generate_umath.__file__))
            f.close()
        return []

    config.add_data_files(join('include','scipy','*.h'))
    config.add_include_dirs('src')

    config.scipy_include_dirs.extend(config.paths('include'))

    deps = [join('src','arrayobject.c'),
            join('src','arraymethods.c'),
            join('src','scalartypes.inc.src'),
            join('src','arraytypes.inc.src'),
            join('include','scipy','*object.h')
            ]

    config.add_extension('multiarray',
                         sources = [join('src','multiarraymodule.c'),
                                    generate_config_h,
                                    generate_array_api,
                                    join('src','scalartypes.inc.src'),
                                    join('src','arraytypes.inc.src'),
                                    join(codegen_dir,'generate_array_api.py'),
                                    join('*.py')
                                    ],
                         depends = deps,
                         )

    config.add_extension('umath',
                         sources = [generate_config_h,
                                    join('src','umathmodule.c.src'),
                                    generate_umath_c,
                                    generate_ufunc_api,
                                    join('src','scalartypes.inc.src'),
                                    join('src','arraytypes.inc.src'),
                                    ],
                         depends = [join('src','ufuncobject.c'),
                                    generate_umath_py,
                                    join(codegen_dir,'generate_ufunc_api.py')
                                    ]+deps,
                         )

    config.add_extension('_compiled_base',
                         sources=[join('src','_compiled_base.c'),
                                  generate_config_h,
                                  generate_array_api,
                                  ],
                         )

    config.add_data_dir('tests')
    config.make_svn_version_py()

    return config

def testcode_mathlib():
    return """\
/* check whether libm is broken */
#include <math.h>
int main(int argc, char *argv[])
{
  return exp(-720.) > 1.0;  /* typically an IEEE denormal */
}
"""

import sys
def generate_testcode(target):
    if sys.platform == 'win32':
        target = target.replace('\\','\\\\')
    testcode = [r'''
#include <Python.h>
#include <limits.h>
#include <stdio.h>

int main(int argc, char **argv)
{

        FILE *fp;

        fp = fopen("'''+target+'''","w");
        ''']

    c_size_test = r'''
#ifndef %(sz)s
          fprintf(fp,"#define %(sz)s %%d\n", sizeof(%(type)s));
#else
          fprintf(fp,"/* #define %(sz)s %%d */\n", %(sz)s);
#endif
'''
    for sz, t in [('SIZEOF_SHORT', 'short'),
                  ('SIZEOF_INT', 'int'),
                  ('SIZEOF_LONG', 'long'),
                  ('SIZEOF_FLOAT', 'float'),
                  ('SIZEOF_DOUBLE', 'double'),
                  ('SIZEOF_LONG_DOUBLE', 'long double'),
                  ('SIZEOF_PY_INTPTR_T', 'Py_intptr_t'),
                  ]:
        testcode.append(c_size_test % {'sz' : sz, 'type' : t})

    testcode.append('#ifdef PY_LONG_LONG')
    testcode.append(c_size_test % {'sz' : 'SIZEOF_LONG_LONG',
                                   'type' : 'PY_LONG_LONG'})
    testcode.append(c_size_test % {'sz' : 'SIZEOF_PY_LONG_LONG',
                                   'type' : 'PY_LONG_LONG'})
    

    testcode.append(r'''
#else
        fprintf(fp, "/* PY_LONG_LONG not defined */\n");
#endif
#ifndef CHAR_BIT
          {
             unsigned char var = 2;
             int i=0;
             while (var >= 2) {
                     var = var << 1;
                     i++;
             }
             fprintf(fp,"#define CHAR_BIT %d\n", i+1);
          }
#else
          fprintf(fp, "/* #define CHAR_BIT %d */\n", CHAR_BIT);
#endif
          fclose(fp);
          return 0;
}
''')
    testcode = '\n'.join(testcode)    
    return testcode

if __name__=='__main__':
    from scipy.distutils.core import setup
    setup(**configuration(top_path='').todict())

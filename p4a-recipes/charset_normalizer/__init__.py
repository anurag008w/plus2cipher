from pythonforandroid.recipe import PythonRecipe

class CharsetNormalizerRecipe(PythonRecipe):
    version = '3.5.1'
    url = 'https://pypi.org/packages/source/c/charset-normalizer/charset_normalizer-{version}.tar.gz'
    depends = ['setuptools']
    
    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        # Force pure python build by disabling mypyc compilation
        env['CHARSET_NORMALIZER_USE_MYPYC'] = '0'
        return env

recipe = CharsetNormalizerRecipe()

from pathlib import Path
import importlib
import traceback

# modify this if additional languages must be present
required_translations = ['en', 'hu']


class TranslationMissingError(Exception):

    def __init__(self, file_name: str, dictionary_name: str, missing_languages):
        self.file_name = file_name
        self.dictionary_name = dictionary_name
        self.missing_languages = missing_languages

    def __str__(self) -> str:
        return f'In file "{self.file_name}": Dictionary "{self.dictionary_name}" has missing languages {str(self.missing_languages)}'


def convert_to_import_name(file_name: str) -> str:
    import_name = file_name.removesuffix('.py')
    return import_name.replace('/', '.').replace('\\', '.')


def check_translations_for_python_file(file_name: str):
    import_name = convert_to_import_name(file_name)
    print(f'Using the import name {import_name} to import this python file...')
    python_module = importlib.import_module(import_name)

    for variable_name in dir(python_module):
        if variable_name.startswith('_'):
            continue
        check_variable(file_name, variable_name, python_module)


def check_variable(file_name: str, variable_name: str, module):
    variable = getattr(module, variable_name)
    if type(variable) is dict:
        # a dictionary has been found in one of the checked files
        keys: list = variable.keys()
        if any(key in required_translations for key in keys):
            # if at least one translation key was found, then all of them must be found!
            missing_translations = collect_missing_languages(keys)
            if len(missing_translations) > 0:
                raise TranslationMissingError(
                    file_name=file_name,
                    dictionary_name=variable_name,
                    missing_languages=missing_translations
                )
        else:
            print(f'The file {file_name} contains a dictionary {variable_name} which is not related to translations, ignoring')


def collect_missing_languages(keys: list) -> list:
    missing_translations = []
    for required_translation in required_translations:
        if required_translation not in keys:
            missing_translations.append(required_translation)
    return missing_translations


# Actual check starts here -----------------------------------------------------------------------------------------
# TODO: extend the check to the command definition JSON files

translations_check_directory = 'bot'
print(f'Starting translations check on the source files in {translations_check_directory} directory...')
print(f'Required languages are: {str(required_translations)}')
translation_errors = []

for python_file_path in Path('bot').rglob('*.py'):
    try:
        python_file_name = str(python_file_path)

        # these do not need to be checked
        if python_file_name.endswith('templates.py') or python_file_name.endswith('template_utils.py') or python_file_name.endswith('time_utils.py'):
            print(f'Checking the python file {python_file_name}')
            check_translations_for_python_file(python_file_name)
        else:
            print(f'Ignoring the check of {python_file_name} because it is not a template file')
    except TranslationMissingError as e:
        translation_errors.append(e)
    except Exception:
        print('Failed to run translations check due to unexpected error!')
        traceback.print_exc()

if len(translation_errors) > 0:
    print('Translation errors found!')
    for translation_error in translation_errors:
        print(str(translation_error))
    exit(1)
else:
    print('No translation errors were found!')

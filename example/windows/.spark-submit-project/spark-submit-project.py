import logging
import sys
import os
import zipfile
import shutil
import subprocess
import configparser


PRIVATE_FOLDER_PATH = '.spark-submit-project'
CONFIGURATION_FILENAME = os.path.join(PRIVATE_FOLDER_PATH, 'ssp.conf')


class _PathConfigurationKeys:
    """
    Holds the key names for file paths section of the config file.
    """

    def __init__(self):
        pass

    SECTION_NAME = 'PATHS'

    LIBRARIES_DIR = 'Libraries Directory'
    DISTRIBUTION_DIR = 'Distribution Directory'
    SOURCE_CODE_DIR = 'Source Code Directory'
    REQUIREMENTS_FILE = 'Requirements File'
    INCLUDE_CODE_DIR = 'Include Code Directory'
    INCLUDE_ASSETS_DIR = 'Include Assets Directory'
    INCLUDE_CODE_FILE = 'Include Code File'
    INCLUDE_ASSETS_FILE = 'Include Assets File'

    def get_keys_list(self) -> [str]:
        """
        Returns all the key names in a list.

        :return: Type[str]
        """
        return [self.LIBRARIES_DIR, self.DISTRIBUTION_DIR, self.SOURCE_CODE_DIR, self.REQUIREMENTS_FILE,
                self.INCLUDE_CODE_FILE, self.INCLUDE_CODE_DIR, self.INCLUDE_ASSETS_FILE, self.INCLUDE_ASSETS_DIR]


class _OptionsConfigurationKeys:
    """
    Holds key names for the [OPTIONS] section of config file.
    """

    def __init__(self):
        pass

    SECTION_NAME = 'OPTIONS'

    USE_ARCHIVE_ARG = 'Use Archive Argument'

    def get_keys_list(self) -> [str]:
        """
        Returns all the key names in a list.

        :return: Type[str]
        """
        return [self.USE_ARCHIVE_ARG]


class _Paths:
    """
    Represents all the paths used in this script.

    Uses _PathConfigurationKeys class to read the config file.
    """

    def __init__(self, config_filename):
        """
        Reads the `config_filename` file using the _PathConfigurationKeys and stores them in an instance of itself.

        :param config_filename: complete filename of the config file.
        """

        keys = _PathConfigurationKeys()

        conf = configparser.ConfigParser()
        conf.read(config_filename)

        try:
            conf = conf[keys.SECTION_NAME]

            self.libraries_dir = conf[keys.LIBRARIES_DIR]
            self.distribution_dir = conf[keys.DISTRIBUTION_DIR]
            self.source_code_dir = conf[keys.SOURCE_CODE_DIR]
            self.requirements_file = conf[keys.REQUIREMENTS_FILE]
            self.include_code_dir = conf[keys.INCLUDE_CODE_DIR]
            self.include_code_file = conf[keys.INCLUDE_CODE_FILE]
            self.include_assets_dir = conf[keys.INCLUDE_ASSETS_DIR]
            self.include_assets_file = conf[keys.INCLUDE_ASSETS_FILE]

        except KeyError:

            keys_list_str = '\n'.join(keys.get_keys_list())

            logging.error(
                f"\n  Configuration for one or more paths was missing.\n  Ensure that '{CONFIGURATION_FILENAME}' "
                f"has all the required paths in the [{keys.SECTION_NAME}] section.\n  "
                f"\n  The list of required keys is:\n  [{keys.SECTION_NAME}]\n  {keys_list_str}\n  "
            )
            exit(1)


class _Options:
    """
    Represents all the options used in this script.

    Uses _OptionsConfigurationKeys class to read the config file.
    """

    def __init__(self, config_filename):
        """
        Reads the `config_filename` file using the _OptionsConfigurationKeys and stores them in an instance of itself.

        :param config_filename: complete filename of the config file.
        """

        keys = _OptionsConfigurationKeys()

        conf = configparser.ConfigParser()
        conf.read(config_filename)

        try:
            conf = conf[keys.SECTION_NAME]

            self.use_archive_arg = conf.getboolean(keys.USE_ARCHIVE_ARG)

        except KeyError:

            keys_list_str = '\n'.join(keys.get_keys_list())

            logging.error(
                f"\n  Configuration for one or more paths was missing.\n  Ensure that '{CONFIGURATION_FILENAME}' "
                f"has all the required paths in the [{keys.SECTION_NAME}] section.\n  "
                f"\n  The list of required keys is:\n  [{keys.SECTION_NAME}]\n  {keys_list_str}\n  "
            )
            exit(1)
        except ValueError or TypeError:
            logging.error(f"Unable to read [{LOGGING_CONFIG_SECTION_NAME}] "
                          f"Section's '{keys.USE_ARCHIVE_ARG}' key as an boolean."
                          f"Make sure that the value of '{keys.USE_ARCHIVE_ARG}' is either 'True' or 'False'")
            exit(1)


class Requirements:
    """
    This class holds the responsibility of loading external packages, archiving source code and processing include files
    and directories.
    """

    # postfixes are appended to the end of directory names to avoid conflicts.
    ASSETS_POSTFIX = '_assets'
    CODE_POSTFIX = '_code'
    SOURCE_POSTFIX = '_src'

    @staticmethod
    def _load_requirements_packages(paths: _Paths):
        """
        Loads/Downloads the requirements in the requirements file in the libraries directory.

        Uses the `pip wheel -r <file> -w <dir>` command.

        :param paths: An instance of _Paths, being used by the script.
        :return: None.
        """
        if os.path.isfile(paths.requirements_file):

            logging.info("Loading External Packages...")

            command_args = ['pip', 'wheel', '-r', f"{paths.requirements_file}", '-w', f"{paths.libraries_dir}"]

            logging.debug(f"Running Command: {subprocess.list2cmdline(command_args)}")

            subprocess.run(args=command_args)
        else:
            logging.warning(f"Requirement file '{paths.requirements_file}' not found. " 
                            "Not loading any external packages.")

    @staticmethod
    def _create_source_distribution(paths: _Paths):
        """
        Archives the directories in source code directory and places it in the distribution directory.

        Files are not moved to the distribution directory, they are taken directly from the source code directory.

        :param paths: An instance of _Paths, being used by the script.
        :return: None
        """

        path = Requirements._generate_dist_path(paths.distribution_dir, paths.source_code_dir,
                                                Requirements.SOURCE_POSTFIX)

        if os.path.isdir(paths.source_code_dir):
            logging.info("Gathering source code...")
            os.makedirs(path)
            Requirements._create_archives_of_directories_in(paths.source_code_dir, path)
        else:
            logging.warning(f"Source code directory '{paths.source_code_dir}' does not exist.")

    @staticmethod
    def _create_archives_of_directories_in(source_dir, destination_dir):
        """
        Creates zip files of all the top level directories of `source_dir` and places them in `destination_dir`.

        :param source_dir: The directory from where the directories to be archived are to be taken.
        :param destination_dir: The directory where the archives should be palced.
        :return: None.
        """
        for (root, directories, files) in os.walk(source_dir):
            for directory in directories:
                shutil.make_archive(f"{os.path.join(destination_dir, directory)}",
                                    'zip', os.path.join(source_dir, directory))
            break
        pass

    @staticmethod
    def _create_include_dir_distributions(paths: _Paths):
        """
        Walks the Include Code Directory and Include Assets Directory, converting the top level directories into
        zip archives and placing them in their respective Distribution Directory's sub directory.

        :param paths:  An instance of _Paths, being used by the script.
        :return: None.
        """
        if os.path.isdir(paths.include_code_dir):
            logging.info("Processing Include Code Directory...")
            path = Requirements._generate_dist_path(paths.distribution_dir, paths.include_code_dir,
                                                    Requirements.CODE_POSTFIX)
            if not os.path.isdir(path):
                os.makedirs(path)
            Requirements._create_archives_of_directories_in(paths.include_code_dir, path)

        if os.path.isdir(paths.include_assets_dir):
            logging.info("Processing Include Assets Directory...")
            path = Requirements._generate_dist_path(paths.distribution_dir, paths.include_assets_dir,
                                                    Requirements.ASSETS_POSTFIX)
            if not os.path.isdir(path):
                os.makedirs(path)
            Requirements._create_archives_of_directories_in(paths.include_assets_dir, path)

    @staticmethod
    def _acquire_dependencies(paths: _Paths):
        """
        A convenience function that combines the functions that write to the disk.

        :param paths:  An instance of _Paths, being used by the script.
        :return: None
        """

        Requirements._load_requirements_packages(paths)
        Requirements._create_source_distribution(paths)
        Requirements._create_include_dir_distributions(paths)

    @staticmethod
    def _get_file_paths_list(directory) -> [str]:
        """
        Utility function to list the complete filenames of the top level files of the directory.

        :param directory: The directory path from which the filenames are to be taken.
        :return: [str]
        """
        file_paths = []
        for (_, _, filenames) in os.walk(directory):
            for file in filenames:
                file_paths.append(os.path.join(directory, file))
            break

        return file_paths

    @staticmethod
    def _extract_lines(filename) -> [str]:
        """
        Splits the file's lines into a list.

        :param filename: file to process.
        :return: Type[str]
        """
        file = open(filename, 'r+')
        lines = [line.strip() for line in file]
        file.close()
        return lines

    @staticmethod
    def _generate_dist_path(dist_dir, original_dir, postfix):
        """
        Generates a path of a sub distribution directory corresponding to the original directory. postfix is used to
        avoid potential conflicts.

        :param dist_dir: Path of top level distribution directory.
        :param original_dir: Path of the directory which needs a sub distribution directory.
        :param postfix: A string appended with the sub directory name to avoid conflicts.
        :return: None.
        """
        name = original_dir.split(os.path.sep)[-1]
        name += postfix
        path = os.path.join(dist_dir, name)
        return path

    @staticmethod
    def _clean_dir(directory):
        """
        Deletes the files and folders in a directory.

        :param directory: Path of the directory.
        :return: None.
        """
        if os.path.isdir(directory):
            shutil.rmtree(directory)
            os.mkdir(directory)

    @staticmethod
    def _collect_dependencies(dist_dir, directory, postfix) -> [str]:
        """
        Collects the directory's sub distribution files and the top level files of the directory itself, and places
        their paths in a list.

        :param dist_dir: Top level distribution directory.
        :param directory: The directory whose dependencies are being collected.
        :param postfix: The posted used when the sub distribution directory for the directory was made.
        :return: Type[str].
        """
        deps = []

        deps.extend(Requirements._get_file_paths_list(directory))
        path = Requirements._generate_dist_path(dist_dir, directory, postfix)
        deps.extend(Requirements._get_file_paths_list(path))

        return deps

    @staticmethod
    def _process_assets(paths: _Paths, options: _Options) -> ([str], [str]):
        """
        Collects the include directory's sub distribution files and the top level files of the directory itself,
        and places their paths in two list, file_assets, archive_assets. It also process the include asset file
        and places assets in file_assets, archive_assets.

        Currently, only zip files are considered archives.

        :param paths: An instance of _Paths, being used by the script.
        :return: Type([str],[str])
        """
        file_assets = []
        archive_assets = []
        temp_file_names = []

        if os.path.isdir(paths.include_assets_dir):
            path = Requirements._generate_dist_path(paths.distribution_dir, paths.include_assets_dir,
                                                    Requirements.ASSETS_POSTFIX)
            files_list = Requirements._get_file_paths_list(path)
            if options.use_archive_arg:
                archive_assets.extend(files_list)
            else:
                file_assets.extend(files_list)

            temp_file_names = Requirements._get_file_paths_list(paths.include_assets_dir)

        elif not paths.include_assets_dir == '':
            logging.warning(f"Include Assets Directory '{paths.include_dir}' does not exist.")

        if os.path.isfile(paths.include_assets_file):
            temp_file_names.extend(Requirements._extract_lines(paths.include_assets_file))

        elif not paths.include_assets_file == '':
            logging.warning(f"Include Assets File '{paths.include_assets_file}' does not exist.")

        if options.use_archive_arg:
            import re

            regex = re.compile(r'^.*\.(zip)$')

            for name in temp_file_names:
                if bool(regex.match(name)):
                    archive_assets.append(name)
                else:
                    file_assets.append(name)
        else:
            file_assets.extend(temp_file_names)

        return file_assets, archive_assets

    @staticmethod
    def get_requirements_list(paths: _Paths, options: _Options) -> ([str], [str], [str]):
        """
        Acquires the dependencies and makes a list of complete filenames of all the dependencies.

        Returns three lists.
        First code_files are the code dependencies.
        Second asset_files are the file assets like txt, jpg etc. all expect .zip.
        Third archive_assets are assets but only zip files.

        :param options: An instance of _Options, being used by the script.
        :param paths: An instance of _Paths, being used by the script.
        :return: Type([str],[str],[str])
        """

        logging.info("Deleting old distribution files...")

        Requirements._clean_dir(paths.distribution_dir)
        Requirements._clean_dir(paths.libraries_dir)

        Requirements._acquire_dependencies(paths)

        logging.info("Gathering requirements...")

        code_files = []
        code_files.extend(Requirements._get_file_paths_list(paths.libraries_dir))

        if os.path.isdir(paths.source_code_dir):
            code_files.extend(Requirements._collect_dependencies(paths.distribution_dir, paths.source_code_dir,
                                                                 Requirements.SOURCE_POSTFIX))
        # Code Includes

        if os.path.isdir(paths.include_code_dir):
            code_files.extend(Requirements._collect_dependencies(paths.distribution_dir, paths.include_code_dir,
                                                                 Requirements.CODE_POSTFIX))
        elif not paths.include_code_dir == '':
            logging.warning(f"Include Code Directory '{paths.include_code_dir}' does not exist.")

        if os.path.isfile(paths.include_code_file):
            lines = Requirements._extract_lines(paths.include_code_file)
            code_files.extend(lines)
        elif not paths.include_code_file == '':
            logging.warning(f"Include Code File '{paths.include_code_file}' does not exist.")

        # Assets Includes

        file_assets, archive_assets = Requirements._process_assets(paths, options)

        return code_files, file_assets, archive_assets


def _init_logger(config_filename):
    """
    Read the logging config from the [LOGGING] section of config file and applies it to the logger.

    :param config_filename: The complete filename of the config file.
    :return: None.
    """
    LOGGING_CONFIG_SECTION_NAME = 'LOGGING'

    conf = configparser.ConfigParser()
    conf.read(config_filename)

    level = 20

    try:
        conf = conf[LOGGING_CONFIG_SECTION_NAME]
    except KeyError:
        logging.error(f"Unable to read [{LOGGING_CONFIG_SECTION_NAME}] "
                      f"Section from '{CONFIGURATION_FILENAME}' config file.")
        exit(1)
    try:
        level = conf.getint('Level')
    except ValueError or TypeError:
        logging.error(f"Unable to read [{LOGGING_CONFIG_SECTION_NAME}] "
                      f"Section's 'Level' key as an Integer."
                      f"Make sure that the value of 'Level' is an integer")
        exit(1)
    log_file = os.path.join(PRIVATE_FOLDER_PATH, 'log.txt')
    logging.basicConfig(format="SSP - %(asctime)s - %(levelname)8s - %(message)s",
                        level=level,
                        datefmt='%H:%M:%S',
                        handlers=[
                            logging.FileHandler(log_file, mode='w'),
                            logging.StreamHandler()
                        ])
    logging.info(f"Logs are being stored in {log_file}")

# Check if config file exists.
if not os.path.isfile(CONFIGURATION_FILENAME):
    logging.error(
        f"'{CONFIGURATION_FILENAME}' file was not found in the current working directory. "
        f"Make sure you run the ssp.sh from the project directory and that the project directory has the "
        f"'{CONFIGURATION_FILENAME}' configuration file."
    )
    exit(1)

# Initialize Logger
_init_logger(CONFIGURATION_FILENAME)

# Load paths for the script to use.
PATHS = _Paths(CONFIGURATION_FILENAME)

# Load options
OPTIONS = _Options(CONFIGURATION_FILENAME)

# Acquire a list of dependencies (filenames).
requirements_list, assets_list, archives_list = Requirements.get_requirements_list(PATHS, OPTIONS)

# Convert it to a comma separated string of filenames.
requirements_list_str = ','.join(requirements_list)
assets_list_str = ','.join(assets_list)
archives_list_str = ','.join(archives_list)

# Args passed to this script
args = sys.argv
old_py_files_args = ''
old_files_args = ''
old_archive_args = ''

# If a '--py-files' arg was passed, merge it with the requirements_list_str.
if '--py-files' in args:
    idx = args.index('--py-files')
    if len(args) > idx + 1:
        old_py_files_args = args[idx + 1]
        del args[idx + 1]
    del args[idx]
    requirements_list_str = old_py_files_args + ',' + requirements_list_str

if '--files' in args:
    idx = args.index('--files')
    if len(args) > idx + 1:
        old_files_args = args[idx + 1]
        del args[idx + 1]
    del args[idx]
    assets_list_str = old_files_args + ',' + assets_list_str

if '--archives' in args:
    idx = args.index('--archives')
    if len(args) > idx + 1:
        old_archive_args = args[idx + 1]
        del args[idx + 1]
    del args[idx]
    archives_list_str = old_archive_args + ',' + archives_list_str

# The arg[0] is this file's name. Changing it to spark-submit.
args[0] = 'spark-submit'

# Insert the list filenames of dependencies as the --py-files arg.
if requirements_list_str != '':
    args.insert(1, requirements_list_str)
    args.insert(1, '--py-files')

if assets_list_str != '':
    args.insert(1, assets_list_str)
    args.insert(1, '--files')

if archives_list_str != '':
    args.insert(1, archives_list_str)
    args.insert(1, '--archives')

logging.debug(f"Running the following command:\n\n  {subprocess.list2cmdline(args)}\n")

spark_submit_proc = subprocess.run(args=args, shell=True)

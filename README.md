# Spark-Submit-Project
spark-submit-project (SSP) is a script file that calls `spark-submit` but takes aways the hassle of manually adding files to `--py-files`, `--files`, and `--archives` arguments. 

There are many alternatives out there but for small scale development, those can be annoying to set up. SSP, though a bit unprofessional, is quick and gets you started right away.
 
**Contents**
 - [Spark-Submit-Project](#spark-submit-project)
 - [Install](#install)
 - [Usage](#usage)
 - [Including Files and Folders](#including-files-and-folders)
 - [Configuration](#configuration)
	 - [Python](#python)
	 -  [Configuration File](#configuration-file)
		 - [PATHS](#paths)
		 - [LOGGING](#logging)
		 - [OPTIONS](#options)

# Install

1. Create a folder. This is your project folder.
2. Copy the contents of [`dist/linux/`](./dist/linux/) or [`dist/windows/`](./dist/windows/) to your project folder, according to your OS.

> Requires python>=3.6 and pip
> If you do not wish to change your environment's python version, look at the [configuration section](#configuration) to learn how to define what python SSP uses.

# Usage
In a console/terminal with the present working directory as your project folder, use the following commands:
*Linux*
```bash
$ ./ssp.sh <args>
```
*Windows*
```cmd
> .\ssp.bat <args>
```

**\<args\>** are the same args you would pass to `spark-submit`. You can even pass your own `--py-files`, `--files`, and `--archives` arguments. 

See the [examples](example/).

# Including Files and Folders
SSP needs to know what you want to submit with `spark-submit` and what not to. For this, there are several directories and files it uses.

*Default values assume your project folder as the working directory.*
*To change defaults, look at the [configuration section](#configuration).*
| Item                     | Description                                                                                                                                                  | Default                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| Requirements File        | Contains package names. One per line. See [this link](https://pip.readthedocs.io/en/1.1/requirements.html#the-requirements-file-format) for details.         | requirements.txt           |
| Libraries Directory      | <sup>[1]</sup>A private directory used by SSP script to store downloaded files described in Requirements File.                                               | .spark-submit-project/lib  |
| Source Code Directory    | <sup>[2]</sup>The directory where your code files reside. It is not necessary to have this directory.                                                        | src                        |
| Distribution Directory   | <sup>[1]</sup> A private directory used by SSP to store archived files created during submission.                                                            | .spark-submit-project/dist |
| Include Code File        | <sup>[3]</sup>A file where each line is a file path of a code related file e.g. a py file, a package zip, egg or whl. These are submitted as --py-files arg. | None                       |
| Include Code Directory   | <sup>[2]</sup>A directory whose files and directories are submitted as --py-files arg.                                                                       | None                       |
| Include Assets File      | <sup>[3][4]</sup>A file where each line is a file path of a non-code related file.                                                                           | None                       |
| Include Assets Directory | <sup>[2][4]</sup>A directory containing none code files and directories .                                                                                    | None                       |

> Paths are relative to the present working directory of the shell where the script is run. 

[1] This directory should only be used by SSP. Do not copy your files into it.
[2] The top-level files are included directly. Whereas top-level directories are archived (zip) and then included in the list of files to send with `spark-submit`.
[3]  Paths must not be directories,
[4] zip files are sent as the --archives arg, while other files are sent as --files arg. You can send all files as --files by changing the [configuration file](#configuration).

NOTE: Files from all these locations and directories (as zip archives) will be placed on the working directory of the executors after spark-submit. This means you can import/access files without manually adding the directories to the path.

> ATTENTION: Python package dependencies that required c/c++ compilation are likely to fail when shared through this method. Though I only did testing on a standalone mode spark cluster. See [this link](https://stackoverflow.com/questions/36461054/i-cant-seem-to-get-py-files-on-spark-to-work) to learn more.

# Configuration
## Python
If you do not want to install python>=3.6 in your working environment, you can set an environment variable `SSP_PYTHON` with the path of the python to use.
Alternatively, you can edit the bash/batch script.

## Configuration File
`.spark-submit-project/ssp.conf` is the configuration file used by the script.
There are three sections in the file:

### PATHS
Here you will set up the paths of the [directories and files](#including-files-and-folders) mentioned above.

### LOGGING
Here you define the level of logging. Logs are stored in `.spark-submit-project/log.txt`.
The 'Level' is an integer. See [this link](https://docs.python.org/3/library/logging.html#logging-levels) for more details.

### OPTIONS
Here you set whether you want to use the `--archives` option.
If you prefer to not use this option, then assets' zip files will be sent as `--files` args.
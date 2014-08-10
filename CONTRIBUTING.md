# Micro Bog Magic - Development Guideline

## Table of contents

- [Level of done](#level-of-done)
- [Project structure](#project-structure)
    - [completion](#completion)
    - [man](#man)
    - [mbm](#mbm)
    - [lib](#lib)
    - [provider](#provider)
    - [puppet](#puppet)
    - [token\_procurer](#token_procurer)
- [Implementing a new Provider](#implementing-a-new-provider)

## Level of done

- Every pull request should refer to one feature/bug and should have a
  meaningful name with the prefix `feature` or `bug`
- All test must run without errors
- Test coverage must not be below 100%
- `pep8` must finish without output
- Documentation (including the manpage) should be adjusted/enhanced whenever
  needed
- Your code must not depend on any third party library (standard library only!)
- If you made any changes to the sandbox development environment make sure it
  bootstraps properly on a fresh cloned project
- The zen of python (`echo 'import this' | python3`) should apply to all your
  contributed code

## Project structure

### completion

Contains the bash completion. It would be nice if you help to enhance the
completion for a better user experience.

### man

Contains the manpage. Thanks for contributing here as well.

### mbm

The actual python code.

#### lib

Generic library code used in the provider modules. These modules inside the
`lib` directory should not depend on other modules outside the lib directory.

#### provider

Every module in this folder contains all the code which is specific for a
certain micro blog website. Code which is specific for a certain website must
not exist outside this very module. Generally these modules need to implement
the abstract base classes specified in the `datatype.py` module. Implement a
provider module as close a possible to the existing providers.

### puppet

[Puppet](http://puppetlabs.com/puppet/what-is-puppet) code for provisioning
the development sandbox.

### token\_procurer

Contains a php module which has to run on a web server in order to get OAuth
access tokens. If you are in the mood for PHP development feel free to turn
this into a separate project and make it a general purpose OAuth token procurer
for various web sites.

## Implementing a new provider

TODO

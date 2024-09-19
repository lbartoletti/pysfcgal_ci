# How to release

- edit the CHANGELOG.md. The best way is to start with commitizen for that:
```bash
cz changelog --incremental --unreleased-version v2.0.0
```
and then edit it to make it more user readable. Especially, the `BREAKING
CHANGE` needs to be reviewed carefully and often to be rewritten, including
migration guide for instance.
- edit the version in setup.py
- create a merge request with these changes
- once it is merged, create a tagged release on gitlab.
- switch to the newly created tag
- publish on pypi:
```bash
# create a package in dist/ folder
python -m build
# check everything is ok (replace <version> by the version you've just built)
twine check dist/pysfcgal-<version>*
# check your pypirc for authentication
# upload it to pypi, eventually using --repository for selecting the right authent
twine upload dist/pysfcgal-<version>*
```

What to check after the release:

- the gitlab registry container
- [TODO] the docker hub page
- the pypi page
- [TODO] the new tag in the online documentation

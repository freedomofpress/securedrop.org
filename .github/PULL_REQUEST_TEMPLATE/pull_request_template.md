## Description

<!-- If this is a deploy PR, please append `?template=deploy.md` to the current URL -->

Fixes #.

Changes proposed in this pull request:

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Vulnerabilities update
- [ ] Config changes
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires an admin update after deploy
- [ ] Includes a database migration removing  or renaming a field


## Testing

How should the reviewer test this PR?
Write out any special testing steps here.

### Post-deployment actions

In case this PR needs any admin changes or run a management command after deployment, mention it here:

## Checklist

### General checks

- [ ] Linting and tests pass locally
- [ ] The website and the changes are functional in Tor Browser
- [ ] There is no conflicting migrations
- [ ] Any CSP related changes required has been updated (check at least both firefox & chrome)
- [ ] The changes are accessible using keyboard and screenreader

### If you made changes to directory listing:

- [ ] Verify directory filters (country/topic/language) work as expected
- [ ] Verify directory search works as expected

### If you made changes to contact form

- [ ] Verify contact form submissions works as expected
- [ ] Verify if any CSP changes required (test at least both firefox & chrome)

### If you made changes to scanner

- [ ] Verify that the directory scan result page in admin interface loads as expected
- [ ] Verify that the API at `/api/v1/directory` returns directory entries and scan results as expected

### If it's a major change

- [ ] Do the changes need to be tested in a separate staging instance?

### If you made any frontend change

If the PR involves some visual changes in the frontend, it is recommended to add a screenshot of the new visual.

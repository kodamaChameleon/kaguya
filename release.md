# Versioning and Release
This document describes the versioning and release process of Kaguya. This document is a living document, contents will be updated according to each release.

## Releases
Kaguya releases will be versioned using dotted triples, similar to [Semantic Version](http://semver.org/). For this specific document, we will refer to the respective components of this triple as `<major>.<minor>.<patch>`. The version number may have additional information, such as "-alpha.1", "-beta.2" to mark alpha and beta versions for earlier access. Such releases will be considered as "pre-releases".

### Major and Minor Releases
Major and minor releases of Kaguya will be tagged in `main` when the release reaches the necessary state. The tag format should follow `<major>.<minor>.0`. For example, once the release `1.0.0` is no longer pre-release, a tag will be created with the format `1.0.0` and the new version will be released. The Docker images will be updated shortly after. 

### Patch releases
Patch releases are based on the major/minor release tag. The release speed is one week to solve critical community and security issues; the cadency for other issues is on-demand driven based on the severity of the issue to be fixed.

### Pre-releases
The different alpha and beta builds will be compiled from their corresponding tags. Please note they are done to assist in the stabilization process. If it breaks you get to keep both parts.

### Minor Release Support Matrix
| Version                          | Supported          |
|----------------------------------|--------------------|
| Kaguya v1.1.x                    | :white_check_mark: |

### Upgrade path and support policy
Being as Kaguya is still very much in it's infancy, there is no current upgrade and support policy available.

### Next Release
The activity for next release isn't currently tracked. 

### Credits

This release document is based on [Harbor](https://github.com/goharbor/harbor/blob/master/RELEASES.md)'s release document.

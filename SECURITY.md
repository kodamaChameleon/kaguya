# Security Policy

Kaguya is a command line based application for automating common Risk Management Framework (RMF) controls and NIST 800-53 implementations. As such, the developer has adopted this security disclosure and response policy to ensure that critical issues are responsibly handled.

## Supported Versions
Only the latest Kaguya release is maintained. Applicable fixes, including security fixes, will not backported to older release branches. Please refer to [releases.md](https://github.com/kodamaChameleon/kaguya/blob/main/release.md) for details.

## Reporting a Vulnerability - Private Disclosure Process
Security is of the highest importance and all security vulnerabilities or suspected security vulnerabilities should be reported to Kaguya privately, to minimize attacks against current users of Kaguya before they are fixed. Vulnerabilities will be investigated and patched on the next patch (or minor) release as soon as possible. This information could be kept entirely internal to the project.  

We do not currently have a reporting system in place to submit vulnerabilities to in a secure manner. Should Kaguya find a larger customer base, measures will be taken to ensure the protection of our customers by providing appropriate reporting procedures.

**IMPORTANT: Do not file public issues on GitHub for security vulnerabilities**
 
## Confidentiality, integrity and availability
We consider vulnerabilities leading to the compromise of data confidentiality, elevation of privilege, or integrity to be our highest priority concerns. Availability, in particular in areas relating to DoS and resource exhaustion, is also a serious security concern. The Kaguya developer takes all vulnerabilities, potential vulnerabilities, and suspected vulnerabilities seriously and will investigate them in an urgent and expeditious manner.

Note that we do not currently consider the default settings for Kaguya to be secure-by-default. It is necessary for operators to explicitly configure settings, role based access control, and other resource related features in Kaguya to provide a hardened Kaguya environment. We will not act on any security disclosure that relates to a lack of safe defaults. Over time, we will work towards improved safe-by-default configuration, taking into account backwards compatibility.

## Credits

This security policy is based on [Harbor](https://github.com/goharbor/harbor)'s security policy.

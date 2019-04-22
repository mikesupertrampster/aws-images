AWS AMI
===========

<a href="https://codeclimate.com/github/mikesupertrampster/aws-images/maintainability"><img src="https://api.codeclimate.com/v1/badges/ca3843d3e263f950f008/maintainability" /></a>
[![GitLabCI](https://gitlab.com/mikesupertrampsters/aws-images/badges/master/pipeline.svg
)](https://gitlab.com/mikesupertrampsters/aws-images)

Builds the following AMIs:
 * Base (hardened)
 * Bastion
 * Vault (v1.1.1)

### Usage

```bash
export VERSION_NO=1.0.0
export role=vault
packer build packer/${role}.json
```
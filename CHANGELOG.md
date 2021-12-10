# Change Log
All notable changes to this project will be documented in this file.

## [1.0.0] - 2020-07-21
### Added
* initial repository version

## [1.0.1] - 2021-12-09
### Added
* Rearc's contribution to aws-data-exchange-publisher-coordinator
* Allows to set a specific assets per revision
* The following service limits have been addressed in this solution:
    * 100 assets per import job and a maximum of 10 concurrent import jobs
    * Supports folder prefixes. E.g. if you want to include an S3 folder called data, specify key as "data/" and the solution will include all files within that folder's hierarchy.
    * automatic revisions in ADX
    * Set comments for specific ADX revisions from manifest file
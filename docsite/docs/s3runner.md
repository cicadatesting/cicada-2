---
id: s3-runner
title: S3 Runner
sidebar_label: S3 Runner
---

The S3 Runner is used to upload and download files from S3 and manage buckets
for future tests.

## Config

<pre><code>
config:
  endpointURL: <a href="#endpoint-url">string</a>
  region: <a href="#region">string</a>
  accessKeyID: <a href="#access-key-id">string</a>
  secretAccessKey: <a href="#secret-access-key">string</a>
  sessionToken: <a href="#session-token">string</a>
  useSSL: <a href="#use-ssl">string</a>
</code></pre>

### Endpoint URL

Connect to S3 server at this fully-qualified URL if specified

### Region

Region S3 server is running in if specified

### Access Key ID

Access Key ID used to authenticate

### Secret Access Key

Secret Access Key used to authenticate

### Session Token

Optional session token for authenticating to S3

### Use SSL

Use SSL when connecting to S3. Defaults to `true`

## Actions

<pre><code>
type: <a href="#supported-action-types">string</a>
params:
  path: <a href="#path">string</a>
  contents: <a href="#contents">string</a>
  sourcePath: <a href="#source-path">string</a>
  destinationPath: <a href="#destination-path">string</a>
  bucketName: <a href="#bucket-name">string</a>
  recursive: <a href="#recursive">string</a>
</code></pre>

Returns

<pre><code>
{
    contents: <a href="#contents">string</a>
    exists: <a href="#exists">string</a>
    runtime: <a href="#runtime">int</a>
}
</code></pre>

### Supported Action Types

* write: Write a string to a file in S3
* read: Read file contents to a string in S3
* exists: Check whether a path in S3 is valid
* put: Upload file to S3
* get: Download file from S3
* rm: Delete files from S3
* cb: Create S3 bucket
* rb: Delete S3 bucket

### Path

Path to item in S3. Used in `read`, `write`, `exists` and `rm`

### Contents

File contents to upload to S3. Used in `write`

### Source Path

Path to downstream file in `put` and `get`

### Destination Path

Path to upstream file in `put` and `get`

### Bucket Name

Name of bucket in `cb` and `rb`

### Recursive

Flag to specify uploading or downloading entire folder in `put` or `get`. Also
used to delete objects recursively under folder in `rm`

### Contents

String of file contents if using `get`

### Exists

Whether or not the file at the remote paths exists if using `exists`

### Runtime

Time in milliseconds to complete action

## Asserts

<pre><code>
type: <a href="#supported-assert-types">string</a>
params:
  expected: <a href="#expected">Union[bool, string]</a>
  path: <a href="#path">string</a>
  actionParams: <a href="#actions">ActionParams</a>
</code></pre>

### Supported Assert Types

* Exists: Check if file exists at path
* ContentsEqual: Check if contents of file equal expected string
* ContentsMatch: Check if contents of file match expected regex
* FilesEqual: Check if remote file is equal to expected file

### Expected

Has the following contexts depending on assert type used:

* Exists: True or false, whether or not the file should exist
* ContentsEqual: String file contents should equal
* ContentsMatch: Regex string file contents should match
* FilesEqual: Path to file in runner container that should equal remote file

### Path

Path to remote file doing assert on

### Action params

Overrides earlier params to make assert with

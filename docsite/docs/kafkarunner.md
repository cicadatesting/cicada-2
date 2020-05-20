---
id: kafka-runner
title: Kafka Runner
sidebar_label: Kafka Runner
---

The Kafka runner is able to send and receive messages from a Kafka broker

## Config

<pre><code>
config:
  servers: <a href="#servers">string</a>
  keyEncoding: <a href="#key-encoding">string</a>
  valueEncoding: <a href="#value-encoding">string</a>
  securityProtocol: <a href="#security-protocol">string</a>
  saslMechanism: <a href="#sasl-mechanism">string</a>
  saslUsername: <a href="#sasl-username">string</a>
  saslPassword: <a href="#sasl-password">string</a>
  saslKerberosServiceName: <a href="#sasl-kerberos-service-name">string</a>
  saslKerberosDomainName <a href="#sasl-kerberos-domain-name">string</a>
  saslOauthTokenProvider: <a href="#sasl-oauth-token-provider">string</a>
</code></pre>

### Servers

`,` seperated list of Kafka servers to connect to

### Key Encoding

How to convert message keys between strings and bytes. Defaults to `utf-8`

### Value Encoding

How to convert message values between strings and bytes. Defaults to `utf-8`

### Security Protocol

Security protocol to use when communicating with brokers. Defaults to
`PLAINTEXT`. Valid values are `PLAINTEXT`, `SSL`, `SASL_PLAINTEXT`, `SASL_SSL`

At the moment, not all SSL options are supported

### SASL Mechanism

Authentication mechanism when securityProtocol is `SASL_PLAINTEXT`
or `SASL_SSL`. Defaults to `None`. Valid values are: `PLAIN`, `GSSAPI`,
`OAUTHBEARER`, `SCRAM-SHA-256`, `SCRAM-SHA-512`

### SASL Username

Username must be specified when saslMechanism is `PLAIN` or `SCRAM`

### SASL Password

Password must be specified when saslMechanism is `PLAIN` or `SCRAM`

### SASL Kerberos Service Name

Service name to include in GSSAPI SASL mechanism handshake. Defaults to `kafka`

### SASL Kerberos Domain Name

Kerberos domain name to use in GSSAPI SASL mechanism handshake. Chooses one
of the brokers randomly by default

### SASL OAuth Token Provider

Connect to OAuth token provider if specified

## Actions

<pre><code>
type: <a href="#supported-action-types">string</a>
params:
  topic: <a href="#topic">string</a>
  timeout_ms: <a href="#timeout-ms">int</a>
  max_records: <a href="#max-records">int</a>
  key: <a href="#key">string</a>
  messages: [
    topic: <a href="#topic">string</a>
    key: <a href="#key">string</a>
    value: <a href="#value">string</a>
  ]
  offset: <a href="#offset">string</a>
</code></pre>

Returns

<pre><code>
{
    messages_sent: <a href="#max-records">int</a>
    messages_received: [
      topic: <a href="#topic">string</a>
      key: <a href="#key">string</a>
      value: <a href="#value">string</a>
    ]
    errors: <a href="#errors">[string]</a>
    runtime: <a href="#runtime">int</a>
}
</code></pre>

### Supported Action Types

* Send
* Receive

### Topic

Kafka message topic to send all messages in list to or for a single message

### Timeout MS

Time in milliseconds to wait for messages to receive

### Max Records

Max number of messages to receive in a single poll

### Key

Key to assign to all messages sent or single message

### Value

Value to provide to a single message

### Offset

Where to begin polling the stream. Defaults to `earliest`. Valid values are
`earliest` and `latest`.

### Messages Sent

Number of messages sent

### Messages Received

List of messages received

### Errors

List of errors raised when sending messages

### Runtime

Time in milliseconds to complete action

## Asserts

<pre><code>
type: <a href="#supported-assert-types">string</a>
params:
  actionParams: <a href="#actions">ActionParams</a>
  expected:
    topic: <a href="#topic">string</a>
    key: <a href="#key">string</a>
    value: <a href="#value">string</a>
</code></pre>

### Supported Assert Types

* FindMessage

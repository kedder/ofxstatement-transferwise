# Transferwise plugin for ofxstatement

This plugins is able to parse CSV statements from
[transferwise.com](https://transferwise.com/). Note, that only "accounting"
type of statement is supported.

## Configuration

Configuration can be edited with `ofxstatement edit-config` command. These
configuration parameters are understood by this plugin:


| name       | required? | Description               |
|------------|-----------|---------------------------|
| `account`  | optional  | Name for this account     |
| `currency` | required  | Currency for this account |

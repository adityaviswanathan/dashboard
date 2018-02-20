## Motivation

The `formula_engine` is intended to bridge human-readable formula expressions
and the raw data in the report extracted via `report_utils`. This layer defines
and ultimately expects well-formed formula expression strings as input to
compute on a particular report.

### Parsing the expression (`ParseTree`, `ParseTreeNode`):

Input strings are read into a `ParseTree` which can then be recursively
evaluated based on the definitions of the function nodes in the tree.

In the case of functions that exercise a particular report, ParseTree requires a
reference to an instance of ReportTraverser in order to correctly process nodes
that pertain to report data.

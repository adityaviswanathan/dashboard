# Fiscal report ETL (extract, transform, load)

Fiscal reports are often exported from a variety of collection tools into other
systems for different kinds of reporting or analysis. At a high level, fiscal
reports are a 2D matrix with respect to time (dates) on one axis and line item
titles on the other. Due to this somewhat predictable structure, some degree of
automation around standardizing data extraction from exports is possible. This
ETL tool attempts the following:

- Converts reports to a common CSV format
- Identifies which axis corresponds to dates and which corresponds to titles
- Identifies the starting indexes for the aforementioned axes
- Loads data into a data structure that is navigable for custom analysis

This tool attempts to extract a fiscal report into a navigable `ReportTraverser`
data structure, which enables straightforward access to raw data from the
report. As of now, `ReportTraverser` supports the following query formats:

- Tuple index lookup (e.g. "cell at x,y")
- Date names lookup (e.g. "all date headers")
- Title names lookup (e.g. "all title headers")
- Date filter lookup (e.g. "all cells where date is 'January 2017'")
- Title filter lookup (e.g. "all cells where title is 'rent payment'")

While `report_utils/ReportTraverser` is concerned with the correct extraction of
data from reports, `formula_engine/ParseTree` is concerned with the construction
of functional expressions over extracted data. Both tools will come together to
define analytical formulas over the semantics of specific reports.

## Prerequisites:

- Python 2.7
- `pip` package manager for Python

Install prerequisites via included `requirements.txt`:

```
$ pip install -r requirements.txt
```

## Run tests:

Most of the effort has gone into developing utils for decomposing reports so
the test coverage is mostly around the integrity of these tools against a set
of developer-blessed 'goldens' file, which is the expected output of some util
against a particular file. If input files are changed or added to, goldens can
be refreshed:
```
$ python report_utils/test_report_utils.py --goldens='<DIR_TO_FILES>'
```
This will update or emit a new file `<UTIL_NAME>_goldens.txt` into the folder
containing the sources files. After refreshing, the goldens file should be
blessed by the developer to ensure output is sane.
```
$ python report_utils/test_report_utils.py
```
Tests for `formula_engine` van by run via:
```
$ python formula_engine/test_formula_engine.py
```

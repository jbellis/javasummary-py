# JavaSummary
This is a Python script that uses ANTLR to recursively parse a Java package and generate a summary of the classes, fields, and methods found. The summary is printed to stdout.

This is an experiment to give LLMs a complete overview while being concise enough to fit in its context window.

Java grammar from https://github.com/antlr/grammars-v4/tree/master/java/java

## Setup

`pip install -r requirements.txt`

## Usage
`python java_summary_antlr.py [--methods-only] path-to-java-package`

## Sample Output

```
# Package org.apache.cassandra.index
Class SecondaryIndexBuilder extends CompactionInfo.Holder:

Class SecondaryIndexManager implements IndexRegistry,INotificationConsumer:
  Class WriteTimeTransaction implements UpdateTransaction:
    Methods:
      SecondaryIndexManager(ColumnFamilyStore baseCfs)
      void buildIndexesBlocking(Collection<SSTableReader> sstables, Set<Index> indexes, boolean isFullRebuild)
      WriteTimeTransaction()
      void onUpdated(Row existing, Row updated)
...
```

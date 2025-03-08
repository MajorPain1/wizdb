# wizdb

Builds an SQLite database of items directly from game files.

## Usage
Install Katsuba through PyPi
```
pip install katsuba
```

Head over to the [wiztype repository](https://github.com/wizspoil/wiztype)
and follow README instructions to dump a types JSON from the game client.

Then execute the following commands:

```
# Clone this repository to wizdb/
git clone https://github.com/MajorPain1/wizdb
cd wizdb

...
# Copy the game's Root.wad file to wizdb/Root.wad

# Find a copy of mobdeckbehaviortypes.json from the WizSpoil discord and copy to wizdb/mobdeckbehaviortypes.json

# Copy previously dumped wiztype file to wizdb/types.json
...

# Now build the db
python -m wizdb

# You will see the database file wizdb/items.db on success.
```

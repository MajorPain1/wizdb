# wizdb

Builds an SQLite database of items directly from game files.

## Usage

Head over to the [kobold repository](https://github.com/vbe0201/kobold)
and follow installation instructions in the README. Also do the
optional steps to install Python library bindings.

Then, head over to the [wiztype repository](https://github.com/wizspoil/wiztype)
and follow README instructions to dump a types JSON from the game client.

Then execute the following commands:

```
# Clone this repository to wizdb/
git clone https://github.com/MajorPain1/wizdb
cd wizdb

# Copy the game's Root.wad file to wizdb/Root.wad
...

# Use the previous kobold installation to extract it to wizdb/Root/
kobold wad unpack Root.wad

# Copy previously dumped wiztype file to wizdb/types.json
...

# Now build the db
python -m wizdb

# You will see the database file wizdb/items.db on success.
```

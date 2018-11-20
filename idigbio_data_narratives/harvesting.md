# = DRAFT =

iDigBio Data Harvesting and Ingestion
=====================================


Data Mobilization and Data Publishing
-------------------------------------

Specimen-based Occurrence data is used to record the location and time of a collecting event.

Data Mobilization is the process of freeing data from inaccessible, closed, or proprietary data systems and into a form where the data is shared with the rest of the scientific community.  Mobilization should not be thought of as a one-time process, but a cycle that runs continuously in order to bring new and updated data to the public.

Data Publishing is the step of Mobilization by which a dataset is shared on the Internet for other people to use. In the context of specimen-based occurrence data, a "dataset" is a collection of records about specimens or related digital objects that are typically bundled into a Darwin Core Archive.

See external material for more information on Darwin Core Archives.
http://tools.gbif.org/dwca-assistant/

Data Publishers, or "Publishers" for short, are the servers / http locations on the Internet that provide the links to datasets and metadata.

The route for a dataset to become part of iDigBio begins with our mobilization staff who will handle the initial conversations with a data provider.  iDigBio staff inspect a particular dataset to see if it is ready to be included in the iDigBio aggregated data.  Data records much meet some miminum requirements before they will be considered for inclusion.  For example, datasets whose occurrence identifiers are unsuitable in a global context are not likely to be included in iDigBio aggregation.  iDigBio is focused on specimen-based occurrence records, so observations are also generally out-of-scope and would not be included in the aggregate.

Every occurrence record needs to have a distinct and persistent globally unique identifier if these occurrences are to be aggregated for searching and research purposes.

Any globally unique persistent identifier makes for an acceptable occurrenceID.  We recommended https://github.com/tdwg/guid-as "TDWG Globally Unique Identifiers (GUID) applicability statement" as a canonical reference.  All of the following are valid idenitifer types for occurrences:

* UUID - Universally Unique Identifier aka GUID
* LSID - Life Science Identifier
* HTTP URI - a subset of Uniform Resource Identifier (URI)
* DOI - Digital Object Identifier
* PURL - Permanent URL
* Handle - Handle System

Each potential identifier choice has a set of tradeoffs associated with it. iDigBio recommends UUID v4 identifiers because they are locally mintable (no cost, no external service dependency, and no external organizational dependency). Despite rumors to the contrary, UUIDs are globally unique even when minted locally.  They are true opaque identifiers with all of the benefits thereof, and have no external pressure that discourages permanance (HTTP URIs are particularly susceptible to change). GBIF's publication "A Beginner’s Guide to Persistent Identifiers" https://www.gbif.org/document/80575/a-beginners-guide-to-persistent-identifiers is an excellent reference.


At the time of this writing, iDigBio aggregates over 100 million specimen records from over 1500 datasets provided by 77 publishers.

To accomplish this, iDigBio leverages existing data publishing tools, metadata tracking, and automation.


Data Publishing Feeds (e.g. RSS)
--------------------------------

RSS (Really Simple Syndication) is a technology originally developed for publishing news items.  This technology has been adapted to function as a notification mechanism for newly published datasets (rather than newly published news stories).  iDigBio currently supports both RSS 2.0 and Atom 1.0 but generically we tend to call them "RSS feeds" regardless of the specific underlying technology being used.  The purpose of a feed in the data publishing workflow is to allow subscribers to become aware when new datasets and new versions of existing datasets become available. By simply looking at the publishing date in the feed, consumers avoid having to download a file over and over and do diff comparisons to see if anything has changed.  Maintaining a publication date as a metadata item is also more robust than trying to rely on file modification timestamps or web content headers.

iDigBio's requirements for a usable data publishing feed must include all of the following pieces of information for each dataset:

1. guid for the dataset feed entry (feed url + unique item identifier is sufficient)
2. link to the Darwin Core Archive dataset file which contains the actual occurrence records and any DwC extensions
3. link to the EML file which contains metadata about the dataset contents and the source collection
4. publication date for the most recent date of the dataset update

Additional technical specifications are available in the iDigBio wiki:

https://www.idigbio.org/wiki/index.php/CYWG_iDigBio_DwC-A_Pull_Ingestion

GBIF IPT and Symbiota are two examples of software that have RSS publishing built-in. These data publishing features are advantageous towards sharing collections data with the biocollections community.

The preferred Data Publishing process would include frequent re-publish events to capture ongoing changes to the source collection database.

Data Mobilization and Data Publishing are processes that operate inside of a biocollection, a collection's IT systems, or immediate upstream service providers.

Harvesting
----------

Harvesting is the process by which an aggregator retrieves datasets from the Internet that have been Mobilized and Published.

iDigBio maintains an internal list of available specimen-based occurrence datasets and an ingest flag to indicate whether we wish to include them or not.

Code:
https://github.com/iDigBio/idb-backend/blob/master/idigbio_ingestion/update_publisher_recordset.py

The iDigBio dataset harvesting process:

1. Scan all of the known Publisher RSS feeds for new or updated datasets (inspect the pubdate field for each item in each RSS feed)
2. For each dataset in iDigBio's ingestion list, check to see if the currently-published dataset is newer than the copy that iDigBio already has in storage. Download any newer datasets into iDigBio stroage.

This basic process is currently scheduled to occur every hour.  In our experience Publishers are offline from time to time for maintenance or other reasons.  By continuously checking for new datasets and fetching them as they become available, we eliminate the impact of server downtime on the provider end of things.  At any given time, roughly 10% of known data publishers are offline, so running the harvesting process semi-continuously increases the chances of harvesting success over time.

After harvesting is completed, iDigBio has a copy of all the recently-published Darwin Core Archives across the community that we have marked for Ingestion. At this point the records themselves are not yet extracted or processed in any way.

Data Ingestion
--------------

iDigBio processes the harvested datasets roughly every two weeks, depending on how much mobilization activity has been taking place during the proceeding weeks and how much other project work is required by iDigBio staff. Data Ingestion is what we call the process of converting harvested datasets into individual data record objects.

Code:
https://github.com/iDigBio/idb-backend/blob/master/idigbio_ingestion/db_check.py

The iDigBio Data Ingestion process:

1. For each dataset, extract the contents.
2. Read the data files and accompanying schema (meta.xml)
3. For each record, insert, update, or mark as deleted in the database

At the completion of the iDigBio Ingestion process we have JSON-structured represenations of each data record as well as the relationships between records (such as media that are associated to specimens) stored in a PostgreSQL database.

# = DRAFT =


iDigBio has attempted to maintain a distinction between the occurrenceID contained in a record and the recordID itself.  Unfortunately, Darwin Core itself does not contain a recordID concept and one of the more common data publishing software, GBIF IPT, does not have a recordID concept either.  This means that across much of the community there is no way to distinguish between the identifier of the digital record about an object and the identifier of the object itself. iDigBio currently tracks recordIDs when present (for example, Symbiota data publishing includes recordID with each record) and prevents duplicates of digital records from Symbiota from appearing in iDigBio.  In most cases if there is a duplicated occurrenceID in iDigBio, it occurs when the occurrenceID is not actually globally unique. iDigBio does contain some duplicate records when the same information is published from multiple publishers and the records do not have consistent identifiers between the datasets.


Once Ingestion is completed, the data are sitting in the iDigBio PostgreSQL server ready to be indexed. The iDigBio indexing process makes the data available in public-facing search services and the specimen portal, aiding in the discoverability of specimen records... but that is a topic for another post.

The iDigBio model of harvesting, ingestion, and indexing allows iDigBio to receive thousands of record updates every few weeks with very little hands-on work by iDigBio staff.  By removing most of the overhead of receving "updates" from existing data providers, iDigBio staff can continue to concentrate on new datasets yet to be mobilized.

# = DRAFT =

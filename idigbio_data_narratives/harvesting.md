=DRAFT=

iDigBio Data Harvesting and Ingestion
=====================================


Data Mobilization and Data Publishing
-------------------------------------

Data Mobilization is the process of getting data out of closed or proprietary backend systems and into a form where the data can be shared with other people.  Mobilization should not be though of as a one-time process, but a cycle that runs continuously in order to bring new and updated data to the public.


Data Publishing is the step of Mobilization by which a dataset is shared on the Internet for other people to use. In the context of specimen-based occurrence data, a "dataset" is a collection of specimen records or other related metadata about specimens that are typically bundled into a Darwin Core Archive.

See external materials for more information on Darwin Core Archives.

The approach is most valuable...

Data Publishing Providers, or "Publishers" for short, are the servers / http locations on the Internet that provide the links to datasets and metadata.

At the time of this writing, iDigBio aggregates over 100 million specimen records from over 1500 datasets provided by 77 publishers.

To accomplish this task, iDigBio maintains an internal list of available specimen-based occurrence datasets and an ingest flag to indicate whether we wish to include them or not.


The route for a dataset to get added to the aggregate in iDigBio begins with our mobilization staff who will handle the initial conversations with a data provider.  iDigBio staff inspect a particular dataset to see if it is ready to be included in the iDigBio aggregated data.  For example, datasets that are missing occurrence identifiers or where those occurrence identifiers are unsuitable in a global context are not likely to be included in iDigBio aggregation.  iDigBio's focus is specimen-based occurrence records, so observations are also generally out-of-scope and are not selected to become part of the aggregate.


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

Data Mobilization and Data Publishing are processes that operate inside of a biocollection, its IT systems, or immediate upstream service providers.

Harvesting
----------

Harvesting is the process by which an aggregator retrieves datasets from the Internet that have been Mobilized and Published.

The iDigBio dataset harvesting process:

1. Scan all of the known Publisher RSS feeds for new or updated datasets (inspect the pubdate field for each item in each RSS feed)
2. For each currently-publisehd dataset that is newer than the copy that iDigBio already has in storage, the newer dataset is downloaded and saved into iDigBio stroage.

This basic process is currently scheduled to occur every hour.  In our experience Publishers are offline from time to time for maintenance or other reasons.  By continuously checking for new datasets and fetching them as they become available, we eliminate the impact of server downtime on the provider end of things.  At any given time, roughly 10% of known data publishers are offline.

After harvesting is completed, iDigBio has a copy of all the recently-published Darwin Core Archives across the community that we have marked for Ingestion. At this point the records themselves are not yet extracted or processed in any way.

Data Ingestion
--------------

iDigBio processes the harvested datasets roughly every two weeks, depending on how much mobilization activity has been taking place during the proceeding weeks.  We call this processing Data Ingestion.

The iDigBio Data Ingestion process:

1. For each dataset, extract the contents.
2. Read the data files and accompanying schema (meta.xml)
3. Construct a unique recordID based on the dataset
3. Using the unique identifier contained in each record and the hashed content of each record, compare to the existing data and determine if a record is New, Updated, or Deleted
3. 
4.
5.

At the completion of the iDigBio Ingestion process we have JSON-structured represenation of each data record as well as the relationships between records (such as media that are associated to specimens) stored in a PostgreSQL database.




=DRAFT=



something about recordIDs

A specimen Occurrence is a collecting event at a specific place and time.  Every occurrence needs to have a distinct globally unique identifier and persistent if these occurrences are to be aggregated for searching and research purposes.  The occurrenceID.

iDigBio has attempted to maintain a distinction between the occurrenceID contained in a record and the recordID itself.  Unfortunately, Darwin Core itself does not contain a recordID concept and one of the more common data publishing software, GBIF IPT, does not have a recordID concept either.  This means that across much of the community there is no way to distinguish between the identifier of the digital record about an object and the identifier of the object itself. This also means it is not currently possible to merge two distinct sources of data about a single occurrence.  iDigBio currently tracks recordIDs when present (for example, Symbiota data publishing includes recordID with each record) and prevents duplicates of digital records from appearing in iDigBio.  iDigBio allows multiple instances of an occurrenceID into the aggregate.  iDigBio does not currently attempt to "merge" multiple instances of an occurrenceID together. In most cases, duplicated occurrenceIDs occur when the occurrenceID is not actually globally unique. iDigBio does contain some duplicate records when the same information is published from multiple publishers and the records do not have consistent identifiers between the datasets.


Once Ingestion is completed, the data are sitting in the iDigBio PostgreSQL server ready to be indexed. The iDigBio indexing process makes the data available in our public-facing search services and specimen portal... but that is a topic for another post.

=DRAFT=

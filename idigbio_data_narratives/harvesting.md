=DRAFT=

iDigBio Data Harvesting and Ingestion
=====================================

Data Publishing is the act of putting a dataset on the Internet for other people to use. In the context of specimen occurrence data, a "dataset" is a collection of specimen records or other related metadata about specimens that are typically bundled into a Darwin Core Archive.

See external materials for more information on Darwin Core Archives.


Data Publishing Providers, or "Publishers" for short, are the servers / http locations on the Internet that provide the links to datasets and metadata.

At the time of this writing, iDigBio aggregates over 100 million specimen records from over 1500 datasets provided by 77 publishers.

To accomplish this task, iDigBio maintains an internal list of available specimen-based occurrence datasets and an ingest flag to indicate whether we wish to include them or not.


The route for a dataset to get added to the aggregate in iDigBio begins with our mobilization staff who will handle the initial conversations with a data provider.  iDigBio staff inspect a particular dataset to see if it is ready to be included in the iDigBio aggregated data.  For example, datasets that are missing occurrence identifiers or where those occurrence identifiers are unsuitable in a global context are not likely to be included in iDigBio aggregation.  iDigBio's focus is specimen-based occurrence records, so observations are also generally out-of-scope and are not selected to become part of the aggregate.


Data Publishing Feeds (e.g. RSS)
================================

RSS (Really Simple Syndication) is a technology originally developed for publishing news items.  iDigBio currently supports both RSS 2.0 and Atom 1.0 but generically we tend to call them "RSS feeds" regardless of the specific underlying technology being used.  The purpose of a feed in the data publishing workflow is to allow subscribers to become aware when new datasets and new versions of existing datasets become available. By simply looking at the publishing date in the feed, consumers avoid having to download a file over and over and do diff comparisons to see if anything has changed.  Maintaining a publication date as a metadata item is also more robust than trying to rely on file modification timestamps or web content headers.

iDigBio's requirements for a usable data publishing feed must include all of the following pieces of information for each dataset:

1. guid for the dataset feed entry (feed url + unique item identifier is sufficient)
2. link to the Darwin Core Archive dataset file which contains the actual occurrence records and any DwC extensions
3. link to the EML file which contains metadata about the dataset contents and the source collection
4. publication date for the most recent date of the dataset update

Additional technical specifications are available in the iDigBio wiki:

https://www.idigbio.org/wiki/index.php/CYWG_iDigBio_DwC-A_Pull_Ingestion

GBIF IPT and Symbiota are two examples of software that have RSS publishing built-in. These data publishing features are advantageous towards sharing collections data with the biocollections community.


Harvesting
==========

The iDigBio dataset harvesting process:

1. Scan all of the known Publisher RSS feeds for new or updated datasets (inspect the pubdate field for each item in each RSS feed)
2. For each currently-publisehd dataset that is newer than the copy that iDigBio already has in storage, the newer dataset is downloaded and saved into iDigBio stroage.

This basic process is currently scheduled to occur every hour.  In our experience Publishers are offline from time to time for maintenance or other reasons.  By continuously checking for new datasets and fetching them as they become available, we eliminate the impact of server downtime on the provider end of things.  At any given time, roughly 10% of known data publishers are offline.

After harvesting is completed, iDigBio has a copy of all the recently-published Darwin Core Archives across the community that we have elected for Ingestion.

Ingestion
=========

iDigBio processes the harvested datasets roughly every two weeks....


=DRAFT=



something about recordIDs

occurrenceID is a 

iDigBio has attempted to maintain a distinction between the occurrenceID in a record and the recordID itself.  This would allow multiple facts about the same occurrence to be presented in multiple datasets.  Unfortunately, Darwin Core itself does not contain a recordID concept and one of the more common data publishing software IPT does not have a recordID concept either.


Once Ingestion is completed, the data are sitting in the iDigBio PostgreSQL server ready to be indexed. The iDigBio indexing process makes the data available in our public-facing search services and specimen portal... but that is a topic for another post.

=DRAFT=

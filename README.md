# OpenSpending-Next API

[![Build Status](https://travis-ci.org/openspending/os-api.svg?branch=master)](https://travis-ci.org/openspending/os-api)
[![Coverage Status](https://coveralls.io/repos/openspending/os-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/openspending/os-api?branch=master)

This module contains the code for the API of the new OpenSpending (aka OpenSpending-Next). 
 
### Installation

To get started:

```
$ git clone https://github.com/openspending/os-api.git
$ cd os-api
$ export OS_API_ENGINE=sqlite:///`pwd`/osapi.db
$ celery -A babbage_fiscal.tasks worker &
$ python dev_server.py
```

### API interface

This module provides the following APIs 

 - An OLAP-style API for querying the fiscal data (based on the blueprint provided by [babbage](https://github.com/openspending/babbage)  
 - A backward compatibility layer providing an API compatible to the `aggeregate` API, as described in the [OS documentation](http://community.openspending.org/help/aggregate/)
 - A metadata API providing information regarding different packages
 
### API call reference

 - `/api/3/info/<dataset>/package`
    
   Returns the Fiscal Data-Pacakge for this dataset

 - `/api/3/cubes`
 
   Returns a list of the available datasets in the store
   
 - `/api/3/cubes/<dataset>/model`
 
   Returns the `babbage` model for the dataset. This is the model which is used  when querying the data.
   
 - `/api/3/cubes/<dataset>/facts`
 
   Returns individual entries from the dataset in non-aggregated form.
   
   Parameters:
   - `cut` - filters on the data (`field_name:value`, `field_name:value|field_name:value` etc.) 
   - `fields` - fields to return
   - `order` - data ordering (e.g. `field_name:desc`)
   - `pagesize` - number of entries in one batch of returned data
   - `page` - page selection
   
 - `/api/3/cubes/<dataset>/members/<dimension>`
 
   Returns the distinct set of values for a specific dimension.
   
   Parameters: `cut`, `order`, `page` and `pagesize` as above
   
 - `/api/3/cubes/<dataset>/aggregate`
 
   Returns an aggregate of the data in the specified dataset.
   
   Parameters: 
   - `cut`, `order`, `page` and `pagesize` as above
   - `drilldown` - group by these dimensions (e.g. `field_name_1|field_name_2`)
   - `aggregates` - which measures to aggregate (and what function to perform (e.g. `amount.sum`, `count`)
   
 - `/api/2/aggregate`    
  
   A backwards compatible version of the aggregate API.
  
   Parameters:
   - `dataset` - dataset to query
   - `cut` - filters on the data
   - `drilldown` - fields to group by the results
   - `page` and `page_size` - as above
   - `order` - same as `sort`, above
   - `measure` - measure to aggregate
  
   
   


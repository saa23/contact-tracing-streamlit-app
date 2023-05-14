# Contact Tracing Streamlit App
## Table of Contents
- [Dataset](#dataset)
- [Project Flow](#project-flow)
- [Streamlit App](#streamlit-app)

## Dataset
The location dataset to represent contact tracing refer to [SF Registered Business Locations - San Francisco](https://www.kaggle.com/datasets/san-francisco/sf-registered-business-locations-san-francisco).
The dataset consists of 250,245 records. While the columns as following:
1. Location Id
2. Business Account Number
3. Ownership Name
4. DBA Name
5. Street Address
6. City
7. State
8. Source Zipcode
9. Business Start Date
10. Business End Date
11. Location Start Date
12. Location End Date
13. Mail Address
14. Mail City
15. Mail Zipcode
16. Mail State
17. NAICS Code
18. NAICS Code Description
19. Parking Tax
20. Transient Occupancy Tax
21. LIC Code
22. LIC Code Description
23. Supervisor District
24. Neighborhoods - Analysis Boundaries
25. Business Corridor
26. Business Location

But the important columns that needed in the project are:
1. Location ID &emsp; $\rightarrow$ &emsp; Location Identification Number. Each DBA has a unique LIN for location specific tax filings
2. DBA Name &emsp; $\rightarrow$ &emsp; Doing Business As Name or Location Name (Business name)
3. Street Address &emsp; $\rightarrow$ &emsp; Business location street address
4. City &emsp; $\rightarrow$ &emsp; Business location city
5. Source Zipcode &emsp; $\rightarrow$ &emsp; Business location zip code
6. Business Location &emsp; $\rightarrow$ &emsp; The latitude and longitude of the business location for mapping purposes.

## Requirements
- The project use python 3.8 (but it might be ok to  use later version).
- Whereas the python library needed, please kindly check the [requirements.txt](./requirements.txt)
- Other than that, it is mandatory to install docker.


## Project Flow
- download the dataset
- transform the data using script 
 After that, create a docker compose to build image for service Elasticsearch and Kibana.
 
**(need update later)**

## Streamlit App
 Here are some functionality in the contact tracing streamlit app:
### 1. Search by Free Text

### 2. Search by Zip Code

### 3. Search by Business ID

### 4. Search by Device ID
